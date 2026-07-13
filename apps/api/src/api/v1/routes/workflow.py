from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.workflow import UnifiedWorkflowRequest, UnifiedWorkflowResponse
from src.application.services.unified_response_builder import UnifiedResponseBuilder
from src.api.v1.schemas.recommend import RecommendResponse, RecommendedGrant
from src.api.v1.schemas.eligibility import EligibilityCheckResponse
from src.api.v1.schemas.proposal import ProposalGenerateResponse
from src.api.v1.schemas.deadlines import DeadlineResponse
from src.api.v1.schemas.notifications import NotificationResponse
from src.api.v1.schemas.common import SourceResponse, SelectedGrantInput
from src.application.deps import get_workflow_coordinator
from src.application.services.workflow_coordinator import WorkflowCoordinator

router = APIRouter()


@router.post("/unified", response_model=UnifiedWorkflowResponse)
async def run_unified_workflow(
    payload: UnifiedWorkflowRequest, svc: WorkflowCoordinator = Depends(get_workflow_coordinator)
) -> UnifiedWorkflowResponse:
    result = svc.run_unified_workflow(startup_profile=payload.startup_profile, query=payload.query)

    recommend_section = None
    if result.recommendation is not None:
        recommend_section = RecommendResponse(
            answer=result.recommendation.answer,
            sources=[
                SourceResponse(
                    grant_name=s.grant_name,
                    organization=s.organization,
                    source_document=s.source_document,
                    page_number=s.page_number,
                )
                for s in (result.recommendation.sources or [])
            ],
            results=[],
        )

    eligibility_section = None
    if result.eligibility is not None:
        eligibility_section = EligibilityCheckResponse(answer=result.eligibility.answer, sources=[
            SourceResponse(grant_name=s.grant_name, organization=s.organization, source_document=s.source_document, page_number=s.page_number)
            for s in (result.eligibility.sources or [])
        ])

    proposal_section = None
    if result.proposal is not None:
        proposal_section = ProposalGenerateResponse(answer=result.proposal.answer, sources=[
            SourceResponse(grant_name=s.grant_name, organization=s.organization, source_document=s.source_document, page_number=s.page_number)
            for s in (result.proposal.sources or [])
        ])

    deadlines_section = None
    if result.deadlines is not None:
        deadlines_section = DeadlineResponse(answer=result.deadlines.answer, sources=[
            SourceResponse(grant_name=s.grant_name, organization=s.organization, source_document=s.source_document, page_number=s.page_number)
            for s in (result.deadlines.sources or [])
        ])

    notification_section = None
    if result.notification is not None:
        notification_section = NotificationResponse(answer=result.notification.answer, message=result.notification.answer, sources=[
            SourceResponse(grant_name=s.grant_name, organization=s.organization, source_document=s.source_document, page_number=s.page_number)
            for s in (result.notification.sources or [])
        ])

    readable = UnifiedResponseBuilder.build_readable(result)

    return UnifiedWorkflowResponse(
        startup_summary=result.startup_summary,
        recommendation=recommend_section,
        eligibility=eligibility_section,
        proposal=proposal_section,
        deadlines=deadlines_section,
        notification=notification_section,
        partial=result.partial,
        errors=result.errors,
    )
