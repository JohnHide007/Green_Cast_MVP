"""
Deterministic rules engine — named threshold rules that evaluate raw inputs
and emit RiskAlert objects. All rule logic is transparent and auditable.
"""

from datetime import datetime, timezone

from app.models import ESGMetric, FinancialRecord, MacroSignal, PortfolioCompany, RiskAlert, RiskSeverity

RULE_NAMES: frozenset[str] = frozenset({
    "EPC_BELOW_C",
    "CARBON_INTENSITY_HIGH",
    "CARBON_INTENSITY_MODERATE",
    "ENERGY_DEPENDENCY_HIGH",
    "SUPPLIER_CONCENTRATION_HIGH",
    "CBAM_HIGH_EXPOSURE",
    "CBAM_MEDIUM_EXPOSURE",
    "LEVERAGE_HIGH",
    "LEVERAGE_MODERATE",
    "LTV_HIGH",
    "EBITDA_MARGIN_LOW",
    "INTEREST_RATE_HIGH_EXPOSURE",
})


def evaluate_rules(
    company: PortfolioCompany,
    esg: ESGMetric,
    financials: list[FinancialRecord],
    macro_signals: list[MacroSignal],
) -> list[RiskAlert]:
    """
    Run all named rules against a company's raw inputs.
    Returns only the alerts that fire (threshold breached).
    """
    alerts: list[RiskAlert] = []
    now = datetime.now(timezone.utc)
    cid = company.id

    def _alert(
        rule_name: str,
        severity: RiskSeverity,
        category: str,
        description: str,
        threshold: float | None = None,
        actual: float | None = None,
    ) -> RiskAlert:
        return RiskAlert(
            company_id=cid,
            rule_name=rule_name,
            severity=severity,
            category=category,
            description=description,
            threshold_value=threshold,
            actual_value=actual,
            created_at=now,
        )

    # ── EPC rules ─────────────────────────────────────────────────────────────
    if esg.epc_rating:
        rating = esg.epc_rating.upper()
        if rating in ("D", "E", "F", "G"):
            alerts.append(_alert(
                "EPC_BELOW_C",
                RiskSeverity.high if rating in ("E", "F", "G") else RiskSeverity.medium,
                "Regulatory Risk",
                (
                    f"EPC {rating} rating triggers mandatory renovation obligation under EU EPBD. "
                    f"Estimated retrofit cost to reach grade C: high capex exposure. "
                    f"Mandatory compliance deadline 2033 for worst-rated stock."
                ),
                threshold=45.0,
                actual={"D": 70.0, "E": 85.0, "F": 95.0, "G": 100.0}.get(rating, 70.0),
            ))

    # ── Carbon intensity rules ────────────────────────────────────────────────
    carbon = esg.carbon_intensity
    if carbon > 200.0:
        alerts.append(_alert(
            "CARBON_INTENSITY_HIGH",
            RiskSeverity.high,
            "Transition Risk",
            (
                f"Carbon intensity {carbon:.0f} tCO₂e/€M exceeds EU ETS Phase 4 benchmark (200). "
                f"Increasing EU carbon price trajectory expected to materially affect cost base. "
                f"CSRD Scope 1–2 disclosure obligation triggered."
            ),
            threshold=200.0,
            actual=carbon,
        ))
    elif carbon > 120.0:
        alerts.append(_alert(
            "CARBON_INTENSITY_MODERATE",
            RiskSeverity.medium,
            "Transition Risk",
            (
                f"Carbon intensity {carbon:.0f} tCO₂e/€M is elevated (benchmark: 120). "
                f"Monitor EU ETS price trajectory; sector average risk of upward rerating."
            ),
            threshold=120.0,
            actual=carbon,
        ))

    # ── Energy dependency ─────────────────────────────────────────────────────
    if esg.energy_dependency_score > 0.70:
        alerts.append(_alert(
            "ENERGY_DEPENDENCY_HIGH",
            RiskSeverity.high if esg.energy_dependency_score > 0.80 else RiskSeverity.medium,
            "Operational Risk",
            (
                f"{round(esg.energy_dependency_score * 100)}% revenue exposure to wholesale energy price volatility. "
                f"Unhedged energy costs create significant EBITDA margin sensitivity."
            ),
            threshold=0.70,
            actual=esg.energy_dependency_score,
        ))

    # ── Supplier concentration ─────────────────────────────────────────────────
    if esg.supplier_concentration > 0.50:
        alerts.append(_alert(
            "SUPPLIER_CONCENTRATION_HIGH",
            RiskSeverity.high if esg.supplier_concentration > 0.65 else RiskSeverity.medium,
            "Supply Chain Risk",
            (
                f"Top-3 suppliers represent {round(esg.supplier_concentration * 100)}% of procurement. "
                f"Single-source dependency creates operational disruption risk under supply shock scenarios."
            ),
            threshold=0.50,
            actual=esg.supplier_concentration,
        ))

    # ── CBAM rules ────────────────────────────────────────────────────────────
    cbam = next((s for s in macro_signals if s.signal_type == "CBAM_EXPOSURE"), None)
    if cbam:
        if cbam.level == "high":
            alerts.append(_alert(
                "CBAM_HIGH_EXPOSURE",
                RiskSeverity.high,
                "Regulatory Risk",
                (
                    f"High CBAM exposure: {cbam.description} "
                    f"EU CBAM full implementation from 2026 introduces direct carbon cost levy."
                ),
            ))
        elif cbam.level == "medium":
            alerts.append(_alert(
                "CBAM_MEDIUM_EXPOSURE",
                RiskSeverity.medium,
                "Regulatory Risk",
                (
                    f"Medium CBAM exposure: {cbam.description} "
                    f"Partial sector scope under EU CBAM Regulation 2023/956."
                ),
            ))

    # ── Interest rate rule (RE only) ──────────────────────────────────────────
    ir = next((s for s in macro_signals if s.signal_type == "INTEREST_RATE_SENSITIVITY"), None)
    if ir and ir.value > 0.70:
        alerts.append(_alert(
            "INTEREST_RATE_HIGH_EXPOSURE",
            RiskSeverity.high if ir.value > 0.80 else RiskSeverity.medium,
            "Financial Risk",
            (
                f"{round(ir.value * 100)}% interest rate sensitivity: {ir.description}"
            ),
            threshold=0.70,
            actual=ir.value,
        ))

    # ── Leverage rules (industrial: net_debt / annual EBITDA) ─────────────────
    latest = (
        sorted(financials, key=lambda f: (f.year, f.quarter))[-1]
        if financials else None
    )
    if latest and esg.epc_rating is None:  # industrial
        annual_ebitda = latest.ebitda * 4.0
        if annual_ebitda > 0:
            leverage = latest.net_debt / annual_ebitda
            if leverage > 5.0:
                alerts.append(_alert(
                    "LEVERAGE_HIGH",
                    RiskSeverity.high,
                    "Financial Risk",
                    (
                        f"Net debt / EBITDA: {leverage:.1f}× (threshold: 5.0×). "
                        f"Leverage at {leverage:.1f}× annualised EBITDA — covenant stress risk "
                        f"under earnings compression or rate rise scenarios."
                    ),
                    threshold=5.0,
                    actual=round(leverage, 2),
                ))
            elif leverage > 3.5:
                alerts.append(_alert(
                    "LEVERAGE_MODERATE",
                    RiskSeverity.medium,
                    "Financial Risk",
                    (
                        f"Net debt / EBITDA: {leverage:.1f}× — above mid-market median (3.5×). "
                        f"Monitor covenant headroom; limited refinancing buffer."
                    ),
                    threshold=3.5,
                    actual=round(leverage, 2),
                ))

    # ── LTV rule (RE: net_debt / annual revenue) ──────────────────────────────
    if latest and esg.epc_rating is not None:  # RE
        annual_rev = latest.revenue * 4.0
        if annual_rev > 0:
            ltv = latest.net_debt / annual_rev
            if ltv > 8.0:
                alerts.append(_alert(
                    "LTV_HIGH",
                    RiskSeverity.high,
                    "Financial Risk",
                    (
                        f"LTV {ltv:.1f}× net debt / annual rental revenue (threshold: 8.0×). "
                        f"Elevated refinancing risk; potential lender covenant breach."
                    ),
                    threshold=8.0,
                    actual=round(ltv, 2),
                ))

    # ── EBITDA margin rule ────────────────────────────────────────────────────
    if latest and latest.revenue > 0:
        margin = latest.ebitda / latest.revenue
        if margin < 0.10:
            alerts.append(_alert(
                "EBITDA_MARGIN_LOW",
                RiskSeverity.high if margin < 0.05 else RiskSeverity.medium,
                "Financial Risk",
                (
                    f"EBITDA margin {round(margin * 100, 1)}% — below minimum threshold (10%). "
                    f"Thin margins leave limited buffer against revenue or cost shocks."
                ),
                threshold=0.10,
                actual=round(margin, 4),
            ))

    return alerts
