from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.common import SourceResponse
from src.api.v1.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse
from src.application.deps import get_eligibility_service
from src.application.services.eligibility_service import EligibilityService

router = APIRouter()


@router.post("/check", response_model=EligibilityCheckResponse)
async def check_eligibility(payload: EligibilityCheckRequest, svc: EligibilityService = Depends(get_eligibility_service)) -> EligibilityCheckResponse:
    result = svc.check(startup_profile=payload.startup_profile, selected_grant=payload.selected_grant)
    return EligibilityCheckResponse(
        answer=result.answer,
        sources=[
            SourceResponse(
                grant_name=source.grant_name,
                organization=source.organization,
                source_document=source.source_document,
                page_number=source.page_number,
            )
            for source in result.sources
        ],
    )

