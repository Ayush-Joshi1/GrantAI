from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.common import SourceResponse
from src.api.v1.schemas.deadlines import DeadlineRequest, DeadlineResponse
from src.application.deps import get_deadline_service
from src.application.services.deadline_service import DeadlineService

router = APIRouter()


@router.post("", response_model=DeadlineResponse)
async def analyze_deadline(payload: DeadlineRequest, svc: DeadlineService = Depends(get_deadline_service)) -> DeadlineResponse:
    result = svc.analyze(selected_grant=payload.selected_grant, deadline_context=payload.grant_context)
    return DeadlineResponse(
        deadline_status=__import__("src.api.v1.schemas.common", fromlist=["DeadlineStatus"]).DeadlineStatus.UNKNOWN,
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
