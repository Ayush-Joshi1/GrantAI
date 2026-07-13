from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.common import SourceResponse, StartupProfileInput
from src.api.v1.schemas.recommend import RecommendRequest, RecommendResponse, RecommendedGrant
from src.application.deps import get_grant_recommendation_service
from src.application.services.grant_recommendation_service import GrantRecommendationService

router = APIRouter()


@router.post("", response_model=RecommendResponse)
async def recommend(payload: RecommendRequest, svc: GrantRecommendationService = Depends(get_grant_recommendation_service)) -> RecommendResponse:
    startup_profile = payload.startup_profile or StartupProfileInput()
    result = svc.recommend(startup_profile=startup_profile, query=payload.query)
    return RecommendResponse(
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
        results=[],
    )

