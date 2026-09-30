from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from app.main import app
from app.rbac import UserPrincipal
from app.routers import user_account


@pytest.mark.asyncio
async def test_public_user_principal_uses_oidc_without_admin_membership(monkeypatch):
    from app import dependencies as module

    monkeypatch.setattr(
        module,
        "settings",
        SimpleNamespace(oidc_configured=True),
    )

    async def verify(token: str):
        assert token == "valid-access-token"
        return {
            "sub": "citizen-123",
            "iss": "https://id.codo.test/realms/codo",
            "aud": "codo-api",
        }

    monkeypatch.setattr(module.oidc_authenticator, "verify", verify)
    principal = await module.current_user_principal(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-access-token")
    )
    assert principal.subject == "citizen-123"
    assert principal.issuer == "https://id.codo.test/realms/codo"


@pytest.mark.asyncio
async def test_public_user_auth_is_disabled_when_oidc_not_configured(monkeypatch):
    from app import dependencies as module

    monkeypatch.setattr(module, "settings", SimpleNamespace(oidc_configured=False))
    with pytest.raises(HTTPException) as exc:
        await module.current_user_principal(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        )
    assert exc.value.status_code == 503


class FakeUserService:
    def __init__(self):
        self.deleted = False

    async def sync_profile(self, principal):
        now = datetime.now(timezone.utc)
        return {
            "id": "9dc38520-e45e-4f39-88e5-172caab39dfc",
            "auth_subject": principal.subject,
            "auth_issuer": principal.issuer,
            "display_name": "Awa K.",
            "email": "awa@example.test",
            "email_verified": True,
            "locale": "fr-CI",
            "created_at": now,
            "updated_at": now,
            "last_login_at": now,
        }

    async def update_profile(self, principal, *, display_name, locale):
        row = await self.sync_profile(principal)
        if display_name is not None:
            row["display_name"] = display_name
        if locale is not None:
            row["locale"] = locale
        return row

    async def get_accessibility(self, principal):
        return {
            "text_scale": 1.0,
            "high_contrast": False,
            "reduce_motion": False,
            "offline_cache_enabled": False,
            "updated_at": datetime.now(timezone.utc),
        }

    async def update_accessibility(self, principal, **values):
        return {**values, "updated_at": datetime.now(timezone.utc)}

    async def list_favorites(self, principal):
        return []

    async def add_favorite(self, principal, *, entity_type, entity_key):
        return {
            "id": 7,
            "entity_type": entity_type,
            "entity_key": entity_key,
            "created_at": datetime.now(timezone.utc),
        }

    async def remove_favorite(self, principal, favorite_id):
        return favorite_id == 7

    async def list_folders(self, principal):
        return []

    async def create_folder(self, principal, *, name, description):
        now = datetime.now(timezone.utc)
        return {
            "id": "11111111-1111-4111-8111-111111111111",
            "name": name,
            "description": description,
            "item_count": 0,
            "created_at": now,
            "updated_at": now,
        }

    async def delete_folder(self, principal, folder_id):
        return folder_id == "11111111-1111-4111-8111-111111111111"

    async def list_folder_items(self, principal, folder_id):
        return []

    async def add_folder_item(self, principal, folder_id, *, entity_type, entity_key):
        return {
            "id": 3,
            "entity_type": entity_type,
            "entity_key": entity_key,
            "created_at": datetime.now(timezone.utc),
        }

    async def remove_folder_item(self, principal, folder_id, item_id):
        return item_id == 3

    async def list_alerts(self, principal):
        return []

    async def create_alert(self, principal, *, scope_type, scope_key):
        return {
            "id": "22222222-2222-4222-8222-222222222222",
            "scope_type": scope_type,
            "scope_key": scope_key,
            "enabled": True,
            "created_at": datetime.now(timezone.utc),
        }

    async def update_alert(self, principal, alert_id, *, enabled):
        return {
            "id": alert_id,
            "scope_type": "document",
            "scope_key": "CODO-CI-CONST-2016",
            "enabled": enabled,
            "created_at": datetime.now(timezone.utc),
        }

    async def delete_alert(self, principal, alert_id):
        return alert_id == "22222222-2222-4222-8222-222222222222"

    async def delete_account(self, principal):
        self.deleted = True
        return True


def _principal():
    return UserPrincipal(
        subject="citizen-123",
        issuer="https://id.codo.test/realms/codo",
        claims={"sub": "citizen-123"},
    )


def test_user_account_routes_are_oidc_scoped():
    fake = FakeUserService()
    app.dependency_overrides[user_account.require_database] = lambda: None
    app.dependency_overrides[user_account.current_user_principal] = _principal
    app.dependency_overrides[user_account.user_identity_service] = lambda: fake
    try:
        client = TestClient(app)
        profile = client.get("/v1/me")
        assert profile.status_code == 200
        assert profile.json()["auth_subject"] == "citizen-123"

        favorite = client.post(
            "/v1/me/favorites",
            json={"entity_type": "article", "entity_key": "CODO-CI-CONST-2016-ART-001"},
        )
        assert favorite.status_code == 201
        assert favorite.json()["id"] == 7

        removed = client.delete("/v1/me/favorites/7")
        assert removed.status_code == 204

        folder = client.post("/v1/me/folders", json={"name": "Constitution"})
        assert folder.status_code == 201
        assert folder.json()["name"] == "Constitution"

        alert = client.post(
            "/v1/me/alerts",
            json={"scope_type": "document", "scope_key": "CODO-CI-CONST-2016"},
        )
        assert alert.status_code == 201
        alert_id = alert.json()["id"]
        toggled = client.patch(f"/v1/me/alerts/{alert_id}", json={"enabled": False})
        assert toggled.status_code == 200
        assert toggled.json()["enabled"] is False

        deleted = client.delete("/v1/me")
        assert deleted.status_code == 204
        assert fake.deleted is True
    finally:
        app.dependency_overrides.clear()
