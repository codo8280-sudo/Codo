from fastapi import APIRouter, Response, status

from ..config import settings
from ..db import database_ready

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "database_configured": settings.database_configured,
        "database_provider": settings.database_provider,
        "semantic_search_configured": settings.semantic_search_configured,
        "llm_configured": settings.llm_configured,
        "oidc_configured": settings.oidc_configured,
        "legal_answer_policy": "source-first",
    }


@router.get("/health/live")
async def live() -> dict:
    return {"status": "alive", "service": "codo-api"}


@router.get("/health/ready")
async def ready(response: Response) -> dict:
    db_ok, database = await database_ready()
    ready_state = db_ok and settings.oidc_configured
    if not ready_state:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready_state else "not_ready",
        "database": database,
        "database_provider": settings.database_provider,
        "oidc_configured": settings.oidc_configured,
        "source_first_policy": True,
    }
