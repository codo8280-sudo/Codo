from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


@pytest.mark.asyncio
async def test_bootstrap_token_resolves_to_super_admin(monkeypatch):
    from app import dependencies as module

    monkeypatch.setattr(
        module,
        "settings",
        SimpleNamespace(
            admin_bootstrap_token="bootstrap-secret-value",
            oidc_configured=False,
            database_configured=False,
        ),
    )
    principal = await module.current_admin_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials="bootstrap-secret-value"))
    assert principal.subject == "bootstrap-admin"
    assert principal.roles == frozenset({"SUPER_ADMIN"})
    assert principal.authentication_method == "bootstrap"


@pytest.mark.asyncio
async def test_invalid_bootstrap_token_is_forbidden_when_oidc_disabled(monkeypatch):
    from app import dependencies as module

    monkeypatch.setattr(
        module,
        "settings",
        SimpleNamespace(
            admin_bootstrap_token="bootstrap-secret-value",
            oidc_configured=False,
            database_configured=False,
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await module.current_admin_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-token"))
    assert exc.value.status_code == 403
