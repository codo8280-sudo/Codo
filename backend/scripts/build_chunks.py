from __future__ import annotations

import argparse
import asyncio
import hashlib

from app.db import close_pool, connection, open_pool
from app.services.chunking import split_text



async def run(limit: int) -> None:
    await open_pool()
    try:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select av.id as article_version_id, av.document_version_id, av.official_text,
                           d.source_id
                    from legal_article_versions av
                    join legal_articles a on a.id = av.article_id
                    join legal_documents d on d.id = a.document_id
                    where exists (
                      select 1 from legal_reviews r
                      where r.entity_type='article_version'
                        and r.entity_id=av.id
                        and r.workflow_status='published'
                    )
                    order by av.id
                    limit %s
                    """,
                    (limit,),
                )
                rows = list(await cur.fetchall())
                for row in rows:
                    chunks = split_text(row["official_text"])
                    for index, chunk in enumerate(chunks):
                        digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                        await cur.execute(
                            """
                            insert into legal_chunks(
                              document_version_id, article_version_id, source_id,
                              chunk_index, chunk_text, content_hash
                            ) values (%s,%s,%s,%s,%s,%s)
                            on conflict (article_version_id, chunk_index, content_hash)
                            do update set chunk_text=excluded.chunk_text, updated_at=now()
                            """,
                            (
                                row["document_version_id"], row["article_version_id"], row["source_id"],
                                index, chunk, digest,
                            ),
                        )
                await conn.commit()
                print(f"chunked_article_versions={len(rows)}")
    finally:
        await close_pool()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10000)
    args = parser.parse_args()
    asyncio.run(run(args.limit))
