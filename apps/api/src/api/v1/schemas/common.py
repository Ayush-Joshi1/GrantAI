from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    grant_name: str | None = Field(default=None, description="Grant name from trusted retrieval metadata", max_length=200)
    organization: str | None = Field(default=None, description="Grant organization from trusted retrieval metadata", max_length=200)
    source_document: str | None = Field(default=None, description="Source document name when available", max_length=500)
    page_number: int | None = Field(default=None, description="Page number when available", ge=1)


class StartupProfileInput(BaseModel):
    startup_name: str | None = Field(default=None, description="Startup or company name", max_length=200)
    startup_description: str | None = Field(default=None, description="Short description of the startup", max_length=4000)
    sector: str | None = Field(default=None, description="Primary sector or industry", max_length=200)
    startup_stage: str | None = Field(default=None, description="Startup stage or maturity", max_length=120)
    location: str | None = Field(default=None, description="Primary operating location", max_length=200)
    funding_required: str | None = Field(default=None, description="Funding need or target range", max_length=200)
    founder_profile: str | None = Field(default=None, description="Founder or team context", max_length=4000)
    additional_context: str | None = Field(default=None, description="Additional context for agent reasoning", max_length=8000)


class SelectedGrantInput(BaseModel):
    grant_id: str | None = Field(default=None, description="Optional grant identifier when already known", max_length=200)
    grant_name: str | None = Field(default=None, description="Trusted grant name", max_length=200)
    organization: str | None = Field(default=None, description="Granting organization", max_length=200)
    grant_context: str | None = Field(default=None, description="Trusted grant context supplied by the client", max_length=16000)
    source_document: str | None = Field(default=None, description="Optional source document for the grant context", max_length=500)


class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    LIKELY_ELIGIBLE = "likely_eligible"
    NOT_ELIGIBLE = "not_eligible"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class DeadlineStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"


class NotificationType(str, Enum):
    FUNDING_ACTION = "funding_action"
    DEADLINE_REMINDER = "deadline_reminder"
    GENERAL_UPDATE = "general_update"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ErrorResponse(BaseModel):
    request_id: str | None = Field(default=None, description="Correlation/request ID for troubleshooting")
    error: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] | None = Field(default=None, description="Optional structured details")


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    time: datetime

