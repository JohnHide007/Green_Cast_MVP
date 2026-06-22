"""
ROI calculator — converts analyst time saved into a payback period vs Green Cast cost.

Default inputs yield payback < one quarter at the growth tier:
  25 companies × 12 hrs × 4 reports/year × 80% automation = 960 hrs saved
  960 × €120/hr = €115,200 annual saving
  Growth tier cost = €24,000/year
  Payback = 24,000 / (115,200 / 12) = 2.5 months
"""

from fastapi import APIRouter

from app.models import RoiInput, RoiResult

router = APIRouter(prefix="/roi", tags=["roi"])

TIER_PRICING: dict[str, float] = {
    "starter":    12_000.0,
    "growth":     24_000.0,
    "enterprise": 48_000.0,
}

TIER_LABELS: dict[str, str] = {
    "starter":    "Starter  (up to 10 holdings)",
    "growth":     "Growth   (up to 50 holdings)",
    "enterprise": "Enterprise (unlimited)",
}

AUTOMATION_SAVING_RATE = 0.80   # 80% of analyst report time eliminated


@router.post("/calculate", response_model=RoiResult)
def calculate_roi(inp: RoiInput) -> RoiResult:
    tier = inp.tier if inp.tier in TIER_PRICING else "growth"
    annual_cost = TIER_PRICING[tier]

    total_report_hours = (
        inp.portfolio_companies
        * inp.hours_per_company_per_report
        * inp.reports_per_year
    )
    hours_saved = round(total_report_hours * AUTOMATION_SAVING_RATE, 1)
    eur_saved   = round(hours_saved * inp.analyst_rate_eur, 2)
    net_saving  = round(eur_saved - annual_cost, 2)

    monthly_saving = eur_saved / 12.0
    payback_months = round(annual_cost / monthly_saving, 2) if monthly_saving > 0 else 999.0

    if payback_months < 1:
        payback_display = f"< 1 month"
    elif payback_months < 1.5:
        payback_display = "~1 month"
    else:
        payback_display = f"{payback_months:.1f} months"

    return RoiResult(
        annual_hours_saved=hours_saved,
        annual_eur_saved=eur_saved,
        greencast_annual_cost=annual_cost,
        net_saving=net_saving,
        payback_months=payback_months,
        payback_display=payback_display,
        tier=tier,
        tier_label=TIER_LABELS[tier],
        inputs=inp,
    )
