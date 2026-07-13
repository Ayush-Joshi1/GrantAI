from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.v1.schemas.common import SourceResponse, StartupProfileInput


class RecommendRequest(BaseModel):
    query: str | None = Field(default=None, description="Optional free-text preferences")
    limit: int = Field(default=10, ge=1, le=50)
    startup_profile: StartupProfileInput | None = Field(default=None, description="Optional startup context for recommendation")


class RecommendedGrant(BaseModel):
    grant_id: str
    title: str
    score: float = Field(ge=0, le=1)
    reason: str


class RecommendResponse(BaseModel):
    answer: str = Field(default="", description="Grounded recommendation summary")
    sources: list[SourceResponse] = Field(default_factory=list)
    results: list[RecommendedGrant] = Field(default_factory=list)

