from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.chat import ChatTurnRequest, ChatTurnResponse
from src.application.deps import get_chat_service
from src.application.services.chat_service import ChatService

router = APIRouter()


@router.post("/turn", response_model=ChatTurnResponse)
async def chat_turn(payload: ChatTurnRequest, svc: ChatService = Depends(get_chat_service)):
    result = await svc.turn(session_id=payload.session_id, message=payload.message)
    return ChatTurnResponse(**result)

