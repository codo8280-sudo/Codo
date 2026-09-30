from fastapi import APIRouter, Depends, Query

from ..dependencies import require_database, search_service
from ..schemas import SearchResponse
from ..services.search import SearchService

router = APIRouter(prefix="/v1", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=2, max_length=1000),
    limit: int | None = Query(default=None, ge=1, le=100),
    _: None = Depends(require_database),
    service: SearchService = Depends(search_service),
) -> SearchResponse:
    return await service.search(q, limit=limit)
