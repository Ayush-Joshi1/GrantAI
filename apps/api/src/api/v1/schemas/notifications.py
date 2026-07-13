from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import NotificationPriority, NotificationType, SelectedGrantInput, SourceResponse


class NotificationRequest(BaseModel):
    selected_grant: SelectedGrantInput | None = Field(default=None, description="Trusted grant context when available")
    grant_context: str | None = Field(default=None, description="Optional grant context used for the notification")
    deadline_context: str | None = Field(default=None, description="Optional deadline information for the notification")
    action_context: str | None = Field(default=None, description="Optional action or application context for the notification")
    notification_preferences: str | None = Field(default=None, description="User notification preferences or context", max_length=4000)


class NotificationResponse(BaseModel):
    notification_type: NotificationType = Field(default=NotificationType.GENERAL_UPDATE)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    title: str = Field(default="Funding update")
    message: str = Field(default="")
    answer: str | None = Field(default=None, description="Grounded notification guidance")
    recommended_schedule: str | None = Field(default=None)
    sources: list[SourceResponse] = Field(default_factory=list)
