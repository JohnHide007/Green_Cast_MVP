"""
Pre-investment screening — same normalization + rules engine as portfolio monitoring,
applied to a ScreeningInput (not yet a portfolio company).
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter

from app.models import (
    ESGMetric,
    FactorType,
    FinancialRecord,
    MacroSignal,
    PortfolioCompany,
    RiskSeverity,
    ScreeningInput,
    ScreeningVerdict,
)
from app.normalization import compute_risk_factors
from app.rules import evaluate_rules

router = APIRouter(prefix="/screening", tags=["screening"])


def _rag(score: float) -> str:
    if score >= 67:
        return "red"
    if score >= 34:
        return "amber"
    return "green"


@router.post("/evaluate", response_model=ScreeningVerdict)
def evaluate_target(inp: ScreeningInput) -> ScreeningVerdict:
    now = datetime.now(timezone.utc)

    # Build transient ORM-like objects (no DB session needed)
    company = PortfolioCompany(
        id=0,
        fund_id=0,
        name=inp.name,
        sector=inp.sector,
        country=inp.country,
        entry_year=now.year,
    )
    esg = ESGMetric(
        id=0,
        company_id=0,
        carbon_intensity=inp.carbon_intensity,
        energy_dependency_score=inp.energy_dependency_score,
        supplier_concentration=inp.supplier_concentration,
        epc_rating=inp.epc_rating,
    )

    # Single financial record — annualise by using quarterly values directly
    fin = FinancialRecord(
        id=0,
        company_id=0,
        year=now.year,
        quarter=1,
        revenue=inp.revenue_em,
        ebitda=inp.ebitda_em,
        net_debt=inp.net_debt_em,
    )

    macro: list[MacroSignal] = [
        MacroSignal(
            id=0,
            company_id=0,
            signal_type="CBAM_EXPOSURE",
            level=inp.cbam_level,
            value={"high": 0.85, "medium": 0.55, "low": 0.20, "none": 0.0}.get(inp.cbam_level, 0.0),
            description=f"CBAM level: {inp.cbam_level}",
            source_ref="screening_input",
        )
    ]
    if inp.epc_rating:
        macro.append(MacroSignal(
            id=0,
            company_id=0,
            signal_type="INTEREST_RATE_SENSITIVITY",
            level="high" if inp.ir_sensitivity > 0.70 else "medium" if inp.ir_sensitivity > 0.40 else "low",
            value=inp.ir_sensitivity,
            description=f"Interest rate sensitivity: {round(inp.ir_sensitivity * 100)}%",
            source_ref="screening_input",
        ))

    factors = compute_risk_factors(company, esg, [fin], macro)
    alerts = evaluate_rules(company, esg, [fin], macro)

    overall = next((f for f in factors if f.factor_type == FactorType.OVERALL_RISK_SCORE), None)
    tr = next((f for f in factors if f.factor_type == FactorType.TRANSITION_RISK_COMPOSITE), None)
    fin_comp = next((f for f in factors if f.factor_type == FactorType.FINANCIAL_RISK_COMPOSITE), None)

    # Top 3 component factors (not composites), sorted by score descending
    component_types = {
        FactorType.TRANSITION_RISK_COMPOSITE,
        FactorType.FINANCIAL_RISK_COMPOSITE,
        FactorType.OVERALL_RISK_SCORE,
    }
    components = sorted(
        [f for f in factors if f.factor_type not in component_types],
        key=lambda f: f.normalized_value,
        reverse=True,
    )
    top_factors = [
        {
            "factor_type": f.factor_type,
            "normalized_value": f.normalized_value,
            "weight": f.weight,
        }
        for f in components[:3]
    ]
    alert_dicts = [
        {
            "rule_name": a.rule_name,
            "severity": a.severity,
            "category": a.category,
            "description": a.description,
            "threshold_value": a.threshold_value,
            "actual_value": a.actual_value,
        }
        for a in sorted(alerts, key=lambda a: ({"high": 0, "medium": 1, "low": 2}.get(a.severity, 3)))
    ]

    overall_val = overall.normalized_value if overall else 0.0
    tr_val = tr.normalized_value if tr else 0.0
    fin_val = fin_comp.normalized_value if fin_comp else 0.0

    return ScreeningVerdict(
        name=inp.name,
        sector=inp.sector,
        overall_score=round(overall_val, 1),
        transition_score=round(tr_val, 1),
        financial_score=round(fin_val, 1),
        rag_flag=_rag(overall_val),
        top_factors=top_factors,
        alerts=alert_dicts,
    )
