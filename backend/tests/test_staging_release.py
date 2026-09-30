from __future__ import annotations

from scripts.staging_release import _redact, release_plan


def test_release_plan_requires_migrations_and_preflight():
    plan = release_plan(bootstrap_super_admin=False, run_e2e=True, require_document=True, provider="postgres")
    keys = [item["key"] for item in plan]
    assert keys[0] == "migrations"
    assert "preflight" in keys
    assert "e2e" in keys
    assert "published-document" in keys


def test_release_plan_only_adds_bootstrap_when_requested():
    without = release_plan(bootstrap_super_admin=False, run_e2e=False, require_document=False, provider="postgres")
    with_bootstrap = release_plan(bootstrap_super_admin=True, run_e2e=False, require_document=False, provider="postgres")
    assert "bootstrap-super-admin" not in [item["key"] for item in without]
    assert "bootstrap-super-admin" in [item["key"] for item in with_bootstrap]


def test_release_report_redaction_masks_dsn_credentials_and_bearer_tokens():
    text = "postgresql://codo:secret@db:5432/codo Bearer abc.def.ghi CODO_LLM_API_KEY=very-secret"
    redacted = _redact(text)
    assert "secret@" not in redacted
    assert "abc.def.ghi" not in redacted
    assert "very-secret" not in redacted


def test_release_plan_adds_supabase_security_preflight():
    plan = release_plan(bootstrap_super_admin=False, run_e2e=False, require_document=False, provider="supabase")
    keys = [item["key"] for item in plan]
    assert "provider-security" in keys
    assert keys.index("provider-security") > keys.index("preflight")
