from __future__ import annotations

import json
from uuid import uuid4

from ..db import connection
from ..schemas import RelationshipCandidateIn


class LegalRelationshipService:
    async def create_candidate(self, request: RelationshipCandidateIn, actor: str) -> dict:
        if request.from_document_codo_id == request.to_document_codo_id:
            raise ValueError("A legal relationship cannot point a document to itself")

        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select source_key, trust_level, verified_at
                    from legal_sources
                    where source_key=%s and active=true
                    """,
                    (request.evidence_source_key,),
                )
                source = await cur.fetchone()
                if not source:
                    raise ValueError("Evidence source is not registered or active")
                if source["trust_level"] not in {"A", "B", "C"} or source["verified_at"] is None:
                    raise ValueError("Evidence source is not sufficiently verified")

                await cur.execute(
                    """
                    select * from legal_relationship_candidates
                    where from_document_codo_id=%s
                      and relation_type=%s
                      and to_document_codo_id=%s
                      and evidence_source_key=%s
                    for update
                    """,
                    (
                        request.from_document_codo_id,
                        request.relation_type,
                        request.to_document_codo_id,
                        request.evidence_source_key,
                    ),
                )
                existing = await cur.fetchone()
                if existing and existing["status"] != "pending":
                    raise ValueError("A reviewed relationship candidate is immutable")

                if existing:
                    await cur.execute(
                        """
                        update legal_relationship_candidates
                        set effective_date=%s, evidence_url=%s, note=%s,
                            created_by=%s, created_at=now()
                        where id=%s
                        returning *
                        """,
                        (
                            request.effective_date,
                            str(request.evidence_url) if request.evidence_url else None,
                            request.note,
                            actor,
                            existing["id"],
                        ),
                    )
                else:
                    await cur.execute(
                        """
                        insert into legal_relationship_candidates(
                          id, from_document_codo_id, relation_type, to_document_codo_id,
                          effective_date, evidence_source_key, evidence_url, note, created_by
                        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        returning *
                        """,
                        (
                            str(uuid4()),
                            request.from_document_codo_id,
                            request.relation_type,
                            request.to_document_codo_id,
                            request.effective_date,
                            request.evidence_source_key,
                            str(request.evidence_url) if request.evidence_url else None,
                            request.note,
                            actor,
                        ),
                    )
                row = await cur.fetchone()
                await cur.execute(
                    """
                    insert into audit_logs(actor_subject, action, entity_type, entity_id, previous_data, new_data)
                    values (%s,'create_relationship_candidate','legal_relationship_candidate',%s,null,%s::jsonb)
                    """,
                    (
                        actor,
                        str(row["id"]),
                        json.dumps(
                            {
                                "from_document_codo_id": row["from_document_codo_id"],
                                "relation_type": row["relation_type"],
                                "to_document_codo_id": row["to_document_codo_id"],
                                "evidence_source_key": row["evidence_source_key"],
                                "status": row["status"],
                            }
                        ),
                    ),
                )
                await conn.commit()
                return self._candidate_dict(row)

    async def list_candidates(self, status_filter: str | None = None) -> list[dict]:
        async with connection() as conn:
            async with conn.cursor() as cur:
                if status_filter:
                    await cur.execute(
                        """
                        select * from legal_relationship_candidates
                        where status=%s order by created_at desc, id
                        """,
                        (status_filter,),
                    )
                else:
                    await cur.execute(
                        """
                        select * from legal_relationship_candidates
                        order by created_at desc, id
                        """
                    )
                return [self._candidate_dict(row) for row in await cur.fetchall()]

    async def review_candidate(self, candidate_id: str, approved: bool, actor: str, note: str | None) -> dict:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "select * from legal_relationship_candidates where id=%s for update",
                    (candidate_id,),
                )
                candidate = await cur.fetchone()
                if not candidate:
                    raise ValueError("Relationship candidate not found")
                if candidate["status"] != "pending":
                    raise ValueError("Only a pending relationship candidate can be reviewed")

                relationship_id = None
                if approved:
                    await cur.execute(
                        "select id from legal_documents where codo_id=%s",
                        (candidate["from_document_codo_id"],),
                    )
                    from_doc = await cur.fetchone()
                    await cur.execute(
                        "select id from legal_documents where codo_id=%s",
                        (candidate["to_document_codo_id"],),
                    )
                    to_doc = await cur.fetchone()
                    if not from_doc or not to_doc:
                        raise ValueError("Both legal documents must be ingested before validating the relationship")

                    await cur.execute(
                        """
                        select id, trust_level, verified_at from legal_sources
                        where source_key=%s and active=true
                        """,
                        (candidate["evidence_source_key"],),
                    )
                    source = await cur.fetchone()
                    if not source or source["trust_level"] not in {"A", "B"} or source["verified_at"] is None:
                        raise ValueError("Validated legal relationships require verified A or B evidence")

                    await cur.execute(
                        """
                        select id from legal_relationships
                        where from_document_id=%s
                          and relation_type=%s
                          and to_document_id=%s
                          and effective_date is not distinct from %s
                          and from_article_id is null
                          and to_article_id is null
                        limit 1
                        """,
                        (
                            from_doc["id"],
                            candidate["relation_type"],
                            to_doc["id"],
                            candidate["effective_date"],
                        ),
                    )
                    existing_relationship = await cur.fetchone()
                    if existing_relationship:
                        relationship_id = existing_relationship["id"]
                    else:
                        await cur.execute(
                            """
                            insert into legal_relationships(
                              from_document_id, relation_type, to_document_id,
                              effective_date, evidence_source_id, note
                            ) values (%s,%s,%s,%s,%s,%s)
                            returning id
                            """,
                            (
                                from_doc["id"],
                                candidate["relation_type"],
                                to_doc["id"],
                                candidate["effective_date"],
                                source["id"],
                                note or candidate["note"],
                            ),
                        )
                        relationship_id = (await cur.fetchone())["id"]

                    await cur.execute(
                        """
                        insert into legal_relationship_evidence(
                          relationship_id, source_id, candidate_id, evidence_url, note
                        ) values (%s,%s,%s,%s,%s)
                        on conflict (candidate_id) do update set
                          relationship_id=excluded.relationship_id,
                          source_id=excluded.source_id,
                          evidence_url=excluded.evidence_url,
                          note=excluded.note,
                          linked_at=now()
                        """,
                        (
                            relationship_id,
                            source["id"],
                            candidate["id"],
                            candidate["evidence_url"],
                            note or candidate["note"],
                        ),
                    )

                new_status = "validated" if approved else "rejected"
                await cur.execute(
                    """
                    update legal_relationship_candidates
                    set status=%s, reviewed_by=%s, reviewed_at=now(), review_note=%s, relationship_id=%s
                    where id=%s
                    returning *
                    """,
                    (new_status, actor, note, relationship_id, candidate_id),
                )
                row = await cur.fetchone()
                event_type = "relationship_validated" if approved else "relationship_rejected"
                await cur.execute(
                    """
                    insert into admin_security_events(actor_subject, event_type, metadata)
                    values (%s,%s,%s::jsonb)
                    """,
                    (
                        actor,
                        event_type,
                        json.dumps(
                            {
                                "candidate_id": candidate_id,
                                "relationship_id": relationship_id,
                                "from_document_codo_id": row["from_document_codo_id"],
                                "to_document_codo_id": row["to_document_codo_id"],
                                "relation_type": row["relation_type"],
                            }
                        ),
                    ),
                )
                await cur.execute(
                    """
                    insert into audit_logs(actor_subject, action, entity_type, entity_id, previous_data, new_data)
                    values (%s,%s,'legal_relationship_candidate',%s,%s::jsonb,%s::jsonb)
                    """,
                    (
                        actor,
                        event_type,
                        candidate_id,
                        json.dumps({"status": "pending"}),
                        json.dumps({"status": new_status, "relationship_id": relationship_id}),
                    ),
                )
                await conn.commit()
                return self._candidate_dict(row)

    async def public_relationships(self, codo_id: str) -> list[dict]:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select r.id,
                           fd.codo_id as from_document_codo_id,
                           fa.codo_id as from_article_codo_id,
                           r.relation_type,
                           td.codo_id as to_document_codo_id,
                           ta.codo_id as to_article_codo_id,
                           r.effective_date,
                           s.source_key as evidence_source_key,
                           s.name as evidence_source_name,
                           r.note
                    from legal_relationships r
                    left join legal_documents fd on fd.id=r.from_document_id
                    left join legal_articles fa on fa.id=r.from_article_id
                    left join legal_documents td on td.id=r.to_document_id
                    left join legal_articles ta on ta.id=r.to_article_id
                    left join legal_sources s on s.id=r.evidence_source_id
                    where fd.codo_id=%s or td.codo_id=%s
                    order by r.effective_date nulls last, r.id
                    """,
                    (codo_id, codo_id),
                )
                return [dict(row) for row in await cur.fetchall()]

    @staticmethod
    def _candidate_dict(row: dict) -> dict:
        data = dict(row)
        data["id"] = str(data["id"])
        return data
