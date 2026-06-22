from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    FactorType,
    RiskFactor,
    RiskFactorLineage,
    RiskFactorRead,
)
from app.normalization import TRANSFORM_DESCRIPTIONS

router = APIRouter(prefix="/risk-factors", tags=["risk-factors"])


@router.get("/{factor_id}/lineage", response_model=RiskFactorLineage)
def get_lineage(factor_id: int, session: Session = Depends(get_session)):
    rf = session.get(RiskFactor, factor_id)
    if not rf:
        raise HTTPException(status_code=404, detail="Risk factor not found")

    transform_desc = TRANSFORM_DESCRIPTIONS.get(
        rf.factor_type,
        "No transform description available.",
    )

    return RiskFactorLineage(
        risk_factor=RiskFactorRead.from_orm_with_json(rf),
        transform_description=transform_desc,
        composite_weight_pct=round(rf.weight * 100.0, 1),
    )
