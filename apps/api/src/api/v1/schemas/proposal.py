from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import SelectedGrantInput, SourceResponse, StartupProfileInput


class ProposalGenerateRequest(BaseModel):
    grant_id: str | None = Field(default=None, description="Optional legacy grant identifier", max_length=200)
    startup_profile_id: str | None = Field(default=None, description="Optional legacy startup profile identifier", max_length=200)
    notes: str | None = Field(default=None, max_length=8000)
    selected_grant: SelectedGrantInput | None = Field(default=None, description="Trusted grant context for proposal generation")
    startup_profile: StartupProfileInput | None = Field(default=None, description="Structured startup profile for proposal generation")
    proposal_context: str | None = Field(default=None, description="Additional proposal context", max_length=16000)


class ProposalGenerateResponse(BaseModel):
    proposal_id: str | None = Field(default=None)
    status: str | None = Field(default=None)
    answer: str | None = Field(default=None, description="Grounded proposal draft or summary")
    executive_summary: str | None = Field(default=None)
    problem_statement: str | None = Field(default=None)
    solution: str | None = Field(default=None)
    implementation_plan: str | None = Field(default=None)
    budget: str | None = Field(default=None)
    timeline: str | None = Field(default=None)
    expected_impact: str | None = Field(default=None)
    cover_letter: str | None = Field(default=None)
    sources: list[SourceResponse] = Field(default_factory=list)

