from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.common import SourceResponse
from src.api.v1.schemas.proposal import ProposalGenerateRequest, ProposalGenerateResponse
from src.application.deps import get_proposal_generation_service
from src.application.services.proposal_service import ProposalGenerationService

router = APIRouter()


@router.post("/generate", response_model=ProposalGenerateResponse)
async def generate_proposal(
    payload: ProposalGenerateRequest, svc: ProposalGenerationService = Depends(get_proposal_generation_service)
) -> ProposalGenerateResponse:
    result = svc.generate(
        startup_profile=payload.startup_profile,
        selected_grant=payload.selected_grant,
        proposal_context=payload.proposal_context,
    )
    return ProposalGenerateResponse(
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

