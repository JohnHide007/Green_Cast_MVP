from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.commentary import generate_commentary
from app.database import get_session
from app.models import (
    CommentaryResponse,
    PortfolioCompany,
    RiskAlert,
    RiskFactor,
)

router = APIRouter(prefix="/portfolio", tags=["commentary"])


@router.post("/{company_id}/commentary", response_model=CommentaryResponse)
def get_commentary(company_id: int, session: Session = Depends(get_session)):
    company = session.get(PortfolioCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    factors = session.exec(
        select(RiskFactor).where(RiskFactor.company_id == company_id)
    ).all()
    alerts = session.exec(
        select(RiskAlert).where(RiskAlert.company_id == company_id)
    ).all()

    return generate_commentary(
        company_id=company_id,
        company_name=company.name,
        sector=company.sector,
        factors=list(factors),
        alerts=list(alerts),
    )
