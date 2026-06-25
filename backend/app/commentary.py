"""
AI commentary layer (Module 5) — turns the deterministic risk numbers + fired
alerts into investor-ready, attributed sentences. Each sentence cites the
rule/factor it came from, which is what makes the output auditable rather than
a black box.

Runs through the Vercel AI Gateway (see app.ai_gateway). Degrades gracefully to
an "unavailable" response when no AI Gateway key is configured — the rules-based
scores still render without it.
"""

from app import ai_gateway
from app.models import CommentarySentence, CommentaryResponse, RiskAlert, RiskFactor

# Cache successful results per company so re-opening a page (or the refresh
# button) reuses the generated commentary instead of re-calling the model.
_CACHE: dict[int, CommentaryResponse] = {}

_SYSTEM = (
    "You are a risk analyst at a European private-markets fund manager. "
    "You write concise, forward-looking, investor-ready commentary and you "
    "never fabricate numbers."
)


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

    return f"""Write a concise 4-6 sentence commentary on the following portfolio company's risk profile. Each sentence MUST end with its source references in brackets using the exact factor_type or rule_name identifiers provided below — e.g. [CARBON_INTENSITY_HIGH] or [OVERALL_RISK_SCORE].

Company: {company_name}
Sector: {sector}

Risk Factors (computed, 0-100 scale, higher = worse):
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
    if not ai_gateway.is_configured():
        return CommentaryResponse(
            available=False,
            company_id=company_id,
            sentences=[],
            message="Commentary unavailable — AI_GATEWAY_API_KEY not configured.",
        )

    if company_id in _CACHE:
        return _CACHE[company_id]

    try:
        prompt = _build_prompt(company_name, sector, factors, alerts)
        data = ai_gateway.chat_json(prompt, system=_SYSTEM, max_tokens=4096)
        sentences = [CommentarySentence(**item) for item in data]
        response = CommentaryResponse(
            available=True,
            company_id=company_id,
            sentences=sentences,
        )
        _CACHE[company_id] = response
        return response
    except Exception as exc:
        return CommentaryResponse(
            available=False,
            company_id=company_id,
            sentences=[],
            message=f"Commentary generation failed: {exc}",
        )
