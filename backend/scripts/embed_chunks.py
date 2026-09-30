from __future__ import annotations

import argparse
import asyncio

from app.config import settings
from app.db import close_pool, connection, open_pool
from app.providers.embeddings import build_embedding_provider


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.9g}" for value in values) + "]"


async def run(limit: int) -> None:
    if not settings.semantic_search_configured:
        raise SystemExit("Configure CODO_EMBEDDING_URL and CODO_EMBEDDING_MODEL first.")
    provider = build_embedding_provider()
    await open_pool()
    embedded = 0
    try:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select id, chunk_text from legal_chunks
                    where embedding_model is distinct from %s or embedding_model is null
                    order by id
                    limit %s
                    """,
                    (settings.embedding_model, limit),
                )
                rows = list(await cur.fetchall())
                for row in rows:
                    values = await provider.embed(row["chunk_text"])
                    if not values:
                        continue
                    await cur.execute(
                        """
                        update legal_chunks
                        set embedding=cast(%s as vector), embedding_model=%s,
                            embedding_dimensions=%s, updated_at=now()
                        where id=%s
                        """,
                        (vector_literal(values), settings.embedding_model, len(values), row["id"]),
                    )
                    embedded += 1
                await conn.commit()
    finally:
        await close_pool()
    print(f"embedded_chunks={embedded}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    asyncio.run(run(args.limit))
