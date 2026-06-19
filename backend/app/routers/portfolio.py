from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    ESGMetric,
    ESGMetricRead,
    FinancialRecord,
    FinancialRecordRead,
    PortfolioCompany,
    PortfolioCompanyDetail,
    RiskAlert,
    RiskAlertRead,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


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
