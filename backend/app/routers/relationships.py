from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import legal_relationship_service, require_database
from ..schemas import LegalRelationshipOut, LegalRelationshipsResponse
from ..services.relationships import LegalRelationshipService

router = APIRouter(prefix="/v1/legal", tags=["legal-relationships"])


@router.get("/documents/{codo_id}/relationships", response_model=LegalRelationshipsResponse)
async def document_relationships(
    codo_id: str,
    _: None = Depends(require_database),
    service: LegalRelationshipService = Depends(legal_relationship_service),
) -> LegalRelationshipsResponse:
    rows = await service.public_relationships(codo_id)
    return LegalRelationshipsResponse(items=[LegalRelationshipOut(**row) for row in rows])
