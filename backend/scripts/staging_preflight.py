from __future__ import annotations

import asyncio
from pathlib import Path

from app.auth import AuthenticationError, oidc_authenticator
from app.config import settings

POSTGRES_DIR = Path(__file__).resolve().parents[1] / "postgres"

EXPECTED_TABLES = {
    "legal_documents",
    "legal_document_versions",
    "legal_articles",
    "legal_article_versions",
    "legal_relationship_candidates",
    "admin_memberships",
    "admin_security_events",
    "codo_schema_migrations",
    "user_profiles",
    "user_accessibility_settings",
    "user_favorites",
    "privacy_events",
    "corpus_publication_receipts",
    "staging_release_runs",
    "staging_release_checks",
}


async def _check_oidc() -> tuple[bool, str]:
    if not settings.oidc_configured:
        if settings.admin_bootstrap_token:
            return True, "OIDC not configured; bootstrap recovery is enabled"
        return False, "Neither OIDC nor bootstrap administrative authentication is configured"
    try:
        metadata = await oidc_authenticator._get_metadata()
        jwks = await oidc_authenticator._get_jwks()
    except AuthenticationError as exc:
        return False, f"OIDC discovery/JWKS check failed: {exc}"
    return True, f"OIDC issuer verified; jwks_keys={len(jwks.get('keys', []))}; issuer={metadata.get('issuer')}"


def main() -> int:
    failures: list[str] = []
    notes: list[str] = []

    storage = Path(settings.storage_dir)
    try:
        storage.mkdir(parents=True, exist_ok=True)
        probe = storage / ".preflight-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        notes.append(f"storage=ok path={storage}")
    except OSError as exc:
        failures.append(f"storage=failed error={exc}")

    if not settings.database_configured:
        failures.append("database=not-configured")
    else:
        try:
            import psycopg
        except ImportError:
            failures.append("database=psycopg-not-installed")
        else:
            try:
                with psycopg.connect(settings.database_url) as conn:
                    tables = {
                        row[0]
                        for row in conn.execute(
                            "select table_name from information_schema.tables where table_schema=current_schema()"
                        ).fetchall()
                    }
                    missing = sorted(EXPECTED_TABLES.difference(tables))
                    if missing:
                        failures.append("database=missing-tables:" + ",".join(missing))
                    else:
                        notes.append("database=schema-ok")

                    expected_migrations = {path.name for path in POSTGRES_DIR.glob("*.sql")}
                    applied_migrations = {
                        row[0]
                        for row in conn.execute(
                            "select migration_name from codo_schema_migrations"
                        ).fetchall()
                    }
                    missing_migrations = sorted(expected_migrations.difference(applied_migrations))
                    unexpected_migrations = sorted(applied_migrations.difference(expected_migrations))
                    if missing_migrations:
                        failures.append("database=missing-migrations:" + ",".join(missing_migrations))
                    else:
                        notes.append(f"database=migrations-ok:{len(expected_migrations)}")
                    if unexpected_migrations:
                        failures.append("database=unknown-migrations:" + ",".join(unexpected_migrations))

                    identity_index = conn.execute(
                        "select to_regclass('uq_user_profiles_issuer_subject') is not null"
                    ).fetchone()[0]
                    if not identity_index:
                        failures.append("database=missing-oidc-issuer-subject-unique-index")
                    else:
                        notes.append("database=oidc-subject-namespace-ok")

                    super_admins = conn.execute(
                        "select count(*) from admin_memberships where role_key='SUPER_ADMIN' and active=true"
                    ).fetchone()[0]
                    if super_admins == 0 and not settings.admin_bootstrap_token:
                        failures.append("admin=no-active-super-admin-and-no-bootstrap-recovery")
                    else:
                        notes.append(f"admin=super-admins:{super_admins}")
            except Exception as exc:
                failures.append(f"database=connection-or-query-failed:{exc}")

    oidc_ok, oidc_note = asyncio.run(_check_oidc())
    if oidc_ok:
        notes.append(oidc_note)
    else:
        failures.append(oidc_note)

    for note in notes:
        print("PASS", note)
    for failure in failures:
        print("FAIL", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
