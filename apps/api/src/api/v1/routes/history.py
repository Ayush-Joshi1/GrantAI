from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.history import HistoryItem, HistoryResponse
from src.application.deps import get_history_service
from src.application.services.history_service import HistoryService

router = APIRouter()


@router.get("", response_model=HistoryResponse)
async def history(svc: HistoryService = Depends(get_history_service)):
    items = await svc.list()
    return HistoryResponse(items=[HistoryItem(**x) for x in items])

