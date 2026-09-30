from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ..config import settings
from ..providers.embeddings import EmbeddingProvider
from ..repositories.legal import LegalRepository
from ..schemas import (
    LegalArticleOut,
    LegalDocumentOut,
    LegalSourceOut,
    SearchResponse,
    SearchResultOut,
)


def _source(row: dict[str, Any]) -> LegalSourceOut:
    return LegalSourceOut(
        id=str(row["source_pk"]),
        name=row["source_name"],
        institution_name=row.get("institution_name"),
        trust_level=row["trust_level"],
        url=row["official_url"],
        is_official=bool(row["is_official"]),
        probative_note=row.get("probative_note"),
        verified_at=row.get("verified_at"),
    )


def _document(row: dict[str, Any]) -> LegalDocumentOut:
    return LegalDocumentOut(
        codo_id=row["document_codo_id"],
        title=row["title"],
        nature=row["nature"],
        number=row.get("document_number"),
        status=row["current_status"],
        source=_source(row),
        adoption_date=row.get("adoption_date"),
        publication_date=row.get("publication_date"),
        effective_date=row.get("effective_date"),
        current_version=row.get("version_key"),
        authority_name=row.get("authority_name"),
    )


def _article(row: dict[str, Any]) -> LegalArticleOut | None:
    if not row.get("article_codo_id"):
        return None
    return LegalArticleOut(
        codo_id=row["article_codo_id"],
        document_id=row["document_codo_id"],
        label=row.get("article_label") or "",
        official_text=row.get("official_text") or "",
        status=row.get("article_status") or "verification_pending",
        version=row.get("version_key") or "",
        source=_source(row),
        explanation_codo=row.get("explanation_codo"),
        short_summary=row.get("short_summary"),
        valid_from=row.get("valid_from"),
        valid_to=row.get("valid_to"),
    )


class SearchService:
    def __init__(self, repository: LegalRepository, embeddings: EmbeddingProvider):
        self.repository = repository
        self.embeddings = embeddings

    async def search(self, query: str, limit: int | None = None) -> SearchResponse:
        requested = max(1, min(limit or settings.public_max_results, settings.public_max_results))
        lexical = await self.repository.lexical_search(query, requested * 2)
        semantic: list[dict[str, Any]] = []
        semantic_used = False

        if settings.semantic_search_configured:
            try:
                vector = await self.embeddings.embed(query)
                if vector:
                    semantic = await self.repository.semantic_search(
                        vector,
                        settings.embedding_model,
                        requested * 2,
                    )
                    semantic_used = bool(semantic)
            except Exception:
                # Semantic retrieval is an enhancement. Legal availability must not
                # depend on an external embeddings service; lexical search remains safe.
                semantic = []

        merged: dict[str, dict[str, Any]] = {}
        for rank, row in enumerate(lexical, start=1):
            key = f"{row['document_codo_id']}::{row.get('article_codo_id') or ''}"
            item = dict(row)
            item["rrf"] = 1.0 / (60 + rank)
            item["kind"] = "lexical"
            merged[key] = item

        for rank, row in enumerate(semantic, start=1):
            key = f"{row['document_codo_id']}::{row.get('article_codo_id') or ''}"
            contribution = 1.0 / (60 + rank)
            if key in merged:
                merged[key]["rrf"] += contribution
                merged[key]["kind"] = "hybrid"
                if not merged[key].get("snippet"):
                    merged[key]["snippet"] = row.get("snippet") or ""
            else:
                item = dict(row)
                item["rrf"] = contribution
                item["kind"] = "semantic"
                merged[key] = item

        ordered = sorted(merged.values(), key=lambda x: x["rrf"], reverse=True)[:requested]
        results = [
            SearchResultOut(
                document=_document(row),
                article=_article(row),
                snippet=row.get("snippet") or "",
                score=round(float(row["rrf"]), 8),
                retrieval_kind=row["kind"],
            )
            for row in ordered
        ]
        return SearchResponse(results=results, semantic_search_used=semantic_used)
