"""
Shared Vercel AI Gateway client.

All AI features (commentary, risk interpretation, AI-assisted normalization)
route through Vercel's native AI Gateway via its OpenAI-compatible endpoint.
This gives one key + one billing/observability surface for any provider, and
lets us swap models (OpenAI / Anthropic / Google) by changing one env var.

Auth:  AI_GATEWAY_API_KEY  (create in Vercel dashboard -> AI Gateway -> API Keys)
Model: AI_MODEL            (default: google/gemini-2.5-flash)

When the key is absent the helpers return None so every caller can degrade
gracefully to its rules-based output instead of erroring.
"""

import json
import os
import re
import time
from typing import Any, Optional

GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
DEFAULT_MODEL = "google/gemini-2.5-flash"

# Retry on rate-limit (429). Free-tier Gemini throttles bursts; a short
# backoff lets back-to-back calls (commentary + interpretation) recover.
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = (1.0, 2.5)  # waits between attempts

_client: Optional[Any] = None


def get_model() -> str:
    return os.environ.get("AI_MODEL", DEFAULT_MODEL)


def is_configured() -> bool:
    """True when an AI Gateway key is present."""
    return bool(os.environ.get("AI_GATEWAY_API_KEY"))


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("AI_GATEWAY_API_KEY", "")
    if not api_key:
        return None
    # Let import/construction errors propagate — callers wrap this in try/except
    # and surface a readable message, rather than silently degrading to None.
    from openai import OpenAI

    _client = OpenAI(api_key=api_key, base_url=GATEWAY_BASE_URL)
    return _client


def _is_rate_limit(exc: Exception) -> bool:
    if getattr(exc, "status_code", None) == 429:
        return True
    name = type(exc).__name__
    text = str(exc)
    return "RateLimit" in name or "429" in text or "rate_limit" in text


def chat(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> Optional[str]:
    """Single-turn completion through the gateway. Returns text, or None if AI is unavailable."""
    client = _get_client()
    if client is None:
        return None
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(_MAX_ATTEMPTS):
        try:
            resp = client.chat.completions.create(
                model=get_model(),
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                # Cap reasoning tokens so "thinking" models (e.g. Gemini 2.5
                # Flash) leave enough budget for the actual JSON output.
                extra_body={"reasoning": {"max_tokens": 1024}},
            )
            return resp.choices[0].message.content
        except Exception as exc:
            if _is_rate_limit(exc) and attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_BACKOFF_SECONDS[attempt])
                continue
            raise


def _extract_json(raw: str) -> str:
    """Pull the JSON payload out of a model reply that may include code fences
    or surrounding prose. Returns the best-effort JSON substring."""
    raw = raw.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    # If there's leading/trailing prose, slice from the first opening bracket to
    # the last matching closing bracket.
    starts = [i for i in (raw.find("["), raw.find("{")) if i != -1]
    if starts:
        start = min(starts)
        end = max(raw.rfind("]"), raw.rfind("}"))
        if end > start:
            raw = raw[start : end + 1]
    return raw.strip()


def chat_json(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> Optional[Any]:
    """Like chat(), but parses the model's reply as JSON. Returns None if AI is
    unavailable; raises ValueError if the model returned unparseable JSON."""
    raw = chat(prompt, system=system, max_tokens=max_tokens, temperature=temperature)
    if raw is None:
        return None
    if not raw.strip():
        raise ValueError("Model returned an empty response (token budget likely exhausted by reasoning).")
    try:
        return json.loads(_extract_json(raw))
    except json.JSONDecodeError as exc:
        snippet = raw.strip()[:200]
        raise ValueError(f"Model did not return valid JSON ({exc}). Got: {snippet!r}") from exc
