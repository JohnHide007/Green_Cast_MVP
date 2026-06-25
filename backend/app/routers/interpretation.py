from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.interpretation import interpret_risk
from app.models import (
    MacroSignal,
    PortfolioCompany,
    RiskAlert,
    RiskFactor,
    RiskInterpretationResponse,
)

router = APIRouter(prefix="/portfolio", tags=["interpretation"])


@router.post("/{company_id}/interpretation", response_model=RiskInterpretationResponse)
def get_interpretation(company_id: int, session: Session = Depends(get_session)):
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    factors = session.exec(
        select(RiskFactor).where(RiskFactor.company_id == company_id)
    ).all()
    alerts = session.exec(
        select(RiskAlert).where(RiskAlert.company_id == company_id)
    ).all()
    signals = session.exec(
        select(MacroSignal).where(MacroSignal.company_id == company_id)
    ).all()

    return interpret_risk(
        company_id=company_id,
        company_name=company.name,
        sector=company.sector,
        factors=list(factors),
        alerts=list(alerts),
        signals=list(signals),
    )
