from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HistoryItem(BaseModel):
    type: str
    title: str
    detail: str
    time: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]

