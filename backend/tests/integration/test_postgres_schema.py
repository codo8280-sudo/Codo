from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.mark.integration
def test_all_migrations_apply_in_isolated_schema():
    database_url = os.getenv("CODO_TEST_DATABASE_URL", "")
    if not database_url:
        pytest.skip("CODO_TEST_DATABASE_URL is not configured")
    psycopg = pytest.importorskip("psycopg")

    schema = "codo_test_" + uuid4().hex[:12]
    migrations = sorted((Path(__file__).resolve().parents[2] / "postgres").glob("*.sql"))
    assert migrations

    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(f'create schema "{schema}"')
        try:
            conn.execute(f'set search_path to "{schema}", public')
            for migration in migrations:
                conn.execute(migration.read_text(encoding="utf-8"))

            tables = {
                row[0]
                for row in conn.execute(
                    """
                    select table_name from information_schema.tables
                    where table_schema=%s
                    """,
                    (schema,),
                ).fetchall()
            }
            assert "legal_documents" in tables
            assert "legal_relationship_candidates" in tables
            assert "admin_security_events" in tables
            assert "legal_relationship_evidence" in tables
            assert "privacy_events" in tables
            assert "user_profiles" in tables
            assert "corpus_publication_receipts" in tables
            assert "staging_release_runs" in tables
            assert "staging_release_checks" in tables

            roles = {
                row[0]
                for row in conn.execute(
                    "select role_key from admin_roles"
                ).fetchall()
            }
            assert "SUPER_ADMIN" in roles
            assert "VALIDATEUR_JURIDIQUE" in roles
        finally:
            conn.execute("set search_path to public")
            conn.execute(f'drop schema "{schema}" cascade')
