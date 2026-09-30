from __future__ import annotations

import asyncio
import hashlib
import mimetypes
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

from ..config import settings
from ..db import connection
from ..policy import host_is_allowed

ALLOWED_MIME_PREFIXES = ("text/", "application/pdf", "application/xml", "application/xhtml+xml")


@dataclass
class AcquisitionResult:
    job_id: str
    source_key: str
    source_url: str
    final_url: str
    content_hash: str
    byte_size: int
    mime_type: str
    status: str
    storage_uri: str


class IngestionService:
    async def acquire(self, source_key: str, source_url: str, actor: str = "system") -> AcquisitionResult:
        source = await self._source(source_key)
        if not source:
            raise ValueError("Unknown or inactive source_key")
        if not host_is_allowed(source_url, source["official_url"]):
            raise ValueError("The requested URL is outside the registered official source domain")

        fetched = await asyncio.to_thread(self._fetch, source_url, source["official_url"])
        return await self._persist(
            source=source,
            source_key=source_key,
            source_url=source_url,
            final_url=fetched["final_url"],
            body=fetched["body"],
            mime_type=fetched["mime_type"],
            actor=actor,
            etag=fetched.get("etag"),
            last_modified=fetched.get("last_modified"),
            http_status=fetched.get("http_status"),
            acquisition_kind="automatic",
        )

    async def acquire_bytes(
        self,
        source_key: str,
        source_url: str,
        body: bytes,
        mime_type: str,
        actor: str,
    ) -> AcquisitionResult:
        source = await self._source(source_key)
        if not source:
            raise ValueError("Unknown or inactive source_key")
        if not host_is_allowed(source_url, source["official_url"]):
            raise ValueError("The declared URL is outside the registered official source domain")
        normalized_mime = self._validate_body(body, mime_type)
        return await self._persist(
            source=source,
            source_key=source_key,
            source_url=source_url,
            final_url=source_url,
            body=body,
            mime_type=normalized_mime,
            actor=actor,
            etag=None,
            last_modified=None,
            http_status=None,
            acquisition_kind="operator_supplied",
        )

    async def _persist(
        self,
        *,
        source: dict,
        source_key: str,
        source_url: str,
        final_url: str,
        body: bytes,
        mime_type: str,
        actor: str,
        etag: str | None,
        last_modified: str | None,
        http_status: int | None,
        acquisition_kind: str,
    ) -> AcquisitionResult:
        content_hash = hashlib.sha256(body).hexdigest()
        extension = self._extension(mime_type, final_url)
        relative = Path("original") / source_key / f"{content_hash}{extension}"
        target = settings.storage_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(body)

        job_id = str(uuid.uuid4())
        storage_uri = target.as_posix()
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select content_hash from source_snapshots
                    where source_id=%s order by captured_at desc, id desc limit 1
                    """,
                    (source["id"],),
                )
                previous_snapshot = await cur.fetchone()
                if acquisition_kind == "operator_supplied":
                    check_outcome = "manual_review"
                    check_note = (
                        "Binary supplied by an authenticated CODO operator; declared official URL "
                        "matches the registered institutional domain and requires source verification."
                    )
                elif previous_snapshot and previous_snapshot["content_hash"] == content_hash:
                    check_outcome = "unchanged"
                    check_note = "Official source fetched by CODO acquisition pipeline"
                elif previous_snapshot:
                    check_outcome = "changed"
                    check_note = "Official source fetched by CODO acquisition pipeline"
                else:
                    check_outcome = "reachable"
                    check_note = "Official source fetched by CODO acquisition pipeline"

                await cur.execute(
                    """
                    insert into source_snapshots(
                      source_id, source_url, final_url, content_hash, storage_uri,
                      mime_type, byte_size, http_etag, http_last_modified
                    ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (source_id, content_hash) do update set
                      source_url=excluded.source_url,
                      final_url=excluded.final_url,
                      mime_type=excluded.mime_type,
                      byte_size=excluded.byte_size,
                      http_etag=excluded.http_etag,
                      http_last_modified=excluded.http_last_modified
                    """,
                    (
                        source["id"], source_url, final_url, content_hash, storage_uri,
                        mime_type, len(body), etag, last_modified,
                    ),
                )
                await cur.execute(
                    """
                    insert into ingestion_jobs(
                      id, source_id, source_url, final_url, status, content_hash,
                      original_storage_uri, mime_type, byte_size, http_etag,
                      http_last_modified, created_by
                    ) values (%s,%s,%s,%s,'imported',%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        job_id, source["id"], source_url, final_url, content_hash,
                        storage_uri, mime_type, len(body), etag, last_modified, actor,
                    ),
                )
                await cur.execute(
                    """
                    insert into ingestion_artifacts(
                      ingestion_job_id, artifact_type, storage_uri, content_hash
                    ) values (%s,'original',%s,%s)
                    """,
                    (job_id, storage_uri, content_hash),
                )
                await cur.execute(
                    """
                    insert into source_registry_checks(
                      source_id, checked_url, outcome, content_hash, http_status, note
                    ) values (%s,%s,%s,%s,%s,%s)
                    """,
                    (source["id"], source_url, check_outcome, content_hash, http_status, check_note),
                )
                await cur.execute(
                    "update legal_sources set last_checked_at=now(), updated_at=now() where id=%s",
                    (source["id"],),
                )
                await cur.execute(
                    """
                    insert into ingestion_job_events(
                      ingestion_job_id, from_status, to_status, actor_subject, note
                    ) values (%s,null,'imported',%s,%s)
                    """,
                    (
                        job_id,
                        actor,
                        "Official source acquired and hashed"
                        if acquisition_kind == "automatic"
                        else "Official-source binary supplied by operator and hashed; manual source verification required",
                    ),
                )
                await cur.execute(
                    """
                    insert into audit_logs(actor_subject, action, entity_type, entity_id, new_data)
                    values (%s,%s,'ingestion_job',%s,%s::jsonb)
                    """,
                    (
                        actor,
                        "acquire_source" if acquisition_kind == "automatic" else "supply_source_binary",
                        job_id,
                        '{"status":"imported"}',
                    ),
                )
                await conn.commit()

        return AcquisitionResult(
            job_id=job_id,
            source_key=source_key,
            source_url=source_url,
            final_url=final_url,
            content_hash=content_hash,
            byte_size=len(body),
            mime_type=mime_type,
            status="imported",
            storage_uri=storage_uri,
        )

    async def _source(self, source_key: str):
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "select id, source_key, official_url from legal_sources where source_key=%s and active=true",
                    (source_key,),
                )
                return await cur.fetchone()

    def _fetch(self, url: str, official_url: str) -> dict:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "CODO-Legal-Ingestion/0.6 (+source-verification)"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            final_url = response.geturl()
            if not host_is_allowed(final_url, official_url):
                raise ValueError("Redirect left the registered official source domain")
            mime_type = response.headers.get_content_type().lower()
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > settings.acquisition_max_bytes:
                raise ValueError("Source document exceeds acquisition size limit")
            body = response.read(settings.acquisition_max_bytes + 1)
            mime_type = self._validate_body(body, mime_type)
            return {
                "body": body,
                "final_url": final_url,
                "mime_type": mime_type,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "http_status": getattr(response, "status", None),
            }

    @staticmethod
    def _validate_body(body: bytes, mime_type: str) -> str:
        normalized = mime_type.split(";", 1)[0].strip().lower()
        if not body:
            raise ValueError("Source document is empty")
        if len(body) > settings.acquisition_max_bytes:
            raise ValueError("Source document exceeds acquisition size limit")
        if not any(normalized.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES):
            raise ValueError(f"Unsupported source MIME type: {normalized}")
        if normalized == "application/pdf" and not body.startswith(b"%PDF-"):
            raise ValueError("Declared PDF does not have a valid PDF signature")
        return normalized

    @staticmethod
    def _extension(mime_type: str, url: str) -> str:
        guessed = mimetypes.guess_extension(mime_type) or ""
        if guessed:
            return guessed
        suffix = Path(urllib.parse.urlparse(url).path).suffix
        return suffix if len(suffix) <= 8 else ""
