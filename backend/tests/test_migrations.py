from __future__ import annotations

from pathlib import Path

from scripts.migrate import migration_hash


def test_migration_hash_is_stable(tmp_path: Path):
    migration = tmp_path / "001_test.sql"
    migration.write_text("select 1;\n", encoding="utf-8")
    first = migration_hash(migration)
    second = migration_hash(migration)
    assert first == second
    assert len(first) == 64


def test_migration_hash_changes_when_historical_file_changes(tmp_path: Path):
    migration = tmp_path / "001_test.sql"
    migration.write_text("select 1;\n", encoding="utf-8")
    first = migration_hash(migration)
    migration.write_text("select 2;\n", encoding="utf-8")
    assert migration_hash(migration) != first
