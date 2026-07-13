from __future__ import annotations

from pydantic import BaseModel, Field


class ChatTurnRequest(BaseModel):
    session_id: str | None = Field(default=None, description="Client-provided session id (optional)")
    message: str = Field(min_length=1, max_length=5000)


class ChatTurnResponse(BaseModel):
    session_id: str
    reply: str

