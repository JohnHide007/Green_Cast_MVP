from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    Fund,
    FundPortfolio,
    FundRead,
    PortfolioCompany,
    PortfolioCompanyRead,
)

router = APIRouter(prefix="/funds", tags=["funds"])


@router.get("", response_model=list[FundRead])
def list_funds(session: Session = Depends(get_session)):
    return session.exec(select(Fund)).all()


@router.get("/{fund_id}/portfolio", response_model=FundPortfolio)
def get_fund_portfolio(fund_id: int, session: Session = Depends(get_session)):
    fund = session.get(Fund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    companies = session.exec(
        select(PortfolioCompany).where(PortfolioCompany.fund_id == fund_id)
    ).all()

    return FundPortfolio(
        fund=FundRead.model_validate(fund),
        companies=[PortfolioCompanyRead.model_validate(c) for c in companies],
    )
