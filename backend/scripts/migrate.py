from __future__ import annotations

import hashlib
from pathlib import Path

from app.config import settings


def migration_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> None:
    if not settings.database_configured:
        raise SystemExit("CODO_DATABASE_URL is required for migrations")
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("Install backend/requirements.txt before running migrations") from exc

    root = Path(__file__).resolve().parents[1] / "postgres"
    migrations = sorted(root.glob("*.sql"))
    if not migrations:
        raise SystemExit("No SQL migrations found")

    applied = 0
    skipped = 0
    with psycopg.connect(settings.database_url, autocommit=True, row_factory=dict_row) as conn:
        conn.execute(
            """
            create table if not exists codo_schema_migrations (
              migration_name text primary key,
              content_hash text not null,
              applied_at timestamptz not null default now()
            )
            """
        )
        for path in migrations:
            content_hash = migration_hash(path)
            existing = conn.execute(
                "select content_hash from codo_schema_migrations where migration_name=%s",
                (path.name,),
            ).fetchone()
            if existing:
                if existing["content_hash"] != content_hash:
                    raise SystemExit(
                        f"Migration checksum mismatch for {path.name}. Historical migrations must never be edited."
                    )
                print(f"skipping={path.name} checksum=verified")
                skipped += 1
                continue

            print(f"applying={path.name}")
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute(
                "insert into codo_schema_migrations(migration_name, content_hash) values (%s,%s)",
                (path.name, content_hash),
            )
            applied += 1

    print(f"migrations_applied={applied}")
    print(f"migrations_skipped={skipped}")


if __name__ == "__main__":
    run()
