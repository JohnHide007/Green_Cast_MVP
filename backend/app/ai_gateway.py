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
from typing import Any, Optional

GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
DEFAULT_MODEL = "google/gemini-2.5-flash"

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
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=api_key, base_url=GATEWAY_BASE_URL)
        return _client
    except Exception:
        return None


def chat(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 1024,
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
    resp = client.chat.completions.create(
        model=get_model(),
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages,
    )
    return resp.choices[0].message.content


def _strip_code_fences(raw: str) -> str:
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers that models often add.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    return fence.group(1).strip() if fence else raw


def chat_json(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Optional[Any]:
    """Like chat(), but parses the model's reply as JSON. Returns None if AI is
    unavailable; raises ValueError if the model returned unparseable JSON."""
    raw = chat(prompt, system=system, max_tokens=max_tokens, temperature=temperature)
    if raw is None:
        return None
    try:
        return json.loads(_strip_code_fences(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model did not return valid JSON: {exc}") from exc
