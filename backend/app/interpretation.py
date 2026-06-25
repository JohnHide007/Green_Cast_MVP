"""
AI Risk Interpretation engine (Module 4).

Where commentary (Module 5) writes prose, this layer synthesises the internal
risk factors, fired alerts, and external macro/regulatory signals into a
structured, forward-looking risk thesis: the top risks, their severity, and the
rationale — each tied back to the source factor/rule/signal id.

Routes through the Vercel AI Gateway. Degrades gracefully without a key.
"""

from app import ai_gateway
from app.models import (
    InterpretedRisk,
    MacroSignal,
    RiskAlert,
    RiskFactor,
    RiskInterpretationResponse,
)

_SYSTEM = (
    "You are a senior portfolio risk officer at a European private-markets fund. "
    "You combine internal financial/ESG signals with external macro and regulatory "
    "developments into a concise, forward-looking risk interpretation. You only use "
    "the evidence provided and attribute every risk to its source id."
)


def _build_prompt(
    company_name: str,
    sector: str,
    factors: list[RiskFactor],
    alerts: list[RiskAlert],
    signals: list[MacroSignal],
) -> str:
    factor_lines = "\n".join(
        f"  - {f.factor_type}: {f.normalized_value:.1f}/100 (weight {round(f.weight * 100)}%)"
        for f in factors
    ) or "  (none)"
    alert_lines = "\n".join(
        f"  - [{a.rule_name}] {a.category} ({a.severity}): {a.description}"
        for a in alerts
    ) or "  (none)"
    signal_lines = "\n".join(
        f"  - [{s.signal_type}] level={s.level} value={s.value:.2f}: {s.description}"
        for s in signals
    ) or "  (none)"

    return f"""Synthesise a forward-looking risk interpretation for this portfolio company by combining the INTERNAL signals (risk factors, alerts) with the EXTERNAL signals (macro/regulatory).

Company: {company_name}
Sector: {sector}

INTERNAL — Risk Factors (0-100, higher = worse):
{factor_lines}

INTERNAL — Active Alerts:
{alert_lines}

EXTERNAL — Macro / Regulatory Signals:
{signal_lines}

Return valid JSON only with this shape:
{{
  "thesis": "one-paragraph forward-looking risk thesis (3-4 sentences)",
  "key_risks": [
    {{"title": "...", "severity": "high|medium|low", "rationale": "1-2 sentences", "source_refs": ["FACTOR_OR_RULE_OR_SIGNAL_ID"]}}
  ]
}}
Rules: 3-5 key_risks, ordered most severe first. Only cite ids shown above. No markdown, no preamble.
"""


def interpret_risk(
    company_id: int,
    company_name: str,
    sector: str,
    factors: list[RiskFactor],
    alerts: list[RiskAlert],
    signals: list[MacroSignal],
) -> RiskInterpretationResponse:
    if not ai_gateway.is_configured():
        return RiskInterpretationResponse(
            available=False,
            company_id=company_id,
            message="Interpretation unavailable — AI_GATEWAY_API_KEY not configured.",
        )
    try:
        prompt = _build_prompt(company_name, sector, factors, alerts, signals)
        data = ai_gateway.chat_json(prompt, system=_SYSTEM, max_tokens=4096)
        return RiskInterpretationResponse(
            available=True,
            company_id=company_id,
            thesis=data.get("thesis", ""),
            key_risks=[InterpretedRisk(**r) for r in data.get("key_risks", [])],
            model=ai_gateway.get_model(),
        )
    except Exception as exc:
        return RiskInterpretationResponse(
            available=False,
            company_id=company_id,
            message=f"Interpretation failed: {exc}",
        )
