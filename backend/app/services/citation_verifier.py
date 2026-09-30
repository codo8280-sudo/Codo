from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..policy import source_set_is_sufficient
from ..repositories.legal import LegalRepository
from ..schemas import CitationOut


@dataclass
class CitationVerification:
    sufficient: bool
    citations: list[CitationOut]
    verified_rows: list[dict[str, Any]]


class CitationVerifier:
    def __init__(self, repository: LegalRepository):
        self.repository = repository

    async def verify(self, evidence_ids: list[int]) -> CitationVerification:
        unique_ids = list(dict.fromkeys(evidence_ids))
        rows = await self.repository.verify_evidence(unique_ids)
        if len(rows) != len(unique_ids):
            return CitationVerification(False, [], rows)

        trust_levels = [row["trust_level"] for row in rows]
        if not source_set_is_sufficient(trust_levels):
            return CitationVerification(False, [], rows)

        citations = [
            CitationOut(
                source_id=str(row["source_pk"]),
                document_id=row["document_codo_id"],
                article_id=row.get("article_codo_id"),
                version=row["version_key"],
                label=row.get("article_codo_id") or row["document_codo_id"],
                source_url=row["official_url"],
                trust_level=row["trust_level"],
            )
            for row in rows
        ]
        return CitationVerification(True, citations, rows)
