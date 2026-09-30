from __future__ import annotations

from pathlib import Path

from app.services.provider_security import CODO_PUBLIC_TABLES


def test_provider_security_migration_covers_all_codo_tables():
    path = Path(__file__).resolve().parents[1] / 'postgres' / '010_provider_security_hardening.sql'
    text = path.read_text(encoding='utf-8')
    for table in CODO_PUBLIC_TABLES:
        assert f"'{table}'" in text
    assert 'enable row level security' in text.lower()
    assert "array['anon','authenticated','service_role']" in text


def test_provider_security_migration_revokes_future_default_privileges():
    path = Path(__file__).resolve().parents[1] / 'postgres' / '010_provider_security_hardening.sql'
    text = path.read_text(encoding='utf-8').lower()
    assert 'alter default privileges in schema public revoke all on tables' in text
    assert 'alter default privileges in schema public revoke all on sequences' in text
    assert 'alter default privileges in schema public revoke all on functions' in text
