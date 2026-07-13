from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.profile import ProfileResponse, ProfileUpsertRequest
from src.application.deps import get_profile_service
from src.application.services.profile_service import ProfileService

router = APIRouter()


@router.put("", response_model=ProfileResponse)
async def upsert_profile(
    payload: ProfileUpsertRequest, svc: ProfileService = Depends(get_profile_service)
):
    result = await svc.upsert(payload.model_dump())
    return ProfileResponse(**result)

