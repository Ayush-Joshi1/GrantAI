from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    grant_id: str
    title: str
    snippet: str
    score: float = Field(ge=0)


class SearchResponse(BaseModel):
    results: list[SearchResult]

