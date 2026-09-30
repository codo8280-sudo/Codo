from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from ..config import settings
from ..db import connection
from ..schemas import DraftMetadataIn, StructuredArticleIn, StructuredDocumentIn


class _VisibleTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip_depth += 1
        elif tag.lower() in {"p", "div", "section", "article", "br", "li", "h1", "h2", "h3", "h4"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag.lower() in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


@dataclass(frozen=True)
class ExtractedArtifact:
    job_id: str
    text_path: str
    content_hash: str
    page_count: int | None
    char_count: int
    status: str


@dataclass(frozen=True)
class ArticleCandidate:
    label: str
    stable_token: str
    official_text: str
    sort_order: int


@dataclass(frozen=True)
class DraftDiagnostics:
    article_count: int
    duplicate_labels: list[str]
    numeric_gaps: list[int]
    first_article_number: int | None
    last_article_number: int | None
    warnings: list[str]


class LegalTextParser:
    """Conservative parser used only to create a review draft.

    It deliberately does not infer whether a provision is currently applicable.
    All generated legal statuses remain verification_pending until human review.
    """

    ARTICLE_RE = re.compile(
        r"(?im)^\s*article\s+(?P<number>\d{1,4}|premier)(?P<suffix>\s*(?:bis|ter|quater|quinquies))?"
        r"(?:\s*[-–—:]?\s*(?P<qualifier>nouveau|nouvelle|modifi[eé]|abrog[eé]))?\s*[.:]?\s*$"
    )
    PAGE_MARKER_RE = re.compile(r"(?m)^\s*\[CODO_PAGE\s+\d+\]\s*$")

    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\n[ \t]+", "\n", value)
        value = re.sub(r"\n{4,}", "\n\n\n", value)
        return value.strip()

    @classmethod
    def legal_text(cls, value: str) -> str:
        # Page markers are extraction metadata, never part of the official text.
        value = cls.PAGE_MARKER_RE.sub("", value)
        return cls.normalize_text(value)

    @classmethod
    def parse_articles(cls, value: str) -> tuple[list[ArticleCandidate], DraftDiagnostics]:
        text = cls.legal_text(value)
        matches = list(cls.ARTICLE_RE.finditer(text))
        articles: list[ArticleCandidate] = []
        labels: list[str] = []
        numeric_numbers: list[int] = []

        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            raw_number = match.group("number").lower()
            number = 1 if raw_number == "premier" else int(raw_number)
            suffix = (match.group("suffix") or "").strip().lower()
            qualifier = (match.group("qualifier") or "").strip()
            label = f"Article {number}"
            stable_token = f"{number:03d}"
            if suffix:
                label += f" {suffix}"
                stable_token += f"-{suffix.upper()}"
            if qualifier:
                label += f" — {qualifier.capitalize()}"
            if not body:
                continue
            labels.append(label.lower())
            numeric_numbers.append(number)
            articles.append(
                ArticleCandidate(
                    label=label,
                    stable_token=stable_token,
                    official_text=body,
                    sort_order=index + 1,
                )
            )

        duplicates = sorted({label for label in labels if labels.count(label) > 1})
        unique_numbers = sorted(set(numeric_numbers))
        gaps: list[int] = []
        if unique_numbers:
            expected = set(range(unique_numbers[0], unique_numbers[-1] + 1))
            gaps = sorted(expected.difference(unique_numbers))

        warnings: list[str] = []
        if not articles:
            warnings.append("Aucun article détecté automatiquement; structuration manuelle requise.")
        if duplicates:
            warnings.append("Des libellés d'articles sont dupliqués et doivent être contrôlés.")
        if gaps:
            warnings.append("La numérotation contient des ruptures; elles peuvent être légitimes mais doivent être vérifiées.")
        diagnostics = DraftDiagnostics(
            article_count=len(articles),
            duplicate_labels=duplicates,
            numeric_gaps=gaps,
            first_article_number=unique_numbers[0] if unique_numbers else None,
            last_article_number=unique_numbers[-1] if unique_numbers else None,
            warnings=warnings,
        )
        return articles, diagnostics

    @classmethod
    def build_package(
        cls,
        *,
        source_snapshot_hash: str,
        metadata: DraftMetadataIn,
        extracted_text: str,
    ) -> tuple[StructuredDocumentIn, DraftDiagnostics]:
        normalized = cls.legal_text(extracted_text)
        article_candidates, diagnostics = cls.parse_articles(normalized)
        articles = [
            StructuredArticleIn(
                codo_id=f"{metadata.codo_id}-ART-{candidate.stable_token}",
                label=candidate.label,
                official_text=candidate.official_text,
                status="verification_pending",
                valid_from=metadata.valid_from,
                sort_order=candidate.sort_order,
            )
            for candidate in article_candidates
        ]
        package = StructuredDocumentIn(
            source_snapshot_hash=source_snapshot_hash,
            codo_id=metadata.codo_id,
            domain_slug=metadata.domain_slug,
            nature=metadata.nature,
            title=metadata.title,
            document_number=metadata.document_number,
            status="verification_pending",
            authority_name=metadata.authority_name,
            adoption_date=metadata.adoption_date,
            publication_date=metadata.publication_date,
            version_key=metadata.version_key,
            valid_from=metadata.valid_from,
            valid_to=metadata.valid_to,
            official_text=normalized,
            articles=articles,
        )
        return package, diagnostics


class ExtractionService:
    async def extract(self, job_id: str, actor: str) -> ExtractedArtifact:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from ingestion_jobs where id=%s for update", (job_id,))
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                if job["status"] not in {"imported", "to_analyze"}:
                    raise ValueError("Only an imported or to_analyze job can be extracted")
                source_path = Path(job["original_storage_uri"] or "")
                if not source_path.exists() or not source_path.is_file():
                    raise ValueError("Original source artifact is unavailable")

                text, page_count = self._extract_file(source_path, job.get("mime_type") or "")
                text = LegalTextParser.normalize_text(text)
                if not text:
                    raise ValueError("No extractable text was found in the source artifact")

                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                target = settings.storage_dir / "extracted" / f"{job_id}.txt"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")

                await cur.execute(
                    """
                    insert into ingestion_artifacts(ingestion_job_id, artifact_type, storage_uri, content_hash)
                    values (%s,'extracted_text',%s,%s)
                    """,
                    (job_id, target.as_posix(), digest),
                )
                if job["status"] == "imported":
                    await cur.execute("update ingestion_jobs set status='to_analyze', updated_at=now() where id=%s", (job_id,))
                    await cur.execute(
                        "insert into ingestion_job_events(ingestion_job_id, from_status, to_status, actor_subject, note) values (%s,'imported','to_analyze',%s,%s)",
                        (job_id, actor, "Original document extracted; legal structuring remains pending"),
                    )
                await cur.execute(
                    "insert into audit_logs(actor_subject, action, entity_type, entity_id, new_data) values (%s,'extract_source','ingestion_job',%s,%s::jsonb)",
                    (
                        actor,
                        job_id,
                        '{"artifact_type":"extracted_text","status":"to_analyze"}',
                    ),
                )
                await conn.commit()

        return ExtractedArtifact(
            job_id=job_id,
            text_path=target.as_posix(),
            content_hash=digest,
            page_count=page_count,
            char_count=len(text),
            status="to_analyze",
        )

    async def draft(self, job_id: str, metadata: DraftMetadataIn, actor: str) -> tuple[StructuredDocumentIn, DraftDiagnostics]:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from ingestion_jobs where id=%s", (job_id,))
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                if job["status"] != "to_analyze":
                    raise ValueError("The ingestion job must be in to_analyze status before draft generation")
                await cur.execute(
                    """
                    select storage_uri from ingestion_artifacts
                    where ingestion_job_id=%s and artifact_type='extracted_text'
                    order by id desc limit 1
                    """,
                    (job_id,),
                )
                artifact = await cur.fetchone()
                if not artifact:
                    raise ValueError("No extracted_text artifact exists for this ingestion job")
                extracted_path = Path(artifact["storage_uri"])
                if not extracted_path.exists():
                    raise ValueError("Extracted text artifact is unavailable")
                extracted_text = extracted_path.read_text(encoding="utf-8")
                package, diagnostics = LegalTextParser.build_package(
                    source_snapshot_hash=job["content_hash"],
                    metadata=metadata,
                    extracted_text=extracted_text,
                )

                draft_path = settings.storage_dir / "drafts" / f"{job_id}.json"
                draft_path.parent.mkdir(parents=True, exist_ok=True)
                draft_path.write_text(package.model_dump_json(indent=2), encoding="utf-8")
                draft_hash = hashlib.sha256(draft_path.read_bytes()).hexdigest()
                await cur.execute(
                    """
                    insert into ingestion_artifacts(ingestion_job_id, artifact_type, storage_uri, content_hash)
                    values (%s,'structured_json',%s,%s)
                    """,
                    (job_id, draft_path.as_posix(), draft_hash),
                )
                await cur.execute(
                    "insert into audit_logs(actor_subject, action, entity_type, entity_id, new_data) values (%s,'generate_structure_draft','ingestion_job',%s,%s::jsonb)",
                    (
                        actor,
                        job_id,
                        '{"status":"to_analyze","legal_status":"verification_pending"}',
                    ),
                )
                await conn.commit()
        return package, diagnostics

    def _extract_file(self, path: Path, mime_type: str) -> tuple[str, int | None]:
        suffix = path.suffix.lower()
        mime = mime_type.lower()
        if mime == "application/pdf" or suffix == ".pdf":
            reader = PdfReader(path.as_posix())
            pages: list[str] = []
            for number, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                pages.append(f"\n\n[CODO_PAGE {number}]\n\n{page_text}")
            return "".join(pages), len(reader.pages)
        raw = path.read_bytes()
        decoded = raw.decode("utf-8", errors="replace")
        if "html" in mime or suffix in {".html", ".htm", ".xhtml"}:
            parser = _VisibleTextExtractor()
            parser.feed(decoded)
            return html.unescape(parser.text()), None
        if "xml" in mime or suffix == ".xml":
            return re.sub(r"<[^>]+>", " ", decoded), None
        return decoded, None
