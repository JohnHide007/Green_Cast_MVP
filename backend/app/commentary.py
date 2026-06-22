"""
AI commentary layer — calls Claude to produce attributed sentences about a
company's risk profile. Falls back gracefully when ANTHROPIC_API_KEY is absent.
"""

import json
import os
from typing import Optional

from app.models import CommentarySentence, CommentaryResponse, RiskAlert, RiskFactor

_CLIENT: Optional[object] = None


def _get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        _CLIENT = anthropic.Anthropic(api_key=api_key)
        return _CLIENT
    except Exception:
        return None


def _build_prompt(
    company_name: str,
    sector: str,
    factors: list[RiskFactor],
    alerts: list[RiskAlert],
) -> str:
    factor_lines = "\n".join(
        f"  - {f.factor_type}: {f.normalized_value:.1f}/100 (weight {round(f.weight * 100)}%)"
        for f in factors
    )
    alert_lines = "\n".join(
        f"  - [{a.rule_name}] {a.category} ({a.severity}): {a.description}"
        for a in alerts
    ) or "  (none)"

    return f"""You are a risk analyst at a private markets fund manager. Write a concise 4–6 sentence commentary on the following portfolio company's risk profile. Each sentence MUST end with its source references in brackets using the exact factor_type or rule_name identifiers provided below — e.g. [CARBON_INTENSITY_HIGH] or [OVERALL_RISK_SCORE].

Company: {company_name}
Sector: {sector}

Risk Factors (computed, 0–100 scale, higher = worse):
{factor_lines}

Active Risk Alerts (deterministic rule engine):
{alert_lines}

Rules:
1. Write in Bloomberg/McKinsey style — factual, forward-looking, professional.
2. Do NOT fabricate numbers. Only cite the values shown above.
3. Each sentence must cite at least one [FACTOR_TYPE] or [RULE_NAME] at the end.
4. Return valid JSON only, as an array of objects: [{{"sentence": "...", "source_refs": ["REF1", "REF2"]}}]
5. No markdown, no preamble, just the JSON array.
"""


def generate_commentary(
    company_id: int,
    company_name: str,
    sector: str,
    factors: list[RiskFactor],
    alerts: list[RiskAlert],
) -> CommentaryResponse:
    client = _get_client()
    if client is None:
        return CommentaryResponse(
            available=False,
            company_id=company_id,
            sentences=[],
            message="Commentary unavailable — ANTHROPIC_API_KEY not configured.",
        )

    try:
        prompt = _build_prompt(company_name, sector, factors, alerts)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        sentences = [CommentarySentence(**item) for item in data]
        return CommentaryResponse(
            available=True,
            company_id=company_id,
            sentences=sentences,
        )
    except Exception as exc:
        return CommentaryResponse(
            available=False,
            company_id=company_id,
            sentences=[],
            message=f"Commentary generation failed: {exc}",
        )
