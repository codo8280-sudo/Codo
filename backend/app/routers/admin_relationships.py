from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import legal_relationship_service, require_admin_roles, require_database
from ..rbac import LEGAL_REVIEW_ROLES, RELATIONSHIP_EDITOR_ROLES
from ..schemas import (
    RelationshipCandidateIn,
    RelationshipCandidateOut,
    RelationshipCandidateReviewIn,
)
from ..services.relationships import LegalRelationshipService

router = APIRouter(prefix="/v1/admin/relationships", tags=["admin-relationships"])


@router.get("", response_model=list[RelationshipCandidateOut])
async def list_candidates(
    status_filter: str | None = Query(default=None, alias="status", pattern="^(pending|validated|rejected)$"),
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*RELATIONSHIP_EDITOR_ROLES)),
    service: LegalRelationshipService = Depends(legal_relationship_service),
) -> list[RelationshipCandidateOut]:
    del actor
    return [RelationshipCandidateOut(**row) for row in await service.list_candidates(status_filter)]


@router.post("", response_model=RelationshipCandidateOut)
async def create_candidate(
    request: RelationshipCandidateIn,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*RELATIONSHIP_EDITOR_ROLES)),
    service: LegalRelationshipService = Depends(legal_relationship_service),
) -> RelationshipCandidateOut:
    try:
        row = await service.create_candidate(request, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RelationshipCandidateOut(**row)


@router.post("/{candidate_id}/review", response_model=RelationshipCandidateOut)
async def review_candidate(
    candidate_id: str,
    request: RelationshipCandidateReviewIn,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*LEGAL_REVIEW_ROLES)),
    service: LegalRelationshipService = Depends(legal_relationship_service),
) -> RelationshipCandidateOut:
    try:
        row = await service.review_candidate(candidate_id, request.approved, actor, request.note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RelationshipCandidateOut(**row)
