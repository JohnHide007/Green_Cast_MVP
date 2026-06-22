"""
Normalization service — transforms raw FinancialRecord, ESGMetric, and MacroSignal
inputs into canonical RiskFactor rows with full data lineage.

Three-tier composite architecture:
  Component factors → TRANSITION_RISK_COMPOSITE (climate/regulatory)
                     FINANCIAL_RISK_COMPOSITE   (leverage/financial)
                     → OVERALL_RISK_SCORE (weighted average of both)

Weight profiles are materially differentiated by company type:
  - Industrial (PE/PC): CBAM + energy + carbon heavy; no EPC; debt/EBITDA leverage
  - Real Estate (RE):  EPC + LTV heavy; CBAM ≈ 0; interest rate sensitivity included
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.models import (
    ESGMetric,
    FactorType,
    FinancialRecord,
    MacroSignal,
    PortfolioCompany,
    RiskFactor,
)

# ── Normalisation constants ───────────────────────────────────────────────────

CARBON_MAX_TCO2E_PER_EUR_M = 500.0   # upper bound for carbon intensity scale

EPC_RISK_SCORES: dict[str, float] = {
    "A":  5.0,  # exemplary — negligible EPBD obligation
    "B": 20.0,  # good
    "C": 45.0,  # moderate — watch 2030 EPBD trajectory
    "D": 70.0,  # below average — mandatory renovation by 2033
    "E": 85.0,  # poor — significant capex exposure
    "F": 95.0,  # very poor — near-term stranded asset risk
    "G": 100.0, # worst
}

EPC_DESCRIPTIONS: dict[str, str] = {
    "A": "Excellent — negligible EPBD renovation obligation",
    "B": "Good — low renovation risk",
    "C": "Moderate — monitor EPBD 2030 target",
    "D": "Below average — mandatory renovation by 2033 under revised EPBD",
    "E": "Poor — significant retrofit capex exposure",
    "F": "Very poor — near-term stranded asset and tenant flight risk",
    "G": "Worst class — highest renovation liability",
}

CBAM_LEVEL_SCORES: dict[str, float] = {
    "high":   85.0,
    "medium": 55.0,
    "low":    20.0,
    "none":    0.0,
}

# ── Weight profiles ───────────────────────────────────────────────────────────
# Each set sums to 1.0.  Profiles are deliberately differentiated.

# Transition Risk sub-composite weights
TR_WEIGHTS_INDUSTRIAL: dict[FactorType, float] = {
    FactorType.CARBON_INTENSITY:       0.35,
    FactorType.ENERGY_DEPENDENCY:      0.25,
    FactorType.SUPPLIER_CONCENTRATION: 0.20,
    FactorType.CBAM_EXPOSURE:          0.20,  # CBAM is material for industrial sectors
}  # sum = 1.00

TR_WEIGHTS_RE: dict[FactorType, float] = {
    FactorType.EPC_RATING:             0.50,  # primary regulatory driver for RE
    FactorType.CARBON_INTENSITY:       0.25,
    FactorType.ENERGY_DEPENDENCY:      0.15,
    FactorType.SUPPLIER_CONCENTRATION: 0.05,
    FactorType.CBAM_EXPOSURE:          0.05,  # CBAM ≈ 0 for RE (buildings not in scope)
}  # sum = 1.00

# Financial Risk sub-composite weights
FR_WEIGHTS_INDUSTRIAL: dict[FactorType, float] = {
    FactorType.LEVERAGE_RATIO: 0.60,  # net debt / annual EBITDA — standard PE metric
    FactorType.EBITDA_MARGIN:  0.40,
}  # sum = 1.00

FR_WEIGHTS_RE: dict[FactorType, float] = {
    FactorType.LTV_RATIO:                  0.50,  # net debt / annual rental income
    FactorType.INTEREST_RATE_SENSITIVITY:  0.35,  # floating-rate debt exposure
    FactorType.EBITDA_MARGIN:              0.15,
}  # sum = 1.00

# Overall composite weights (TR + FR → OVERALL)
OVERALL_WEIGHTS_INDUSTRIAL: dict[FactorType, float] = {
    FactorType.TRANSITION_RISK_COMPOSITE: 0.65,
    FactorType.FINANCIAL_RISK_COMPOSITE:  0.35,
}

OVERALL_WEIGHTS_RE: dict[FactorType, float] = {
    FactorType.TRANSITION_RISK_COMPOSITE: 0.45,
    FactorType.FINANCIAL_RISK_COMPOSITE:  0.55,  # leverage + rate risk dominate RE
}

# ── Transform descriptions ────────────────────────────────────────────────────

TRANSFORM_DESCRIPTIONS: dict[FactorType, str] = {
    FactorType.CARBON_INTENSITY: (
        "Linear scale 0–500 tCO₂e/€M → 0–100 risk score. "
        "Values above 500 capped at 100. Reference: EU ETS Phase 4 sector benchmarks."
    ),
    FactorType.ENERGY_DEPENDENCY: (
        "Energy dependency score (0.0–1.0) multiplied by 100. "
        "Measures share of revenue directly exposed to wholesale energy price volatility."
    ),
    FactorType.SUPPLIER_CONCENTRATION: (
        "Supplier concentration ratio (0.0–1.0) multiplied by 100. "
        "Measures share of procurement from top-3 suppliers."
    ),
    FactorType.EPC_RATING: (
        "EPC letter grade → risk score: A=5, B=20, C=45, D=70, E=85, F=95, G=100. "
        "Reflects EU Energy Performance of Buildings Directive renovation obligations."
    ),
    FactorType.CBAM_EXPOSURE: (
        "CBAM exposure level → score: high=85, medium=55, low=20, none=0. "
        "Derived from sector classification against EU CBAM Regulation 2023/956, Annex I."
    ),
    FactorType.INTEREST_RATE_SENSITIVITY: (
        "Interest rate sensitivity (0.0–1.0) × 100. "
        "Reflects floating-rate debt proportion and ECB rate trajectory exposure."
    ),
    FactorType.LTV_RATIO: (
        "RE leverage: net debt ÷ annualised rental revenue (quarterly × 4). "
        "Scale: 0–10× → 0–100. Values above 10× capped at 100."
    ),
    FactorType.LEVERAGE_RATIO: (
        "PE/PC leverage: net debt ÷ annualised EBITDA (quarterly × 4). "
        "Scale: 0–8× net debt/EBITDA → 0–100. Industry standard PE leverage range."
    ),
    FactorType.EBITDA_MARGIN: (
        "Inverted EBITDA margin. Formula: max(0, min(100, 100 − margin% × 3.33)). "
        "30%+ margin → 0 risk; 0% → 100. Latest quarter revenue and EBITDA used."
    ),
    FactorType.TRANSITION_RISK_COMPOSITE: (
        "Weighted average of climate and regulatory risk factors. "
        "Industrial profile: CARBON(35%) + ENERGY(25%) + SUPPLIER(20%) + CBAM(20%). "
        "RE profile: EPC(50%) + CARBON(25%) + ENERGY(15%) + SUPPLIER(5%) + CBAM(5%). "
        "CBAM is near-zero for RE as buildings are not directly in scope."
    ),
    FactorType.FINANCIAL_RISK_COMPOSITE: (
        "Weighted average of financial / leverage risk factors. "
        "Industrial: LEVERAGE_net_debt/EBITDA(60%) + EBITDA_MARGIN(40%). "
        "RE: LTV_net_debt/revenue(50%) + INTEREST_RATE_SENSITIVITY(35%) + EBITDA_MARGIN(15%). "
        "RE is more leverage- and rate-sensitive; industrial is EBITDA-covenant driven."
    ),
    FactorType.OVERALL_RISK_SCORE: (
        "Weighted average of TRANSITION_RISK_COMPOSITE and FINANCIAL_RISK_COMPOSITE. "
        "Industrial: TRANSITION(65%) + FINANCIAL(35%) — ESG transition is the primary risk driver. "
        "RE: TRANSITION(45%) + FINANCIAL(55%) — leverage and rate risk dominate for real estate."
    ),
}


# ── Individual transform functions ────────────────────────────────────────────

def norm_carbon(value: float) -> float:
    return round(min(value / CARBON_MAX_TCO2E_PER_EUR_M * 100.0, 100.0), 2)

def norm_energy(value: float) -> float:
    return round(min(value * 100.0, 100.0), 2)

def norm_supplier(value: float) -> float:
    return round(min(value * 100.0, 100.0), 2)

def norm_epc(rating: str) -> float:
    return EPC_RISK_SCORES.get(rating.upper(), 50.0)

def norm_cbam(level: str) -> float:
    return CBAM_LEVEL_SCORES.get(level.lower(), 0.0)

def norm_interest_rate(value: float) -> float:
    return round(min(value * 100.0, 100.0), 2)

def norm_ltv_re(net_debt: float, annual_revenue: float) -> float:
    """RE: net debt / annual rental income, scale 0–10× → 0–100."""
    if annual_revenue <= 0:
        return 100.0
    return round(min((net_debt / annual_revenue) / 10.0 * 100.0, 100.0), 2)

def norm_leverage_industrial(net_debt: float, annual_ebitda: float) -> float:
    """PE/PC: net debt / annual EBITDA, scale 0–8× → 0–100."""
    if annual_ebitda <= 0:
        return 100.0
    return round(min((net_debt / annual_ebitda) / 8.0 * 100.0, 100.0), 2)

def norm_ebitda_margin(ebitda: float, revenue: float) -> float:
    if revenue <= 0:
        return 100.0
    margin = ebitda / revenue
    return round(max(0.0, min(100.0, 100.0 - margin * 333.33)), 2)


# ── Main factory ──────────────────────────────────────────────────────────────

def compute_risk_factors(
    company: PortfolioCompany,
    esg: ESGMetric,
    financials: list[FinancialRecord],
    macro_signals: list[MacroSignal],
) -> list[RiskFactor]:
    """
    Transform raw inputs for one company into RiskFactor rows.
    Architecture: component factors → two sub-composites → one overall score.
    """
    is_re = esg.epc_rating is not None
    tr_weights   = TR_WEIGHTS_RE   if is_re else TR_WEIGHTS_INDUSTRIAL
    fr_weights   = FR_WEIGHTS_RE   if is_re else FR_WEIGHTS_INDUSTRIAL
    ov_weights   = OVERALL_WEIGHTS_RE if is_re else OVERALL_WEIGHTS_INDUSTRIAL
    now = datetime.now(timezone.utc)

    latest = (
        sorted(financials, key=lambda f: (f.year, f.quarter))[-1]
        if financials else None
    )
    annual_rev    = (latest.revenue * 4.0)  if latest else 0.0
    annual_ebitda = (latest.ebitda  * 4.0)  if latest else 0.0

    tr_factors:  list[RiskFactor] = []   # climate/regulatory
    fin_factors: list[RiskFactor] = []   # financial/leverage

    def _make(
        factor_type: FactorType,
        weight: float,
        source_ref: str,
        value: float,
        inputs: list[dict],
    ) -> RiskFactor:
        return RiskFactor(
            company_id=company.id,
            factor_type=factor_type,
            raw_source_ref=source_ref,
            normalized_value=value,
            weight=weight,
            contributing_inputs=json.dumps(inputs),
            last_updated=now,
        )

    # ── Transition / climate factors ──────────────────────────────────────────

    # 1. CARBON_INTENSITY
    tr_factors.append(_make(
        FactorType.CARBON_INTENSITY,
        tr_weights.get(FactorType.CARBON_INTENSITY, 0.0),
        f"ESGMetric#{esg.id}.carbon_intensity",
        norm_carbon(esg.carbon_intensity),
        [{
            "source_table": "ESGMetric", "record_id": esg.id,
            "field": "carbon_intensity", "raw_value": esg.carbon_intensity,
            "unit": "tCO₂e/€M revenue",
            "description": f"Carbon intensity {esg.carbon_intensity} tCO₂e/€M. Normalised 0–500 scale.",
        }],
    ))

    # 2. ENERGY_DEPENDENCY
    tr_factors.append(_make(
        FactorType.ENERGY_DEPENDENCY,
        tr_weights.get(FactorType.ENERGY_DEPENDENCY, 0.0),
        f"ESGMetric#{esg.id}.energy_dependency_score",
        norm_energy(esg.energy_dependency_score),
        [{
            "source_table": "ESGMetric", "record_id": esg.id,
            "field": "energy_dependency_score", "raw_value": esg.energy_dependency_score,
            "unit": "ratio 0–1",
            "description": f"{round(esg.energy_dependency_score * 100)}% revenue exposed to wholesale energy price volatility.",
        }],
    ))

    # 3. SUPPLIER_CONCENTRATION
    tr_factors.append(_make(
        FactorType.SUPPLIER_CONCENTRATION,
        tr_weights.get(FactorType.SUPPLIER_CONCENTRATION, 0.0),
        f"ESGMetric#{esg.id}.supplier_concentration",
        norm_supplier(esg.supplier_concentration),
        [{
            "source_table": "ESGMetric", "record_id": esg.id,
            "field": "supplier_concentration", "raw_value": esg.supplier_concentration,
            "unit": "ratio 0–1",
            "description": f"Top-3 suppliers: {round(esg.supplier_concentration * 100)}% of procurement.",
        }],
    ))

    # 4. EPC_RATING (RE only)
    if is_re and esg.epc_rating:
        rating = esg.epc_rating.upper()
        tr_factors.append(_make(
            FactorType.EPC_RATING,
            tr_weights.get(FactorType.EPC_RATING, 0.0),
            f"ESGMetric#{esg.id}.epc_rating",
            norm_epc(rating),
            [{
                "source_table": "ESGMetric", "record_id": esg.id,
                "field": "epc_rating", "raw_value": esg.epc_rating,
                "unit": "EU EPC grade A–G",
                "description": EPC_DESCRIPTIONS.get(rating, f"EPC {rating}"),
            }],
        ))

    # 5. CBAM_EXPOSURE
    cbam = next((s for s in macro_signals if s.signal_type == "CBAM_EXPOSURE"), None)
    cbam_inputs = [{
        "source_table": "MacroSignal" if cbam else "derived",
        "record_id": cbam.id if cbam else None,
        "field": "CBAM_EXPOSURE",
        "raw_value": cbam.value if cbam else 0.0,
        "unit": "categorical: high/medium/low/none",
        "description": cbam.description if cbam else "No CBAM exposure identified for this sector.",
    }]
    cbam_level = cbam.level if cbam else "none"
    tr_factors.append(_make(
        FactorType.CBAM_EXPOSURE,
        tr_weights.get(FactorType.CBAM_EXPOSURE, 0.0),
        f"MacroSignal#{cbam.id if cbam else 'none'}.CBAM_EXPOSURE",
        norm_cbam(cbam_level),
        cbam_inputs,
    ))

    # ── Financial factors ─────────────────────────────────────────────────────

    # 6. INTEREST_RATE_SENSITIVITY (RE only)
    if is_re:
        ir = next((s for s in macro_signals if s.signal_type == "INTEREST_RATE_SENSITIVITY"), None)
        ir_val = norm_interest_rate(ir.value) if ir else 50.0
        ir_inputs = [{
            "source_table": "MacroSignal" if ir else "derived",
            "record_id": ir.id if ir else None,
            "field": "INTEREST_RATE_SENSITIVITY",
            "raw_value": ir.value if ir else 0.5,
            "unit": "ratio 0–1",
            "description": ir.description if ir else "Default medium interest rate sensitivity applied.",
        }]
        fin_factors.append(_make(
            FactorType.INTEREST_RATE_SENSITIVITY,
            fr_weights.get(FactorType.INTEREST_RATE_SENSITIVITY, 0.0),
            f"MacroSignal#{ir.id if ir else 'default'}.INTEREST_RATE_SENSITIVITY",
            ir_val,
            ir_inputs,
        ))

    # 7a. LTV_RATIO (RE) or LEVERAGE_RATIO (Industrial)
    if latest:
        if is_re:
            fin_factors.append(_make(
                FactorType.LTV_RATIO,
                fr_weights.get(FactorType.LTV_RATIO, 0.0),
                f"FinancialRecord#{latest.id}.net_debt+revenue",
                norm_ltv_re(latest.net_debt, annual_rev),
                [
                    {
                        "source_table": "FinancialRecord", "record_id": latest.id,
                        "field": "net_debt", "raw_value": latest.net_debt, "unit": "€M",
                        "description": f"Net debt €{latest.net_debt}M (Q{latest.quarter} {latest.year})",
                    },
                    {
                        "source_table": "FinancialRecord", "record_id": latest.id,
                        "field": "revenue", "raw_value": round(annual_rev, 2), "unit": "€M annualised",
                        "description": (
                            f"Annualised rental revenue €{round(annual_rev, 1)}M. "
                            f"LTV: {round(latest.net_debt / annual_rev, 2)}× revenue."
                        ),
                    },
                ],
            ))
        else:
            lev_val = norm_leverage_industrial(latest.net_debt, annual_ebitda)
            lev_ratio = round(latest.net_debt / annual_ebitda, 2) if annual_ebitda > 0 else 0
            fin_factors.append(_make(
                FactorType.LEVERAGE_RATIO,
                fr_weights.get(FactorType.LEVERAGE_RATIO, 0.0),
                f"FinancialRecord#{latest.id}.net_debt+ebitda",
                lev_val,
                [
                    {
                        "source_table": "FinancialRecord", "record_id": latest.id,
                        "field": "net_debt", "raw_value": latest.net_debt, "unit": "€M",
                        "description": f"Net debt €{latest.net_debt}M (Q{latest.quarter} {latest.year})",
                    },
                    {
                        "source_table": "FinancialRecord", "record_id": latest.id,
                        "field": "ebitda", "raw_value": round(annual_ebitda, 2), "unit": "€M annualised",
                        "description": (
                            f"Annualised EBITDA €{round(annual_ebitda, 1)}M. "
                            f"Leverage: {lev_ratio}× net debt/EBITDA (PE scale 0–8×)."
                        ),
                    },
                ],
            ))

        # 7b. EBITDA_MARGIN
        margin_pct = round(latest.ebitda / latest.revenue * 100.0, 1) if latest.revenue else 0.0
        fin_factors.append(_make(
            FactorType.EBITDA_MARGIN,
            fr_weights.get(FactorType.EBITDA_MARGIN, 0.0),
            f"FinancialRecord#{latest.id}.ebitda+revenue",
            norm_ebitda_margin(latest.ebitda, latest.revenue),
            [
                {
                    "source_table": "FinancialRecord", "record_id": latest.id,
                    "field": "ebitda", "raw_value": latest.ebitda, "unit": "€M",
                    "description": f"EBITDA €{latest.ebitda}M (Q{latest.quarter} {latest.year})",
                },
                {
                    "source_table": "FinancialRecord", "record_id": latest.id,
                    "field": "revenue", "raw_value": latest.revenue, "unit": "€M",
                    "description": f"Revenue €{latest.revenue}M — margin {margin_pct}%",
                },
            ],
        ))

    all_components = tr_factors + fin_factors

    # ── TRANSITION_RISK_COMPOSITE ─────────────────────────────────────────────
    def _composite(
        ft: FactorType,
        weight: float,
        components: list[RiskFactor],
        source_ref: str,
    ) -> RiskFactor:
        total_w = sum(f.weight for f in components if f.weight > 0)
        val = round(
            sum(f.normalized_value * f.weight for f in components if f.weight > 0) / total_w,
            2,
        ) if total_w > 0 else 0.0
        inputs = [
            {
                "source_table": "RiskFactor", "record_id": None,
                "field": f.factor_type,
                "raw_value": f.normalized_value,
                "unit": f"score 0–100 (weight {round(f.weight * 100)}%)",
                "description": f"{f.factor_type}: {f.normalized_value}/100 — {round(f.weight*100)}% of this composite",
            }
            for f in components if f.weight > 0
        ]
        return RiskFactor(
            company_id=company.id,
            factor_type=ft,
            raw_source_ref=source_ref,
            normalized_value=val,
            weight=weight,
            contributing_inputs=json.dumps(inputs),
            last_updated=now,
        )

    tr_composite = _composite(
        FactorType.TRANSITION_RISK_COMPOSITE,
        ov_weights[FactorType.TRANSITION_RISK_COMPOSITE],
        tr_factors,
        "derived:weighted_average_of_climate_regulatory_factors",
    )
    fin_composite = _composite(
        FactorType.FINANCIAL_RISK_COMPOSITE,
        ov_weights[FactorType.FINANCIAL_RISK_COMPOSITE],
        fin_factors,
        "derived:weighted_average_of_financial_leverage_factors",
    )

    # ── OVERALL_RISK_SCORE ────────────────────────────────────────────────────
    both = [tr_composite, fin_composite]
    total_ov = sum(c.weight for c in both)
    overall_val = round(
        sum(c.normalized_value * c.weight for c in both) / total_ov, 2
    ) if total_ov > 0 else 0.0
    overall = RiskFactor(
        company_id=company.id,
        factor_type=FactorType.OVERALL_RISK_SCORE,
        raw_source_ref="derived:transition_risk_x_financial_risk_composite",
        normalized_value=overall_val,
        weight=1.0,
        contributing_inputs=json.dumps([
            {
                "source_table": "RiskFactor", "record_id": None,
                "field": FactorType.TRANSITION_RISK_COMPOSITE,
                "raw_value": tr_composite.normalized_value,
                "unit": f"score 0–100 (weight {round(tr_composite.weight * 100)}%)",
                "description": (
                    f"Transition Risk: {tr_composite.normalized_value}/100 — "
                    f"{round(tr_composite.weight * 100)}% of overall score"
                ),
            },
            {
                "source_table": "RiskFactor", "record_id": None,
                "field": FactorType.FINANCIAL_RISK_COMPOSITE,
                "raw_value": fin_composite.normalized_value,
                "unit": f"score 0–100 (weight {round(fin_composite.weight * 100)}%)",
                "description": (
                    f"Financial Risk: {fin_composite.normalized_value}/100 — "
                    f"{round(fin_composite.weight * 100)}% of overall score"
                ),
            },
        ]),
        last_updated=now,
    )

    return all_components + [tr_composite, fin_composite, overall]


def normalise_company(session: Session, company_id: int) -> list[RiskFactor]:
    """Idempotent: delete existing RiskFactors, recompute and persist."""
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise ValueError(f"Company {company_id} not found")

    esg_records = session.exec(
        select(ESGMetric).where(ESGMetric.company_id == company_id)
    ).all()
    if not esg_records:
        return []
    esg = esg_records[0]

    financials = session.exec(
        select(FinancialRecord)
        .where(FinancialRecord.company_id == company_id)
        .order_by(FinancialRecord.year, FinancialRecord.quarter)
    ).all()
    macro_signals = session.exec(
        select(MacroSignal).where(MacroSignal.company_id == company_id)
    ).all()

    for rf in session.exec(
        select(RiskFactor).where(RiskFactor.company_id == company_id)
    ).all():
        session.delete(rf)
    session.flush()

    new_factors = compute_risk_factors(company, esg, list(financials), list(macro_signals))
    for rf in new_factors:
        session.add(rf)
    session.flush()
    return new_factors
