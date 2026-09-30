from __future__ import annotations

from app.services.provider_security import (
    CODO_PUBLIC_TABLES,
    SUPABASE_DATA_API_ROLES,
    TableGrant,
    TableSecurityState,
    evaluate_supabase_security,
)


def _secure_states():
    return [TableSecurityState(name, True) for name in CODO_PUBLIC_TABLES]


def test_supabase_security_passes_when_rls_enabled_and_no_data_api_grants():
    issues = evaluate_supabase_security(
        table_states=_secure_states(),
        grants=[],
        existing_roles=SUPABASE_DATA_API_ROLES,
    )
    assert issues == []


def test_supabase_security_rejects_disabled_rls():
    states = _secure_states()
    states[0] = TableSecurityState(states[0].table_name, False)
    issues = evaluate_supabase_security(
        table_states=states,
        grants=[],
        existing_roles=SUPABASE_DATA_API_ROLES,
    )
    assert any(item.startswith('rls_disabled=') for item in issues)


def test_supabase_security_rejects_data_api_grants():
    issues = evaluate_supabase_security(
        table_states=_secure_states(),
        grants=[TableGrant('authenticated', CODO_PUBLIC_TABLES[0], 'SELECT')],
        existing_roles=SUPABASE_DATA_API_ROLES,
    )
    assert any(item.startswith('data_api_grants=') for item in issues)


def test_supabase_security_requires_supabase_roles():
    issues = evaluate_supabase_security(
        table_states=_secure_states(),
        grants=[],
        existing_roles=(),
    )
    assert any(item.startswith('missing_supabase_roles=') for item in issues)
