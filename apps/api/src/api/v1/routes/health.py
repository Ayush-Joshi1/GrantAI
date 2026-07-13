from __future__ import annotations

from fastapi import APIRouter

from src.api.v1.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="GrantAI API", version="1.0", time=__import__("datetime").datetime.utcnow())
