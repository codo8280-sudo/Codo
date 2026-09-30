from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import (
    current_admin_principal,
    ingestion_workflow_service,
    require_admin_roles,
    require_database,
)
from ..rbac import ALL_ADMIN_ROLES, INGESTION_ROLES, LEGAL_REVIEW_ROLES, AdminPrincipal, is_authorized
from ..schemas import (
    IngestionJobOut,
    LegalDecisionRequest,
    LegalDecisionResponse,
    QualityReportResponse,
    StructureResponse,
    StructuredDocumentIn,
    WorkflowTransitionRequest,
    WorkflowTransitionResponse,
)
from ..services.workflow import IngestionWorkflowService

router = APIRouter(prefix="/v1/admin/ingestion", tags=["admin-workflow"])


@router.get("/{job_id}", response_model=IngestionJobOut)
async def job_status(
    job_id: str,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*ALL_ADMIN_ROLES)),
    service: IngestionWorkflowService = Depends(ingestion_workflow_service),
) -> IngestionJobOut:
    del actor
    try:
        result = await service.job_status(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return IngestionJobOut(**result)


@router.get("/{job_id}/quality", response_model=QualityReportResponse)
async def quality(
    job_id: str,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*ALL_ADMIN_ROLES)),
    service: IngestionWorkflowService = Depends(ingestion_workflow_service),
) -> QualityReportResponse:
    del actor
    try:
        result = await service.quality_report(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return QualityReportResponse(**result)


@router.post("/{job_id}/structure", response_model=StructureResponse)
async def structure(
    job_id: str,
    package: StructuredDocumentIn,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*INGESTION_ROLES)),
    service: IngestionWorkflowService = Depends(ingestion_workflow_service),
) -> StructureResponse:
    try:
        result = await service.structure(job_id, package, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return StructureResponse(**result.__dict__)


@router.post("/{job_id}/legal-decision", response_model=LegalDecisionResponse)
async def legal_decision(
    job_id: str,
    request: LegalDecisionRequest,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*LEGAL_REVIEW_ROLES)),
    service: IngestionWorkflowService = Depends(ingestion_workflow_service),
) -> LegalDecisionResponse:
    try:
        result = await service.legal_decision(job_id, request, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return LegalDecisionResponse(**result.__dict__)


@router.post("/{job_id}/transition", response_model=WorkflowTransitionResponse)
async def transition(
    job_id: str,
    request: WorkflowTransitionRequest,
    _: None = Depends(require_database),
    principal: AdminPrincipal = Depends(current_admin_principal),
    service: IngestionWorkflowService = Depends(ingestion_workflow_service),
) -> WorkflowTransitionResponse:
    early_targets = {"to_analyze", "structured", "sources_verified"}
    required = INGESTION_ROLES if request.target_status in early_targets else LEGAL_REVIEW_ROLES
    if not is_authorized(principal, required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative role is not authorized for this workflow transition",
        )
    try:
        result = await service.transition(job_id, request.target_status, principal.subject, request.note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return WorkflowTransitionResponse(**result.__dict__)
