"""
AI-assisted data normalization / ingestion (Module 1).

Portfolio companies submit financials in inconsistent formats (Exact, SAP, Xero,
Twinfield, Excel exports). Rather than build a bespoke connector per source, the
LLM maps arbitrary input columns to the canonical FinancialRecord schema
(year, quarter, revenue, ebitda, net_debt), returning both the normalized rows
and the inferred field mapping for auditability.

Routes through the Vercel AI Gateway. Degrades gracefully without a key.
"""

import json

from app import ai_gateway
from app.models import (
    NormalizationResponse,
    NormalizedFinancialRow,
)

_SYSTEM = (
    "You are a financial data engineer. You map heterogeneous accounting exports "
    "to a fixed canonical schema. You never invent values: if a target field is "
    "absent in the input, you leave it null."
)

_CANONICAL = "year (int), quarter (int 1-4), revenue (number), ebitda (number), net_debt (number)"


def _build_prompt(rows: list[dict], source_hint: str | None) -> str:
    sample = json.dumps(rows[:20], default=str, indent=2)
    hint = f"\nThe source system is likely: {source_hint}." if source_hint else ""
    return f"""Map these raw financial rows to the canonical schema.{hint}

Canonical fields: {_CANONICAL}
Notes on common source labels: revenue may appear as "turnover", "net sales", "Umsatz", "omzet"; ebitda as "EBITDA", "operating profit"; net_debt as "net debt", "nettoschuld"; amounts may be in thousands ("'000") — convert to absolute units if a scale is indicated.

Raw rows (JSON):
{sample}

Return valid JSON only with this shape:
{{
  "rows": [{{"year": 2023, "quarter": 4, "revenue": 0, "ebitda": 0, "net_debt": 0}}],
  "field_mapping": {{"<source_field>": "<canonical_field>"}},
  "notes": "one sentence on assumptions (scale, currency, dropped columns)"
}}
Use null for any canonical field you cannot fill. No markdown, no preamble.
"""


def normalize_rows(rows: list[dict], source_hint: str | None = None) -> NormalizationResponse:
    if not ai_gateway.is_configured():
        return NormalizationResponse(
            available=False,
            message="Normalization unavailable — AI_GATEWAY_API_KEY not configured.",
        )
    if not rows:
        return NormalizationResponse(
            available=False,
            message="No rows provided.",
        )
    try:
        prompt = _build_prompt(rows, source_hint)
        data = ai_gateway.chat_json(prompt, system=_SYSTEM, max_tokens=4096)
        return NormalizationResponse(
            available=True,
            rows=[NormalizedFinancialRow(**r) for r in data.get("rows", [])],
            field_mapping=data.get("field_mapping", {}),
            notes=data.get("notes", ""),
            model=ai_gateway.get_model(),
        )
    except Exception as exc:
        return NormalizationResponse(
            available=False,
            message=f"Normalization failed: {exc}",
        )
