from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    ESGMetric,
    ESGMetricRead,
    FactorType,
    FinancialRecord,
    FinancialRecordRead,
    PortfolioCompany,
    PortfolioCompanyDetail,
    RiskAlert,
    RiskAlertRead,
    RiskFactor,
    RiskFactorRead,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# Composite factor types — surfaced first; OVERALL_RISK_SCORE is the primary headline score
_COMPOSITE_TYPES = {
    FactorType.OVERALL_RISK_SCORE,
    FactorType.TRANSITION_RISK_COMPOSITE,
    FactorType.FINANCIAL_RISK_COMPOSITE,
}

_COMPOSITE_ORDER = [
    FactorType.OVERALL_RISK_SCORE,
    FactorType.TRANSITION_RISK_COMPOSITE,
    FactorType.FINANCIAL_RISK_COMPOSITE,
]


@router.get("/{company_id}", response_model=PortfolioCompanyDetail)
def get_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    financials = session.exec(
        select(FinancialRecord)
        .where(FinancialRecord.company_id == company_id)
        .order_by(FinancialRecord.year, FinancialRecord.quarter)
    ).all()

    esg = session.exec(
        select(ESGMetric).where(ESGMetric.company_id == company_id)
    ).all()

    return PortfolioCompanyDetail(
        id=company.id,
        fund_id=company.fund_id,
        name=company.name,
        sector=company.sector,
        country=company.country,
        entry_year=company.entry_year,
        financials=[FinancialRecordRead.model_validate(f) for f in financials],
        esg_metrics=[ESGMetricRead.model_validate(e) for e in esg],
    )


@router.get("/{company_id}/risk-factors", response_model=list[RiskFactorRead])
def get_risk_factors(company_id: int, session: Session = Depends(get_session)):
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    factors = session.exec(
        select(RiskFactor).where(RiskFactor.company_id == company_id)
    ).all()

    composites_by_type = {f.factor_type: f for f in factors if f.factor_type in _COMPOSITE_TYPES}
    components = sorted(
        [f for f in factors if f.factor_type not in _COMPOSITE_TYPES],
        key=lambda f: f.normalized_value,
        reverse=True,
    )

    ordered_composites = [
        composites_by_type[ft]
        for ft in _COMPOSITE_ORDER
        if ft in composites_by_type
    ]

    return [RiskFactorRead.from_orm_with_json(f) for f in ordered_composites + components]


@router.get("/{company_id}/risk-alerts", response_model=list[RiskAlertRead])
def get_risk_alerts(company_id: int, session: Session = Depends(get_session)):
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    alerts = session.exec(
        select(RiskAlert)
        .where(RiskAlert.company_id == company_id)
        .order_by(RiskAlert.created_at.desc())
    ).all()

    return [RiskAlertRead.model_validate(a) for a in alerts]
