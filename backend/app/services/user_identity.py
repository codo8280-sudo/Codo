from __future__ import annotations

import hashlib
import json
import secrets
from uuid import uuid4

from ..db import connection
from ..rbac import UserPrincipal


class UserIdentityService:
    @staticmethod
    def _display_name(claims: dict) -> str | None:
        for key in ("name", "preferred_username", "given_name"):
            value = claims.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:240]
        return None

    @staticmethod
    def _email(claims: dict) -> str | None:
        value = claims.get("email")
        if isinstance(value, str) and value.strip():
            return value.strip()[:320]
        return None

    @staticmethod
    def _email_verified(claims: dict) -> bool:
        return claims.get("email_verified") is True

    @staticmethod
    def _locale(claims: dict) -> str:
        value = claims.get("locale")
        if isinstance(value, str) and value.strip():
            return value.strip()[:32]
        return "fr-CI"

    async def sync_profile(self, principal: UserPrincipal) -> dict:
        profile_id = str(uuid4())
        claims = principal.claims
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    insert into user_profiles(
                      id, auth_subject, auth_issuer, display_name, email,
                      email_verified, locale, last_login_at
                    )
                    values (%s,%s,%s,%s,%s,%s,%s,now())
                    on conflict (auth_issuer, auth_subject) do update set
                      auth_issuer=excluded.auth_issuer,
                      display_name=coalesce(user_profiles.display_name, excluded.display_name),
                      email=excluded.email,
                      email_verified=excluded.email_verified,
                      locale=case
                        when user_profiles.locale is null or user_profiles.locale='' then excluded.locale
                        else user_profiles.locale
                      end,
                      last_login_at=now(),
                      updated_at=now()
                    returning id::text, auth_subject, auth_issuer, display_name, email,
                              email_verified, locale, created_at, updated_at, last_login_at
                    """,
                    (
                        profile_id,
                        principal.subject,
                        principal.issuer,
                        self._display_name(claims),
                        self._email(claims),
                        self._email_verified(claims),
                        self._locale(claims),
                    ),
                )
                row = await cur.fetchone()
                await cur.execute(
                    """
                    insert into user_accessibility_settings(user_id)
                    values (%s::uuid)
                    on conflict (user_id) do nothing
                    """,
                    (row["id"],),
                )
                await conn.commit()
                return dict(row)

    async def update_profile(self, principal: UserPrincipal, *, display_name: str | None, locale: str | None) -> dict:
        await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    update user_profiles
                    set display_name=coalesce(%s, display_name),
                        locale=coalesce(%s, locale),
                        updated_at=now()
                    where auth_subject=%s and auth_issuer=%s
                    returning id::text, auth_subject, auth_issuer, display_name, email,
                              email_verified, locale, created_at, updated_at, last_login_at
                    """,
                    (display_name, locale, principal.subject, principal.issuer),
                )
                row = await cur.fetchone()
                await conn.commit()
                return dict(row)

    async def get_accessibility(self, principal: UserPrincipal) -> dict:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select text_scale::float8 as text_scale, high_contrast, reduce_motion,
                           offline_cache_enabled, updated_at
                    from user_accessibility_settings
                    where user_id=%s::uuid
                    """,
                    (profile["id"],),
                )
                return dict(await cur.fetchone())

    async def update_accessibility(
        self,
        principal: UserPrincipal,
        *,
        text_scale: float,
        high_contrast: bool,
        reduce_motion: bool,
        offline_cache_enabled: bool,
    ) -> dict:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    insert into user_accessibility_settings(
                      user_id, text_scale, high_contrast, reduce_motion, offline_cache_enabled, updated_at
                    ) values (%s::uuid,%s,%s,%s,%s,now())
                    on conflict (user_id) do update set
                      text_scale=excluded.text_scale,
                      high_contrast=excluded.high_contrast,
                      reduce_motion=excluded.reduce_motion,
                      offline_cache_enabled=excluded.offline_cache_enabled,
                      updated_at=now()
                    returning text_scale::float8 as text_scale, high_contrast, reduce_motion,
                              offline_cache_enabled, updated_at
                    """,
                    (profile["id"], text_scale, high_contrast, reduce_motion, offline_cache_enabled),
                )
                row = await cur.fetchone()
                await conn.commit()
                return dict(row)

    async def list_favorites(self, principal: UserPrincipal) -> list[dict]:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select id, entity_type, entity_key, created_at
                    from user_favorites
                    where user_id=%s::uuid
                    order by created_at desc, id desc
                    """,
                    (profile["id"],),
                )
                return [dict(row) for row in await cur.fetchall()]

    async def add_favorite(self, principal: UserPrincipal, *, entity_type: str, entity_key: str) -> dict:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    insert into user_favorites(user_id, entity_type, entity_key)
                    values (%s::uuid,%s,%s)
                    on conflict (user_id, entity_type, entity_key) do update
                      set entity_key=excluded.entity_key
                    returning id, entity_type, entity_key, created_at
                    """,
                    (profile["id"], entity_type, entity_key),
                )
                row = await cur.fetchone()
                await conn.commit()
                return dict(row)

    async def remove_favorite(self, principal: UserPrincipal, favorite_id: int) -> bool:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    delete from user_favorites
                    where id=%s and user_id=%s::uuid
                    returning id
                    """,
                    (favorite_id, profile["id"]),
                )
                deleted = await cur.fetchone()
                await conn.commit()
                return deleted is not None


    async def list_folders(self, principal: UserPrincipal) -> list[dict]:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select f.id::text, f.name, f.description, f.created_at, f.updated_at,
                           count(i.id)::int as item_count
                    from user_folders f
                    left join user_folder_items i on i.folder_id=f.id
                    where f.user_id=%s::uuid
                    group by f.id
                    order by f.updated_at desc, f.created_at desc
                    """,
                    (profile["id"],),
                )
                return [dict(row) for row in await cur.fetchall()]

    async def create_folder(self, principal: UserPrincipal, *, name: str, description: str | None) -> dict:
        profile = await self.sync_profile(principal)
        folder_id = str(uuid4())
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    insert into user_folders(id, user_id, name, description)
                    values (%s::uuid,%s::uuid,%s,%s)
                    returning id::text, name, description, created_at, updated_at
                    """,
                    (folder_id, profile["id"], name, description),
                )
                row = dict(await cur.fetchone())
                row["item_count"] = 0
                await conn.commit()
                return row

    async def delete_folder(self, principal: UserPrincipal, folder_id: str) -> bool:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    delete from user_folders
                    where id=%s::uuid and user_id=%s::uuid
                    returning id
                    """,
                    (folder_id, profile["id"]),
                )
                deleted = await cur.fetchone()
                await conn.commit()
                return deleted is not None

    async def list_folder_items(self, principal: UserPrincipal, folder_id: str) -> list[dict] | None:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "select 1 from user_folders where id=%s::uuid and user_id=%s::uuid",
                    (folder_id, profile["id"]),
                )
                if await cur.fetchone() is None:
                    return None
                await cur.execute(
                    """
                    select i.id, i.entity_type, i.entity_key, i.created_at
                    from user_folder_items i
                    where i.folder_id=%s::uuid
                    order by i.created_at desc, i.id desc
                    """,
                    (folder_id,),
                )
                return [dict(row) for row in await cur.fetchall()]

    async def add_folder_item(
        self,
        principal: UserPrincipal,
        folder_id: str,
        *,
        entity_type: str,
        entity_key: str,
    ) -> dict | None:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "select 1 from user_folders where id=%s::uuid and user_id=%s::uuid",
                    (folder_id, profile["id"]),
                )
                if await cur.fetchone() is None:
                    return None
                await cur.execute(
                    """
                    insert into user_folder_items(folder_id, entity_type, entity_key)
                    values (%s::uuid,%s,%s)
                    on conflict (folder_id, entity_type, entity_key) do update
                      set entity_key=excluded.entity_key
                    returning id, entity_type, entity_key, created_at
                    """,
                    (folder_id, entity_type, entity_key),
                )
                row = dict(await cur.fetchone())
                await cur.execute("update user_folders set updated_at=now() where id=%s::uuid", (folder_id,))
                await conn.commit()
                return row

    async def remove_folder_item(self, principal: UserPrincipal, folder_id: str, item_id: int) -> bool:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    delete from user_folder_items i
                    using user_folders f
                    where i.id=%s and i.folder_id=f.id and f.id=%s::uuid and f.user_id=%s::uuid
                    returning i.id
                    """,
                    (item_id, folder_id, profile["id"]),
                )
                deleted = await cur.fetchone()
                if deleted:
                    await cur.execute("update user_folders set updated_at=now() where id=%s::uuid", (folder_id,))
                await conn.commit()
                return deleted is not None

    async def list_alerts(self, principal: UserPrincipal) -> list[dict]:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select id::text, scope_type, scope_key, enabled, created_at
                    from user_alert_subscriptions
                    where user_id=%s::uuid
                    order by created_at desc
                    """,
                    (profile["id"],),
                )
                return [dict(row) for row in await cur.fetchall()]

    async def create_alert(self, principal: UserPrincipal, *, scope_type: str, scope_key: str) -> dict:
        profile = await self.sync_profile(principal)
        alert_id = str(uuid4())
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    insert into user_alert_subscriptions(id, user_id, scope_type, scope_key, enabled)
                    values (%s::uuid,%s::uuid,%s,%s,true)
                    on conflict (user_id, scope_type, scope_key) do update set enabled=true
                    returning id::text, scope_type, scope_key, enabled, created_at
                    """,
                    (alert_id, profile["id"], scope_type, scope_key),
                )
                row = dict(await cur.fetchone())
                await conn.commit()
                return row

    async def update_alert(self, principal: UserPrincipal, alert_id: str, *, enabled: bool) -> dict | None:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    update user_alert_subscriptions
                    set enabled=%s
                    where id=%s::uuid and user_id=%s::uuid
                    returning id::text, scope_type, scope_key, enabled, created_at
                    """,
                    (enabled, alert_id, profile["id"]),
                )
                row = await cur.fetchone()
                await conn.commit()
                return dict(row) if row else None

    async def delete_alert(self, principal: UserPrincipal, alert_id: str) -> bool:
        profile = await self.sync_profile(principal)
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    delete from user_alert_subscriptions
                    where id=%s::uuid and user_id=%s::uuid
                    returning id
                    """,
                    (alert_id, profile["id"]),
                )
                deleted = await cur.fetchone()
                await conn.commit()
                return deleted is not None

    async def delete_account(self, principal: UserPrincipal) -> bool:
        # Do not store the OIDC subject after account deletion. The privacy ledger
        # receives only a non-linkable one-way digest. The random nonce is deliberately
        # not stored, so the deleted OIDC subject cannot be recomputed from the ledger.
        material = secrets.token_bytes(32) + f"{principal.issuer}|{principal.subject}".encode("utf-8")
        digest = hashlib.sha256(material).hexdigest()
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    delete from user_profiles
                    where auth_subject=%s and auth_issuer=%s
                    returning id
                    """,
                    (principal.subject, principal.issuer),
                )
                deleted = await cur.fetchone()
                if deleted:
                    await cur.execute(
                        """
                        insert into privacy_events(subject_hash, event_type, metadata)
                        values (%s,'account_deleted',%s::jsonb)
                        """,
                        (digest, json.dumps({"source": "self_service"})),
                    )
                await conn.commit()
                return deleted is not None
