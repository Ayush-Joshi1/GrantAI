from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import DeadlineStatus, SelectedGrantInput, SourceResponse


class DeadlineRequest(BaseModel):
    selected_grant: SelectedGrantInput | None = Field(default=None, description="Trusted grant context for deadline analysis")
    grant_context: str | None = Field(default=None, description="Optional additional grant context", max_length=16000)


class DeadlineResponse(BaseModel):
    deadline_status: DeadlineStatus = Field(default=DeadlineStatus.UNKNOWN)
    deadline: str | None = Field(default=None, description="Deadline text when available")
    days_remaining: int | None = Field(default=None, ge=0, description="Days remaining when a supported deadline is known")
    important_dates: list[str] = Field(default_factory=list)
    recommended_action: str | None = Field(default=None)
    answer: str | None = Field(default=None, description="Grounded deadline analysis")
    analysis: str | None = Field(default=None)
    sources: list[SourceResponse] = Field(default_factory=list)
