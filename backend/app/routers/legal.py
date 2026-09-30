from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import legal_repository, require_database
from ..repositories.legal import LegalRepository
from ..schemas import ArticleVersionOut, DocumentProvenanceOut, ProvenanceSourceOut, PublicationReceiptOut
from ..services.search import _article, _document

router = APIRouter(prefix="/v1", tags=["legal-corpus"])


@router.get("/documents/{codo_id}")
async def document(codo_id: str, _: None = Depends(require_database), repository: LegalRepository = Depends(legal_repository)) -> dict:
    row = await repository.document_by_codo_id(codo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published verified document not found")
    mapped = dict(row)
    mapped["document_codo_id"] = mapped["codo_id"]
    mapped["source_name"] = mapped["source_name"]
    return {"document": _document(mapped).model_dump(mode="json")}


@router.get("/documents/{codo_id}/provenance", response_model=DocumentProvenanceOut)
async def document_provenance(
    codo_id: str,
    _: None = Depends(require_database),
    repository: LegalRepository = Depends(legal_repository),
) -> DocumentProvenanceOut:
    rows = await repository.document_provenance(codo_id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published verified document provenance not found")
    first = rows[0]
    return DocumentProvenanceOut(
        document_id=first["document_codo_id"],
        version_key=first["version_key"],
        sources=[
            ProvenanceSourceOut(
                source_id=str(row["source_pk"]),
                source_name=row["source_name"],
                institution_name=row.get("institution_name"),
                trust_level=row["trust_level"],
                provenance_role=row["provenance_role"],
                source_url=row["source_url"],
                final_url=row.get("final_url"),
                captured_at=row["captured_at"],
                content_hash=row["content_hash"],
                verified_at=row.get("verified_at"),
                note=row.get("note"),
            )
            for row in rows
        ],
    )


@router.get("/documents/{codo_id}/publication-receipt", response_model=PublicationReceiptOut)
async def document_publication_receipt(
    codo_id: str,
    _: None = Depends(require_database),
    repository: LegalRepository = Depends(legal_repository),
) -> PublicationReceiptOut:
    row = await repository.document_publication_receipt(codo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication receipt not found")
    return PublicationReceiptOut(**row)


@router.get("/articles/{codo_id}")
async def article(codo_id: str, _: None = Depends(require_database), repository: LegalRepository = Depends(legal_repository)) -> dict:
    row = await repository.article_by_codo_id(codo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published verified article not found")
    article_out = _article(row)
    if article_out is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published verified article not found")
    return {"article": article_out.model_dump(mode="json")}


@router.get("/articles/{codo_id}/versions")
async def article_versions(codo_id: str, _: None = Depends(require_database), repository: LegalRepository = Depends(legal_repository)) -> dict:
    rows = await repository.article_versions(codo_id)
    versions = [ArticleVersionOut(**row).model_dump(mode="json") for row in rows]
    return {"versions": versions}
