from __future__ import annotations

from typing import Any

from ..db import connection


_PUBLISHED_ARTICLE = """
exists (
  select 1 from legal_reviews r
  where r.entity_type = 'article_version'
    and r.entity_id = av.id
    and r.workflow_status = 'published'
)
"""

_PUBLISHED_DOCUMENT = """
exists (
  select 1 from legal_reviews r
  where r.entity_type = 'document_version'
    and r.entity_id = dv.id
    and r.workflow_status = 'published'
)
"""


class LegalRepository:
    async def lexical_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        statement = f"""
        with article_hits as (
          select
            d.id as document_pk,
            d.codo_id as document_codo_id,
            d.title,
            d.nature,
            d.document_number,
            d.current_status,
            d.authority_name,
            d.adoption_date,
            d.publication_date,
            dv.id as document_version_pk,
            dv.version_key,
            dv.valid_from as effective_date,
            a.id as article_pk,
            a.codo_id as article_codo_id,
            a.article_label,
            av.id as article_version_pk,
            av.official_text,
            av.status as article_status,
            av.valid_from,
            av.valid_to,
            av.explanation_codo,
            av.short_summary,
            s.id as source_pk,
            s.name as source_name,
            s.institution_name,
            s.trust_level,
            s.official_url,
            s.is_official,
            s.probative_note,
            s.verified_at,
            ts_rank_cd(av.search_text, websearch_to_tsquery('french', %s)) as lexical_score,
            replace(replace(ts_headline('french', av.official_text, websearch_to_tsquery('french', %s),
              'MaxFragments=2, MaxWords=28, MinWords=10'), '<b>', ''), '</b>', '') as snippet
          from legal_article_versions av
          join legal_articles a on a.id = av.article_id
          join legal_documents d on d.id = a.document_id
          join legal_document_versions dv on dv.id = av.document_version_id
          join legal_sources s on s.id = d.source_id
          where av.is_current = true
            and dv.is_current = true
            and s.verified_at is not null
            and s.trust_level in ('A','B','C')
            and av.search_text @@ websearch_to_tsquery('french', %s)
            and {_PUBLISHED_ARTICLE}
            and {_PUBLISHED_DOCUMENT}
        ), document_hits as (
          select
            d.id as document_pk,
            d.codo_id as document_codo_id,
            d.title,
            d.nature,
            d.document_number,
            d.current_status,
            d.authority_name,
            d.adoption_date,
            d.publication_date,
            dv.id as document_version_pk,
            dv.version_key,
            dv.valid_from as effective_date,
            null::bigint as article_pk,
            null::text as article_codo_id,
            null::text as article_label,
            null::bigint as article_version_pk,
            null::text as official_text,
            null::text as article_status,
            null::date as valid_from,
            null::date as valid_to,
            null::text as explanation_codo,
            null::text as short_summary,
            s.id as source_pk,
            s.name as source_name,
            s.institution_name,
            s.trust_level,
            s.official_url,
            s.is_official,
            s.probative_note,
            s.verified_at,
            ts_rank_cd(d.search_text, websearch_to_tsquery('french', %s)) as lexical_score,
            d.title as snippet
          from legal_documents d
          join legal_document_versions dv on dv.document_id = d.id and dv.is_current = true
          join legal_sources s on s.id = d.source_id
          where s.verified_at is not null
            and s.trust_level in ('A','B','C')
            and d.search_text @@ websearch_to_tsquery('french', %s)
            and {_PUBLISHED_DOCUMENT}
        )
        select * from (
          select * from article_hits
          union all
          select * from document_hits
        ) x
        order by lexical_score desc, document_codo_id, article_codo_id nulls first
        limit %s
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (query, query, query, query, query, limit))
                return list(await cur.fetchall())

    async def semantic_search(
        self,
        embedding: list[float],
        embedding_model: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        vector_literal = "[" + ",".join(f"{value:.9g}" for value in embedding) + "]"
        statement = f"""
        select
          d.id as document_pk,
          d.codo_id as document_codo_id,
          d.title,
          d.nature,
          d.document_number,
          d.current_status,
          d.authority_name,
          d.adoption_date,
          d.publication_date,
          dv.id as document_version_pk,
          dv.version_key,
          dv.valid_from as effective_date,
          a.id as article_pk,
          a.codo_id as article_codo_id,
          a.article_label,
          av.id as article_version_pk,
          av.official_text,
          av.status as article_status,
          av.valid_from,
          av.valid_to,
          av.explanation_codo,
          av.short_summary,
          s.id as source_pk,
          s.name as source_name,
          s.institution_name,
          s.trust_level,
          s.official_url,
          s.is_official,
          s.probative_note,
          s.verified_at,
          1 - (lc.embedding <=> cast(%s as vector)) as semantic_score,
          lc.chunk_text as snippet
        from legal_chunks lc
        join legal_article_versions av on av.id = lc.article_version_id
        join legal_articles a on a.id = av.article_id
        join legal_documents d on d.id = a.document_id
        join legal_document_versions dv on dv.id = av.document_version_id
        join legal_sources s on s.id = lc.source_id
        where lc.embedding is not null
          and lc.embedding_model = %s
          and lc.embedding_dimensions = %s
          and av.is_current = true
          and dv.is_current = true
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and {_PUBLISHED_ARTICLE}
          and {_PUBLISHED_DOCUMENT}
        order by lc.embedding <=> cast(%s as vector)
        limit %s
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    statement,
                    (vector_literal, embedding_model, len(embedding), vector_literal, limit),
                )
                return list(await cur.fetchall())

    async def document_by_codo_id(self, codo_id: str) -> dict[str, Any] | None:
        statement = f"""
        select d.*, dv.id as document_version_pk, dv.version_key, dv.valid_from as effective_date,
               s.id as source_pk, s.name as source_name, s.institution_name, s.trust_level,
               s.official_url, s.is_official, s.probative_note, s.verified_at
        from legal_documents d
        join legal_document_versions dv on dv.document_id = d.id and dv.is_current = true
        join legal_sources s on s.id = d.source_id
        where d.codo_id = %s
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and {_PUBLISHED_DOCUMENT}
        limit 1
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (codo_id,))
                return await cur.fetchone()

    async def article_by_codo_id(self, codo_id: str) -> dict[str, Any] | None:
        statement = f"""
        select d.codo_id as document_codo_id, d.title, d.nature, d.document_number,
               d.current_status, d.authority_name, d.adoption_date, d.publication_date,
               dv.version_key, dv.valid_from as effective_date,
               a.codo_id as article_codo_id, a.article_label,
               av.id as article_version_pk, av.official_text, av.status as article_status,
               av.valid_from, av.valid_to, av.explanation_codo, av.short_summary,
               s.id as source_pk, s.name as source_name, s.institution_name, s.trust_level,
               s.official_url, s.is_official, s.probative_note, s.verified_at
        from legal_articles a
        join legal_article_versions av on av.article_id = a.id and av.is_current = true
        join legal_documents d on d.id = a.document_id
        join legal_document_versions dv on dv.id = av.document_version_id and dv.is_current = true
        join legal_sources s on s.id = d.source_id
        where a.codo_id = %s
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and {_PUBLISHED_ARTICLE}
          and {_PUBLISHED_DOCUMENT}
        limit 1
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (codo_id,))
                return await cur.fetchone()

    async def document_provenance(self, codo_id: str) -> list[dict[str, Any]]:
        statement = f"""
        select d.codo_id as document_codo_id, dv.version_key,
               s.id as source_pk, s.name as source_name, s.institution_name,
               s.trust_level, s.verified_at, lvs.provenance_role, lvs.note,
               ss.source_url, ss.final_url, ss.captured_at, ss.content_hash
        from legal_documents d
        join legal_document_versions dv on dv.document_id=d.id and dv.is_current=true
        join legal_version_sources lvs on lvs.document_version_id=dv.id
        join source_snapshots ss on ss.id=lvs.source_snapshot_id
        join legal_sources s on s.id=ss.source_id
        where d.codo_id=%s
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and {_PUBLISHED_DOCUMENT}
        order by case lvs.provenance_role
          when 'primary_text' then 1
          when 'amendment' then 2
          when 'verification' then 3
          else 4 end,
          ss.captured_at desc
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (codo_id,))
                return list(await cur.fetchall())

    async def document_publication_receipt(self, codo_id: str) -> dict[str, Any] | None:
        statement = f"""
        select r.document_codo_id as document_id, r.version_key, r.publication_hash,
               r.source_snapshot_hash, r.published_at
        from corpus_publication_receipts r
        join legal_document_versions dv on dv.id=r.document_version_id
        join legal_documents d on d.id=dv.document_id
        where d.codo_id=%s
          and dv.is_current=true
          and {_PUBLISHED_DOCUMENT}
        order by r.published_at desc
        limit 1
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (codo_id,))
                return await cur.fetchone()

    async def article_versions(self, codo_id: str) -> list[dict[str, Any]]:
        statement = """
        select dv.version_key, av.status, av.official_text, av.valid_from, av.valid_to, av.is_current
        from legal_articles a
        join legal_article_versions av on av.article_id = a.id
        join legal_document_versions dv on dv.id = av.document_version_id
        join legal_sources s on s.id = (select source_id from legal_documents where id = a.document_id)
        where a.codo_id = %s
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and exists (
            select 1 from legal_reviews r
            where r.entity_type = 'article_version'
              and r.entity_id = av.id
              and r.workflow_status = 'published'
          )
        order by coalesce(av.valid_from, date '0001-01-01') desc, av.id desc
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (codo_id,))
                return list(await cur.fetchall())

    async def verify_evidence(self, evidence_ids: list[int]) -> list[dict[str, Any]]:
        if not evidence_ids:
            return []
        statement = """
        select av.id as article_version_pk, a.id as article_pk, a.codo_id as article_codo_id,
               d.id as document_pk, d.codo_id as document_codo_id, dv.id as document_version_pk,
               dv.version_key, s.id as source_pk, s.trust_level, s.official_url,
               s.name as source_name, s.verified_at
        from legal_article_versions av
        join legal_articles a on a.id = av.article_id
        join legal_documents d on d.id = a.document_id
        join legal_document_versions dv on dv.id = av.document_version_id
        join legal_sources s on s.id = d.source_id
        where av.id = any(%s)
          and av.is_current = true
          and dv.is_current = true
          and s.verified_at is not null
          and s.trust_level in ('A','B','C')
          and exists (
            select 1 from legal_reviews r
            where r.entity_type = 'article_version'
              and r.entity_id = av.id
              and r.workflow_status = 'published'
          )
          and exists (
            select 1 from legal_reviews r
            where r.entity_type = 'document_version'
              and r.entity_id = dv.id
              and r.workflow_status = 'published'
          )
        """
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(statement, (evidence_ids,))
                return list(await cur.fetchall())

    async def save_answer(self, question: str, answer_json: str, sufficient: bool, citations: list[dict[str, Any]]) -> int:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "insert into ai_answers(question_text, answer_text, has_sufficient_verified_sources) values (%s,%s,%s) returning id",
                    (question, answer_json, sufficient),
                )
                row = await cur.fetchone()
                answer_id = int(row["id"])
                for order, citation in enumerate(citations, start=1):
                    await cur.execute(
                        """
                        insert into citations(ai_answer_id, source_id, document_id, document_version_id, article_id, article_version_id, citation_order)
                        values (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            answer_id,
                            citation["source_pk"],
                            citation["document_pk"],
                            citation["document_version_pk"],
                            citation.get("article_pk"),
                            citation.get("article_version_pk"),
                            order,
                        ),
                    )
                await conn.commit()
                return answer_id
