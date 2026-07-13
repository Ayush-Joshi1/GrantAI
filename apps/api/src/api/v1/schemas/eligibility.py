from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import EligibilityStatus, SelectedGrantInput, SourceResponse, StartupProfileInput


class EligibilityCheckRequest(BaseModel):
    grant_id: str | None = Field(default=None, description="Optional legacy grant identifier", max_length=200)
    startup_profile_id: str | None = Field(default=None, description="Optional legacy startup profile identifier", max_length=200)
    answers: dict[str, str] = Field(default_factory=dict, description="Legacy answer map for placeholder services")
    selected_grant: SelectedGrantInput | None = Field(default=None, description="Trusted grant context for eligibility analysis")
    startup_profile: StartupProfileInput | None = Field(default=None, description="Structured startup profile for eligibility analysis")
    additional_answers: dict[str, str] = Field(default_factory=dict, description="Structured additional answers")
    additional_context: str | None = Field(default=None, description="Additional context for eligibility analysis", max_length=12000)


class EligibilityCheckResponse(BaseModel):
    eligibility_status: EligibilityStatus = Field(default=EligibilityStatus.INSUFFICIENT_INFORMATION)
    answer: str | None = Field(default=None, description="Grounded eligibility analysis")
    analysis: str | None = Field(default=None, description="Alternative analysis field for richer responses")
    reasons: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    sources: list[SourceResponse] = Field(default_factory=list)
    decision: Literal["eligible", "not_eligible", "unknown"] | None = Field(default=None)
    confidence: float | None = Field(default=None, ge=0, le=1)
    missing_info: list[str] = Field(default_factory=list)

