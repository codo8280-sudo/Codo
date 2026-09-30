from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from ..config import settings
from ..db import connection
from ..policy import ingestion_transition_allowed, source_set_is_sufficient
from ..schemas import LegalDecisionRequest, StructuredDocumentIn
from .chunking import rebuild_published_chunks
from .publication import publication_hash
from .quality import blocking_quality_failures


@dataclass
class StructureResult:
    job_id: str
    document_codo_id: str
    document_version_id: int
    article_version_count: int
    status: str


@dataclass
class TransitionResult:
    job_id: str
    previous_status: str
    status: str


@dataclass
class LegalDecisionResult:
    job_id: str
    document_status: str
    article_version_count: int
    status: str


class IngestionWorkflowService:
    async def structure(self, job_id: str, package: StructuredDocumentIn, actor: str) -> StructureResult:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select j.*, s.source_key, s.trust_level, s.verified_at
                    from ingestion_jobs j join legal_sources s on s.id=j.source_id
                    where j.id=%s for update
                    """,
                    (job_id,),
                )
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                if job["status"] not in {"imported", "to_analyze"}:
                    raise ValueError("Only an imported or to_analyze job can be structured")
                if job["content_hash"] != package.source_snapshot_hash:
                    raise ValueError("Structured package does not match the acquired source snapshot hash")
                if job["trust_level"] == "D" or job["verified_at"] is None:
                    raise ValueError("The registered source is not sufficiently verified for legal structuring")

                await cur.execute(
                    """
                    select id, storage_uri, content_hash
                    from source_snapshots
                    where source_id=%s and content_hash=%s
                    limit 1
                    """,
                    (job["source_id"], package.source_snapshot_hash),
                )
                snapshot = await cur.fetchone()
                if not snapshot:
                    raise ValueError("No preserved source snapshot matches the structured package")

                previous_status = job["status"]
                if previous_status == "imported":
                    await self._event(
                        cur,
                        job_id,
                        "imported",
                        "to_analyze",
                        actor,
                        "Analysis entry before legal structuring",
                    )
                    await cur.execute(
                        "update ingestion_jobs set status='to_analyze', updated_at=now() where id=%s",
                        (job_id,),
                    )

                domain_id = None
                if package.domain_slug:
                    await cur.execute(
                        "select id from legal_domains where slug=%s and active=true",
                        (package.domain_slug,),
                    )
                    domain = await cur.fetchone()
                    if not domain:
                        raise ValueError("Unknown or inactive legal domain slug")
                    domain_id = domain["id"]

                await cur.execute(
                    """
                    insert into legal_documents(
                      codo_id, domain_id, source_id, nature, title, document_number,
                      adoption_date, publication_date, current_status, authority_name
                    ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict (codo_id) do update set
                      domain_id=excluded.domain_id,
                      nature=excluded.nature,
                      title=excluded.title,
                      document_number=excluded.document_number,
                      adoption_date=excluded.adoption_date,
                      publication_date=excluded.publication_date,
                      authority_name=excluded.authority_name,
                      updated_at=now()
                    returning id, source_id
                    """,
                    (
                        package.codo_id,
                        domain_id,
                        job["source_id"],
                        package.nature,
                        package.title,
                        package.document_number,
                        package.adoption_date,
                        package.publication_date,
                        "verification_pending",
                        package.authority_name,
                    ),
                )
                document_row = await cur.fetchone()
                document_id = document_row["id"]
                if document_row["source_id"] != job["source_id"]:
                    raise ValueError("Stable CODO document identifier is already bound to another source")

                await cur.execute(
                    "select id from legal_document_versions where document_id=%s and version_key=%s",
                    (document_id, package.version_key),
                )
                existing_dv = await cur.fetchone()
                if existing_dv:
                    await cur.execute(
                        """
                        select 1 from legal_reviews
                        where entity_type='document_version' and entity_id=%s
                          and workflow_status='published'
                        limit 1
                        """,
                        (existing_dv["id"],),
                    )
                    if await cur.fetchone():
                        raise ValueError(
                            "A published document version with this version_key already exists and cannot be overwritten"
                        )

                await cur.execute(
                    """
                    insert into legal_document_versions(
                      document_id, version_key, valid_from, valid_to, status, official_text,
                      source_snapshot_uri, is_current, ingestion_job_id
                    ) values (%s,%s,%s,%s,%s,%s,%s,false,%s)
                    on conflict (document_id, version_key) do update set
                      valid_from=excluded.valid_from,
                      valid_to=excluded.valid_to,
                      status=excluded.status,
                      official_text=excluded.official_text,
                      source_snapshot_uri=excluded.source_snapshot_uri,
                      ingestion_job_id=excluded.ingestion_job_id
                    returning id
                    """,
                    (
                        document_id,
                        package.version_key,
                        package.valid_from,
                        package.valid_to,
                        package.status,
                        package.official_text,
                        snapshot["storage_uri"],
                        job_id,
                    ),
                )
                document_version_id = (await cur.fetchone())["id"]

                await cur.execute(
                    """
                    insert into legal_version_sources(
                      document_version_id, source_snapshot_id, provenance_role, note
                    ) values (%s,%s,'primary_text',%s)
                    on conflict (document_version_id, source_snapshot_id, provenance_role)
                    do update set note=excluded.note
                    """,
                    (
                        document_version_id,
                        snapshot["id"],
                        "Source snapshot acquired and hashed before structuring",
                    ),
                )
                await self._review(cur, "document_version", document_version_id, "structured", actor)

                article_version_count = 0
                for item in package.articles:
                    await cur.execute(
                        """
                        insert into legal_articles(codo_id, document_id, article_label, sort_order)
                        values (%s,%s,%s,%s)
                        on conflict (codo_id) do update set
                          article_label=excluded.article_label,
                          sort_order=excluded.sort_order
                        returning id, document_id
                        """,
                        (item.codo_id, document_id, item.label, item.sort_order),
                    )
                    article_row = await cur.fetchone()
                    article_id = article_row["id"]
                    if article_row["document_id"] != document_id:
                        raise ValueError("Stable CODO article identifier is already bound to another document")

                    await cur.execute(
                        "select id from legal_article_versions where article_id=%s and document_version_id=%s",
                        (article_id, document_version_id),
                    )
                    existing_av = await cur.fetchone()
                    if existing_av:
                        await cur.execute(
                            """
                            select 1 from legal_reviews
                            where entity_type='article_version' and entity_id=%s
                              and workflow_status='published'
                            limit 1
                            """,
                            (existing_av["id"],),
                        )
                        if await cur.fetchone():
                            raise ValueError(
                                "A published article version for this document version already exists and cannot be overwritten"
                            )

                    await cur.execute(
                        """
                        insert into legal_article_versions(
                          article_id, document_version_id, official_text, status, valid_from, valid_to,
                          explanation_codo, short_summary, is_current, ingestion_job_id
                        ) values (%s,%s,%s,%s,%s,%s,%s,%s,false,%s)
                        on conflict (article_id, document_version_id) do update set
                          official_text=excluded.official_text,
                          status=excluded.status,
                          valid_from=excluded.valid_from,
                          valid_to=excluded.valid_to,
                          explanation_codo=excluded.explanation_codo,
                          short_summary=excluded.short_summary,
                          ingestion_job_id=excluded.ingestion_job_id
                        returning id
                        """,
                        (
                            article_id,
                            document_version_id,
                            item.official_text,
                            item.status,
                            item.valid_from,
                            item.valid_to,
                            item.explanation_codo,
                            item.short_summary,
                            job_id,
                        ),
                    )
                    article_version_id = (await cur.fetchone())["id"]
                    await self._review(cur, "article_version", article_version_id, "structured", actor)
                    article_version_count += 1

                artifact = settings.storage_dir / "structured" / f"{job_id}.json"
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text(package.model_dump_json(indent=2), encoding="utf-8")
                artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
                await cur.execute(
                    """
                    insert into ingestion_artifacts(ingestion_job_id, artifact_type, storage_uri, content_hash)
                    values (%s,'structured_json',%s,%s)
                    """,
                    (job_id, artifact.as_posix(), artifact_hash),
                )
                await cur.execute(
                    "update ingestion_jobs set status='structured', updated_at=now() where id=%s",
                    (job_id,),
                )
                await self._event(
                    cur,
                    job_id,
                    "to_analyze",
                    "structured",
                    actor,
                    "Structured legal document package imported",
                )
                await self._audit(
                    cur,
                    actor,
                    "structure_ingestion_job",
                    "ingestion_job",
                    job_id,
                    {"status": previous_status},
                    {
                        "status": "structured",
                        "document_codo_id": package.codo_id,
                        "source_snapshot_id": snapshot["id"],
                    },
                )
                await conn.commit()

        return StructureResult(
            job_id,
            package.codo_id,
            document_version_id,
            article_version_count,
            "structured",
        )

    async def legal_decision(
        self,
        job_id: str,
        request: LegalDecisionRequest,
        actor: str,
    ) -> LegalDecisionResult:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from ingestion_jobs where id=%s for update", (job_id,))
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                if job["status"] != "legal_review":
                    raise ValueError("Legal status can only be decided during legal_review")

                await cur.execute(
                    "select id from legal_document_versions where ingestion_job_id=%s",
                    (job_id,),
                )
                dvs = list(await cur.fetchall())
                if len(dvs) != 1:
                    raise ValueError("Expected exactly one document version for this ingestion job")
                dv_id = dvs[0]["id"]
                await cur.execute(
                    "update legal_document_versions set status=%s, valid_from=coalesce(%s, valid_from) where id=%s",
                    (request.document_status, request.valid_from, dv_id),
                )

                await cur.execute(
                    """
                    select av.id, a.codo_id
                    from legal_article_versions av
                    join legal_articles a on a.id=av.article_id
                    where av.ingestion_job_id=%s
                    """,
                    (job_id,),
                )
                article_rows = list(await cur.fetchall())
                known_ids = {row["codo_id"] for row in article_rows}
                unknown_ids = sorted(set(request.article_statuses).difference(known_ids))
                if unknown_ids:
                    raise ValueError(
                        "Article status decision contains unknown CODO IDs: " + ", ".join(unknown_ids)
                    )

                default_status = request.article_default_status or request.document_status
                for row in article_rows:
                    article_status = request.article_statuses.get(row["codo_id"], default_status)
                    await cur.execute(
                        """
                        update legal_article_versions
                        set status=%s, valid_from=coalesce(%s, valid_from)
                        where id=%s
                        """,
                        (article_status, request.valid_from, row["id"]),
                    )
                    await self._review(
                        cur,
                        "article_version",
                        row["id"],
                        "legal_status_decided",
                        actor,
                        request.note,
                    )

                await self._review(
                    cur,
                    "document_version",
                    dv_id,
                    "legal_status_decided",
                    actor,
                    request.note,
                )
                await self._audit(
                    cur,
                    actor,
                    "legal_status_decision",
                    "ingestion_job",
                    job_id,
                    {"workflow_status": "legal_review"},
                    {
                        "document_status": request.document_status,
                        "article_default_status": default_status,
                        "article_overrides": request.article_statuses,
                        "valid_from": request.valid_from.isoformat() if request.valid_from else None,
                    },
                )
                await conn.commit()

        return LegalDecisionResult(
            job_id=job_id,
            document_status=request.document_status,
            article_version_count=len(article_rows),
            status="legal_review",
        )

    async def quality_report(self, job_id: str) -> dict:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select j.*, s.source_key, s.trust_level, s.verified_at,
                           d.nature, d.title, d.document_number,
                           dv.id as document_version_id, dv.version_key,
                           dv.status as document_legal_status
                    from ingestion_jobs j
                    join legal_sources s on s.id=j.source_id
                    left join legal_document_versions dv on dv.ingestion_job_id=j.id
                    left join legal_documents d on d.id=dv.document_id
                    where j.id=%s
                    limit 1
                    """,
                    (job_id,),
                )
                row = await cur.fetchone()
                if not row:
                    raise ValueError("Ingestion job not found")

                checks: list[dict] = []

                def add(key: str, passed: bool, blocking: bool, detail: str) -> None:
                    checks.append({"key": key, "passed": bool(passed), "blocking": blocking, "detail": detail})

                original = Path(row["original_storage_uri"] or "")
                add(
                    "original_preserved",
                    bool(row["original_storage_uri"] and original.exists() and original.is_file()),
                    True,
                    "Le document original acquis doit être conservé et accessible.",
                )
                add(
                    "source_registry_verified",
                    row["verified_at"] is not None and row["trust_level"] in {"A", "B", "C"},
                    True,
                    "La source doit être enregistrée, datée et de niveau A, B ou C.",
                )

                await cur.execute(
                    """
                    select s.trust_level, s.verified_at, ss.content_hash, ss.storage_uri
                    from legal_version_sources lvs
                    join source_snapshots ss on ss.id=lvs.source_snapshot_id
                    join legal_sources s on s.id=ss.source_id
                    where lvs.document_version_id=%s
                    """,
                    (row["document_version_id"],),
                ) if row["document_version_id"] else None
                provenance = list(await cur.fetchall()) if row["document_version_id"] else []
                provenance_levels = [p["trust_level"] for p in provenance]
                provenance_hash_match = any(p["content_hash"] == row["content_hash"] for p in provenance)
                add(
                    "source_provenance_linked",
                    bool(provenance and source_set_is_sufficient(provenance_levels) and provenance_hash_match),
                    True,
                    "La version doit pointer vers au moins une preuve A/B correspondant au hash acquis.",
                )

                await cur.execute(
                    "select count(*) as n from legal_article_versions where ingestion_job_id=%s",
                    (job_id,),
                )
                article_count = int((await cur.fetchone())["n"])
                normative = (row.get("nature") or "").strip().lower() in {
                    "constitution",
                    "loi",
                    "code",
                    "ordonnance",
                    "décret",
                    "decret",
                    "acte uniforme",
                }
                add(
                    "articles_structured",
                    article_count > 0 or not normative,
                    normative,
                    f"Articles structurés: {article_count}.",
                )

                await cur.execute(
                    """
                    select count(*) filter (where status='verification_pending') as pending,
                           count(*) as total
                    from legal_article_versions
                    where ingestion_job_id=%s
                    """,
                    (job_id,),
                )
                article_status_counts = await cur.fetchone()
                status_final = bool(
                    row["document_version_id"]
                    and row["document_legal_status"]
                    and row["document_legal_status"] != "verification_pending"
                    and int(article_status_counts["pending"] or 0) == 0
                )
                add(
                    "legal_status_decided",
                    status_final,
                    True,
                    "Aucune version de document ou d'article ne peut rester verification_pending.",
                )

                add(
                    "core_metadata_present",
                    bool(row.get("title") and row.get("version_key")),
                    True,
                    "Titre et identifiant de version sont obligatoires.",
                )
                add(
                    "document_number_present",
                    bool(row.get("document_number")),
                    False,
                    "Le numéro du texte doit être renseigné lorsqu'il existe.",
                )

                await cur.execute(
                    """
                    select artifact_type, count(*) as n
                    from ingestion_artifacts where ingestion_job_id=%s
                    group by artifact_type
                    """,
                    (job_id,),
                )
                artifact_counts = {r["artifact_type"]: int(r["n"]) for r in await cur.fetchall()}
                add(
                    "extraction_trace_preserved",
                    artifact_counts.get("extracted_text", 0) > 0,
                    True,
                    "Le texte extrait doit rester disponible pour le contrôle documentaire.",
                )
                add(
                    "structured_artifact_preserved",
                    artifact_counts.get("structured_json", 0) > 0,
                    True,
                    "Le paquet structuré soumis à validation doit être conservé.",
                )

                await cur.execute(
                    """
                    select count(*) as n from legal_reviews
                    where entity_type='document_version' and entity_id=%s
                      and workflow_status='validated'
                    """,
                    (row["document_version_id"],),
                ) if row["document_version_id"] else None
                validated_review = int((await cur.fetchone())["n"]) > 0 if row["document_version_id"] else False
                add(
                    "human_validation_recorded",
                    validated_review,
                    False,
                    "La validation humaine est enregistrée avant publication.",
                )

                blocking_pass = all(c["passed"] for c in checks if c["blocking"])
                can_validate = blocking_pass and row["status"] == "legal_review"
                can_publish = blocking_pass and row["status"] == "validated" and validated_review
                return {
                    "job_id": job_id,
                    "workflow_status": row["status"],
                    "can_validate": can_validate,
                    "can_publish": can_publish,
                    "checks": checks,
                }

    async def job_status(self, job_id: str) -> dict:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select j.*, s.source_key
                    from ingestion_jobs j join legal_sources s on s.id=j.source_id
                    where j.id=%s
                    """,
                    (job_id,),
                )
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                await cur.execute(
                    """
                    select artifact_type, storage_uri, content_hash, created_at
                    from ingestion_artifacts where ingestion_job_id=%s order by id
                    """,
                    (job_id,),
                )
                artifacts = list(await cur.fetchall())
                await cur.execute(
                    """
                    select from_status, to_status, actor_subject, note, occurred_at
                    from ingestion_job_events where ingestion_job_id=%s
                    order by occurred_at, id
                    """,
                    (job_id,),
                )
                events = list(await cur.fetchall())
                return {
                    "job_id": str(job["id"]),
                    "source_key": job["source_key"],
                    "source_url": job["source_url"],
                    "final_url": job.get("final_url"),
                    "status": job["status"],
                    "content_hash": job.get("content_hash"),
                    "mime_type": job.get("mime_type"),
                    "byte_size": job.get("byte_size"),
                    "created_at": job["created_at"],
                    "updated_at": job["updated_at"],
                    "artifacts": artifacts,
                    "events": events,
                }

    async def transition(self, job_id: str, target: str, actor: str, note: str | None = None) -> TransitionResult:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from ingestion_jobs where id=%s for update", (job_id,))
                job = await cur.fetchone()
                if not job:
                    raise ValueError("Ingestion job not found")
                current = job["status"]
                if not ingestion_transition_allowed(current, target):
                    raise ValueError(f"Workflow transition {current} -> {target} is not allowed")

                if target in {"sources_verified", "legal_review", "validated", "published"}:
                    await self._require_structured_versions(cur, job_id)

                if target == "sources_verified":
                    await self._require_source_provenance(cur, job_id)

                if target == "validated":
                    await self._require_source_provenance(cur, job_id)
                    await self._require_final_legal_status(cur, job_id)
                    await self._require_blocking_quality(cur, job_id)

                if target in {"sources_verified", "legal_review", "validated"}:
                    await self._set_reviews(cur, job_id, target, actor, note)

                if target == "published":
                    await self._require_source_provenance(cur, job_id)
                    await self._require_final_legal_status(cur, job_id)
                    await self._require_blocking_quality(cur, job_id)
                    await self._require_validation_review(cur, job_id)
                    await self._publish_versions(cur, job_id, actor, note)
                    await self._create_publication_receipt(cur, job_id, actor)
                    chunk_count = await rebuild_published_chunks(cur, job_id)
                    await self._audit(
                        cur,
                        actor,
                        "index_published_corpus",
                        "ingestion_job",
                        job_id,
                        {},
                        {"lexical_chunk_count": chunk_count},
                    )

                await cur.execute(
                    "update ingestion_jobs set status=%s, updated_at=now() where id=%s",
                    (target, job_id),
                )
                await self._event(cur, job_id, current, target, actor, note)
                await self._audit(
                    cur,
                    actor,
                    "transition_ingestion_job",
                    "ingestion_job",
                    job_id,
                    {"status": current},
                    {"status": target},
                )
                await conn.commit()
                return TransitionResult(job_id, current, target)

    async def _publish_versions(self, cur, job_id: str, actor: str, note: str | None) -> None:
        await cur.execute(
            "select id, document_id, status from legal_document_versions where ingestion_job_id=%s",
            (job_id,),
        )
        document_versions = list(await cur.fetchall())
        if not document_versions:
            raise ValueError("No structured document version is attached to this job")
        for dv in document_versions:
            await cur.execute(
                "update legal_document_versions set is_current=false where document_id=%s",
                (dv["document_id"],),
            )
            await cur.execute(
                "update legal_document_versions set is_current=true, published_at=now() where id=%s",
                (dv["id"],),
            )
            await cur.execute(
                "update legal_documents set current_status=%s, updated_at=now() where id=%s",
                (dv["status"], dv["document_id"]),
            )
            await self._review(cur, "document_version", dv["id"], "published", actor, note)

        await cur.execute(
            "select id, article_id from legal_article_versions where ingestion_job_id=%s",
            (job_id,),
        )
        article_versions = list(await cur.fetchall())
        for av in article_versions:
            await cur.execute(
                "update legal_article_versions set is_current=false where article_id=%s",
                (av["article_id"],),
            )
            await cur.execute(
                "update legal_article_versions set is_current=true where id=%s",
                (av["id"],),
            )
            await self._review(cur, "article_version", av["id"], "published", actor, note)

    async def _create_publication_receipt(self, cur, job_id: str, publisher: str) -> None:
        await cur.execute(
            """
            select dv.id as document_version_id, dv.version_key, dv.status, dv.official_text,
                   dv.valid_from, dv.valid_to, d.codo_id, j.content_hash as source_snapshot_hash
            from legal_document_versions dv
            join legal_documents d on d.id=dv.document_id
            join ingestion_jobs j on j.id=dv.ingestion_job_id
            where dv.ingestion_job_id=%s
            """,
            (job_id,),
        )
        documents = list(await cur.fetchall())
        if len(documents) != 1:
            raise ValueError("Publication receipt requires exactly one document version per ingestion job")
        document = documents[0]

        await cur.execute(
            """
            select a.codo_id, a.article_label, a.sort_order, av.status, av.official_text,
                   av.valid_from, av.valid_to
            from legal_article_versions av
            join legal_articles a on a.id=av.article_id
            where av.ingestion_job_id=%s
            order by a.sort_order, a.codo_id
            """,
            (job_id,),
        )
        articles = list(await cur.fetchall())

        await cur.execute(
            """
            select reviewer_subject
            from legal_reviews
            where entity_type='document_version'
              and entity_id=%s
              and workflow_status='validated'
              and reviewer_subject is not null
            order by reviewed_at desc nulls last, id desc
            limit 1
            """,
            (document["document_version_id"],),
        )
        validation = await cur.fetchone()
        if not validation or not validation["reviewer_subject"]:
            raise ValueError("Publication receipt requires an identified human validator")

        digest = publication_hash(document, articles, document["source_snapshot_hash"])
        await cur.execute(
            "select * from corpus_publication_receipts where ingestion_job_id=%s",
            (job_id,),
        )
        existing = await cur.fetchone()
        if existing:
            if (
                existing["publication_hash"] != digest
                or existing["source_snapshot_hash"] != document["source_snapshot_hash"]
                or existing["document_version_id"] != document["document_version_id"]
            ):
                raise ValueError("Existing publication receipt does not match the publication payload")
            return

        await cur.execute(
            """
            insert into corpus_publication_receipts(
              ingestion_job_id, document_version_id, document_codo_id, version_key,
              publication_hash, source_snapshot_hash, validator_subject, publisher_subject
            ) values (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                job_id,
                document["document_version_id"],
                document["codo_id"],
                document["version_key"],
                digest,
                document["source_snapshot_hash"],
                validation["reviewer_subject"],
                publisher,
            ),
        )
        await self._audit(
            cur,
            publisher,
            "create_publication_receipt",
            "document_version",
            str(document["document_version_id"]),
            {},
            {
                "document_codo_id": document["codo_id"],
                "version_key": document["version_key"],
                "publication_hash": digest,
                "source_snapshot_hash": document["source_snapshot_hash"],
            },
        )

    async def _require_blocking_quality(self, cur, job_id: str) -> None:
        await cur.execute(
            """
            select j.original_storage_uri, j.content_hash, s.trust_level, s.verified_at,
                   d.nature, d.title, dv.id as document_version_id, dv.version_key, dv.status
            from ingestion_jobs j
            join legal_sources s on s.id=j.source_id
            join legal_document_versions dv on dv.ingestion_job_id=j.id
            join legal_documents d on d.id=dv.document_id
            where j.id=%s
            """,
            (job_id,),
        )
        rows = list(await cur.fetchall())
        if len(rows) != 1:
            raise ValueError("Quality gate requires exactly one structured document version")
        row = rows[0]

        await cur.execute(
            "select artifact_type, count(*) as n from ingestion_artifacts where ingestion_job_id=%s group by artifact_type",
            (job_id,),
        )
        artifacts = {r["artifact_type"]: int(r["n"]) for r in await cur.fetchall()}

        await cur.execute(
            "select count(*) as n, count(*) filter (where status='verification_pending') as pending from legal_article_versions where ingestion_job_id=%s",
            (job_id,),
        )
        article_counts = await cur.fetchone()

        await cur.execute(
            """
            select ss.content_hash as snapshot_hash, s.trust_level, s.verified_at
            from legal_version_sources lvs
            join source_snapshots ss on ss.id=lvs.source_snapshot_id
            join legal_sources s on s.id=ss.source_id
            where lvs.document_version_id=%s
            """,
            (row["document_version_id"],),
        )
        provenance = list(await cur.fetchall())
        matching = [p for p in provenance if p["snapshot_hash"] == row["content_hash"] and p["verified_at"] is not None]
        provenance_sufficient = bool(matching) and source_set_is_sufficient([p["trust_level"] for p in matching])
        original = Path(row["original_storage_uri"] or "")
        normative = (row["nature"] or "").strip().lower() in {
            "constitution", "loi", "code", "ordonnance", "décret", "decret", "acte uniforme"
        }
        failures = blocking_quality_failures(
            original_preserved=bool(row["original_storage_uri"] and original.exists() and original.is_file()),
            source_registry_verified=row["verified_at"] is not None and row["trust_level"] in {"A", "B", "C"},
            core_metadata_present=bool(row["title"] and row["version_key"]),
            document_status_final=row["status"] != "verification_pending",
            extraction_trace_preserved=artifacts.get("extracted_text", 0) > 0,
            structured_artifact_preserved=artifacts.get("structured_json", 0) > 0,
            normative=normative,
            article_count=int(article_counts["n"] or 0),
            pending_article_count=int(article_counts["pending"] or 0),
            provenance_sufficient=provenance_sufficient,
        )
        if failures:
            raise ValueError("Blocking quality gate failed: " + ", ".join(failures))

    async def _require_source_provenance(self, cur, job_id: str) -> None:
        await cur.execute(
            """
            select j.content_hash, lvs.document_version_id, ss.content_hash as snapshot_hash,
                   s.trust_level, s.verified_at
            from ingestion_jobs j
            join legal_document_versions dv on dv.ingestion_job_id=j.id
            join legal_version_sources lvs on lvs.document_version_id=dv.id
            join source_snapshots ss on ss.id=lvs.source_snapshot_id
            join legal_sources s on s.id=ss.source_id
            where j.id=%s
            """,
            (job_id,),
        )
        rows = list(await cur.fetchall())
        if not rows:
            raise ValueError("No source provenance is linked to this legal version")
        matching = [r for r in rows if r["snapshot_hash"] == r["content_hash"]]
        levels = [r["trust_level"] for r in matching if r["verified_at"] is not None]
        if not matching or not source_set_is_sufficient(levels):
            raise ValueError("Source provenance does not meet CODO verification requirements")

    async def _require_final_legal_status(self, cur, job_id: str) -> None:
        await cur.execute(
            """
            select count(*) as n from legal_document_versions
            where ingestion_job_id=%s and status='verification_pending'
            """,
            (job_id,),
        )
        pending_documents = int((await cur.fetchone())["n"])
        await cur.execute(
            """
            select count(*) as n from legal_article_versions
            where ingestion_job_id=%s and status='verification_pending'
            """,
            (job_id,),
        )
        pending_articles = int((await cur.fetchone())["n"])
        if pending_documents or pending_articles:
            raise ValueError(
                "Legal status decision is required before validation; verification_pending cannot be published"
            )

    async def _require_validation_review(self, cur, job_id: str) -> None:
        await cur.execute(
            """
            select count(*) as n
            from legal_document_versions dv
            where dv.ingestion_job_id=%s
              and exists (
                select 1 from legal_reviews r
                where r.entity_type='document_version'
                  and r.entity_id=dv.id
                  and r.workflow_status='validated'
              )
            """,
            (job_id,),
        )
        if int((await cur.fetchone())["n"]) < 1:
            raise ValueError("A human validation record is required before publication")

    async def _set_reviews(self, cur, job_id: str, status: str, actor: str, note: str | None) -> None:
        await cur.execute("select id from legal_document_versions where ingestion_job_id=%s", (job_id,))
        for row in await cur.fetchall():
            await self._review(cur, "document_version", row["id"], status, actor, note)
        await cur.execute("select id from legal_article_versions where ingestion_job_id=%s", (job_id,))
        for row in await cur.fetchall():
            await self._review(cur, "article_version", row["id"], status, actor, note)

    async def _require_structured_versions(self, cur, job_id: str) -> None:
        await cur.execute(
            "select count(*) as n from legal_document_versions where ingestion_job_id=%s",
            (job_id,),
        )
        if int((await cur.fetchone())["n"]) < 1:
            raise ValueError("The ingestion job has no structured legal document version")

    async def _review(
        self,
        cur,
        entity_type: str,
        entity_id: int,
        status: str,
        actor: str,
        note: str | None = None,
    ) -> None:
        await cur.execute(
            """
            insert into legal_reviews(
              entity_type, entity_id, workflow_status, reviewer_subject, review_note, reviewed_at
            ) values (%s,%s,%s,%s,%s,now())
            """,
            (entity_type, entity_id, status, actor, note),
        )

    async def _event(
        self,
        cur,
        job_id: str,
        current: str | None,
        target: str,
        actor: str,
        note: str | None,
    ) -> None:
        await cur.execute(
            """
            insert into ingestion_job_events(
              ingestion_job_id, from_status, to_status, actor_subject, note
            ) values (%s,%s,%s,%s,%s)
            """,
            (job_id, current, target, actor, note),
        )

    async def _audit(
        self,
        cur,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        previous: dict,
        new: dict,
    ) -> None:
        await cur.execute(
            """
            insert into audit_logs(
              actor_subject, action, entity_type, entity_id, previous_data, new_data
            ) values (%s,%s,%s,%s,%s::jsonb,%s::jsonb)
            """,
            (actor, action, entity_type, entity_id, json.dumps(previous), json.dumps(new)),
        )
