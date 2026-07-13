from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileUpsertRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=200)
    location: str = Field(min_length=2, max_length=200)
    sector: str = Field(min_length=2, max_length=200)
    incorporation_date: str = Field(min_length=4, max_length=32)


class ProfileResponse(BaseModel):
    profile_id: str
    company_name: str
    location: str
    sector: str
    incorporation_date: str

