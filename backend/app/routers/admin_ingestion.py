from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ..dependencies import extraction_service, ingestion_service, require_admin_roles, require_database
from ..rbac import INGESTION_ROLES
from ..schemas import (
    AcquisitionRequest,
    AcquisitionResponse,
    DraftMetadataIn,
    DraftResponse,
    ExtractionResponse,
)
from ..services.extraction import ExtractionService
from ..services.ingestion import IngestionService

router = APIRouter(prefix="/v1/admin/ingestion", tags=["admin-ingestion"])


@router.post("/acquire", response_model=AcquisitionResponse)
async def acquire(
    request: AcquisitionRequest,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*INGESTION_ROLES)),
    service: IngestionService = Depends(ingestion_service),
) -> AcquisitionResponse:
    try:
        result = await service.acquire(request.source_key, str(request.source_url), actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AcquisitionResponse(**result.__dict__)


@router.post("/acquire-file", response_model=AcquisitionResponse)
async def acquire_file(
    request: Request,
    source_key: str = Query(min_length=2, max_length=120),
    source_url: str = Query(min_length=8, max_length=2000),
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*INGESTION_ROLES)),
    service: IngestionService = Depends(ingestion_service),
) -> AcquisitionResponse:
    try:
        body = await request.body()
        mime_type = request.headers.get("content-type", "application/octet-stream")
        result = await service.acquire_bytes(source_key, source_url, body, mime_type, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AcquisitionResponse(**result.__dict__)


@router.post("/{job_id}/extract", response_model=ExtractionResponse)
async def extract(
    job_id: str,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*INGESTION_ROLES)),
    service: ExtractionService = Depends(extraction_service),
) -> ExtractionResponse:
    try:
        result = await service.extract(job_id, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ExtractionResponse(**result.__dict__)


@router.post("/{job_id}/draft", response_model=DraftResponse)
async def draft(
    job_id: str,
    metadata: DraftMetadataIn,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*INGESTION_ROLES)),
    service: ExtractionService = Depends(extraction_service),
) -> DraftResponse:
    try:
        package, diagnostics = await service.draft(job_id, metadata, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DraftResponse(
        package=package,
        diagnostics={
            "article_count": diagnostics.article_count,
            "duplicate_labels": diagnostics.duplicate_labels,
            "numeric_gaps": diagnostics.numeric_gaps,
            "first_article_number": diagnostics.first_article_number,
            "last_article_number": diagnostics.last_article_number,
            "warnings": diagnostics.warnings,
        },
    )
