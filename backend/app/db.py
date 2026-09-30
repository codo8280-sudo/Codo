from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from .config import settings

_pool: Any | None = None


async def open_pool() -> None:
    global _pool
    if not settings.database_configured:
        return
    if _pool is None:
        try:
            from psycopg.rows import dict_row
            from psycopg_pool import AsyncConnectionPool
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL support requires psycopg[binary,pool]. Install backend/requirements.txt."
            ) from exc
        _pool = AsyncConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=8,
            open=False,
            kwargs={"row_factory": dict_row},
        )
    await _pool.open()


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def pool():
    if _pool is None:
        raise RuntimeError("CODO_DATABASE_URL is not configured or the PostgreSQL pool is not open.")
    return _pool


@asynccontextmanager
async def connection():
    async with pool().connection() as conn:
        yield conn


async def database_ready() -> tuple[bool, str]:
    if not settings.database_configured:
        return False, "database-not-configured"
    try:
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select 1 as ok")
                row = await cur.fetchone()
                if not row or int(row["ok"]) != 1:
                    return False, "database-invalid-response"
    except Exception as exc:
        return False, f"database-unavailable:{exc.__class__.__name__}"
    return True, "database-ready"
