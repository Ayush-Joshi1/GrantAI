from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import StartupProfileInput
from src.api.v1.schemas.recommend import RecommendResponse
from src.api.v1.schemas.eligibility import EligibilityCheckResponse
from src.api.v1.schemas.proposal import ProposalGenerateResponse
from src.api.v1.schemas.deadlines import DeadlineResponse
from src.api.v1.schemas.notifications import NotificationResponse


class UnifiedWorkflowRequest(BaseModel):
    startup_profile: StartupProfileInput | None = Field(default=None)
    query: str | None = Field(default=None)


class UnifiedWorkflowResponse(BaseModel):
    startup_summary: str | None = Field(default=None)
    recommendation: RecommendResponse | None = Field(default=None)
    eligibility: EligibilityCheckResponse | None = Field(default=None)
    proposal: ProposalGenerateResponse | None = Field(default=None)
    deadlines: DeadlineResponse | None = Field(default=None)
    notification: NotificationResponse | None = Field(default=None)
    partial: bool = Field(default=False)
    errors: dict[str, str] | None = Field(default=None)
