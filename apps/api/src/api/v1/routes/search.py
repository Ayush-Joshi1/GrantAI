from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.search import SearchRequest, SearchResponse, SearchResult
from src.application.deps import get_search_service
from src.application.services.search_service import SearchService

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(payload: SearchRequest, svc: SearchService = Depends(get_search_service)):
    results = await svc.search(query=payload.query, limit=payload.limit)
    return SearchResponse(results=[SearchResult(**r) for r in results])

