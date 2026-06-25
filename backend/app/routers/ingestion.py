from fastapi import APIRouter

from app.ingestion import normalize_rows
from app.models import NormalizationInput, NormalizationResponse

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/normalize", response_model=NormalizationResponse)
def normalize(payload: NormalizationInput):
    """AI-assisted normalization: map messy financial rows to the canonical schema."""
    return normalize_rows(payload.rows, payload.source_hint)
