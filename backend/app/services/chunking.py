from __future__ import annotations

import hashlib


def split_text(text: str, target_chars: int = 1800, overlap_chars: int = 240) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + target_chars)
        if end < len(normalized):
            pivot = normalized.rfind(" ", start + target_chars // 2, end)
            if pivot > start:
                end = pivot
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


async def rebuild_published_chunks(cur, job_id: str) -> int:
    """Create lexical chunks for article versions published by one ingestion job.

    This function does not create embeddings. It guarantees that every newly
    published article can participate in lexical retrieval immediately.
    """
    await cur.execute(
        """
        select av.id as article_version_id, av.document_version_id, av.official_text,
               d.source_id
        from legal_article_versions av
        join legal_articles a on a.id = av.article_id
        join legal_documents d on d.id = a.document_id
        where av.ingestion_job_id=%s
        order by av.id
        """,
        (job_id,),
    )
    rows = list(await cur.fetchall())
    created = 0
    for row in rows:
        await cur.execute("delete from legal_chunks where article_version_id=%s", (row["article_version_id"],))
        for index, chunk in enumerate(split_text(row["official_text"])):
            digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            await cur.execute(
                """
                insert into legal_chunks(
                  document_version_id, article_version_id, source_id,
                  chunk_index, chunk_text, content_hash
                ) values (%s,%s,%s,%s,%s,%s)
                """,
                (
                    row["document_version_id"], row["article_version_id"], row["source_id"],
                    index, chunk, digest,
                ),
            )
            created += 1
    return created
