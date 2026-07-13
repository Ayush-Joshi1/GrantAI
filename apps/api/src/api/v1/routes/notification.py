from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.common import SourceResponse
from src.api.v1.schemas.notifications import NotificationRequest, NotificationResponse
from src.application.deps import get_notification_service
from src.application.services.notification_service import NotificationService

router = APIRouter()


@router.post("", response_model=NotificationResponse)
async def create_notification(payload: NotificationRequest, svc: NotificationService = Depends(get_notification_service)) -> NotificationResponse:
    result = svc.create(
        request=payload,
        selected_grant=payload.selected_grant,
        grant_context=payload.grant_context,
        deadline_context=payload.deadline_context,
        action_context=payload.action_context,
        notification_preferences=payload.notification_preferences,
    )
    return NotificationResponse(
        title="Funding update",
        message=result.answer,
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
