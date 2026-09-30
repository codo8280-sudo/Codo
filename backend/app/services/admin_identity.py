from __future__ import annotations

import json
from ..config import settings
from ..db import connection
from ..rbac import ALL_ADMIN_ROLES


class AdminIdentityService:
    async def list_memberships(self, auth_subject: str | None = None) -> list[dict]:
        async with connection() as conn:
            async with conn.cursor() as cur:
                if auth_subject:
                    await cur.execute(
                        """
                        select auth_subject, role_key, active, granted_at, granted_by
                        from admin_memberships
                        where auth_subject=%s
                        order by role_key
                        """,
                        (auth_subject,),
                    )
                else:
                    await cur.execute(
                        """
                        select auth_subject, role_key, active, granted_at, granted_by
                        from admin_memberships
                        order by auth_subject, role_key
                        """
                    )
                return [dict(row) for row in await cur.fetchall()]

    async def grant(self, auth_subject: str, role_key: str, actor: str) -> dict:
        if role_key not in ALL_ADMIN_ROLES:
            raise ValueError("Unknown CODO administrative role")
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "select role_key from admin_roles where role_key=%s",
                    (role_key,),
                )
                if not await cur.fetchone():
                    raise ValueError("Administrative role is not seeded in the database")
                await cur.execute(
                    """
                    insert into admin_memberships(auth_subject, role_key, active, granted_by)
                    values (%s,%s,true,%s)
                    on conflict (auth_subject, role_key) do update set
                      active=true,
                      granted_at=now(),
                      granted_by=excluded.granted_by
                    returning auth_subject, role_key, active, granted_at, granted_by
                    """,
                    (auth_subject, role_key, actor),
                )
                row = await cur.fetchone()
                await cur.execute(
                    """
                    insert into admin_security_events(actor_subject, event_type, target_subject, metadata)
                    values (%s,'membership_granted',%s,%s::jsonb)
                    """,
                    (actor, auth_subject, json.dumps({"role_key": role_key})),
                )
                await cur.execute(
                    """
                    insert into audit_logs(actor_subject, action, entity_type, entity_id, previous_data, new_data)
                    values (%s,'grant_admin_role','admin_membership',%s,null,%s::jsonb)
                    """,
                    (actor, f"{auth_subject}:{role_key}", json.dumps({"active": True, "role_key": role_key})),
                )
                await conn.commit()
                return dict(row)

    async def revoke(self, auth_subject: str, role_key: str, actor: str) -> dict:
        if role_key not in ALL_ADMIN_ROLES:
            raise ValueError("Unknown CODO administrative role")
        async with connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select auth_subject, role_key, active, granted_at, granted_by
                    from admin_memberships
                    where auth_subject=%s and role_key=%s
                    for update
                    """,
                    (auth_subject, role_key),
                )
                existing = await cur.fetchone()
                if not existing:
                    raise ValueError("Administrative membership not found")
                if not existing["active"]:
                    return dict(existing)

                if role_key == "SUPER_ADMIN" and not settings.admin_bootstrap_token:
                    await cur.execute(
                        """
                        select count(*) as n from admin_memberships
                        where role_key='SUPER_ADMIN' and active=true and auth_subject<>%s
                        """,
                        (auth_subject,),
                    )
                    remaining = int((await cur.fetchone())["n"])
                    if remaining == 0:
                        raise ValueError("Cannot revoke the last active SUPER_ADMIN while bootstrap recovery is disabled")

                await cur.execute(
                    """
                    update admin_memberships set active=false
                    where auth_subject=%s and role_key=%s
                    returning auth_subject, role_key, active, granted_at, granted_by
                    """,
                    (auth_subject, role_key),
                )
                row = await cur.fetchone()
                await cur.execute(
                    """
                    insert into admin_security_events(actor_subject, event_type, target_subject, metadata)
                    values (%s,'membership_revoked',%s,%s::jsonb)
                    """,
                    (actor, auth_subject, json.dumps({"role_key": role_key})),
                )
                await cur.execute(
                    """
                    insert into audit_logs(actor_subject, action, entity_type, entity_id, previous_data, new_data)
                    values (%s,'revoke_admin_role','admin_membership',%s,%s::jsonb,%s::jsonb)
                    """,
                    (
                        actor,
                        f"{auth_subject}:{role_key}",
                        json.dumps({"active": True, "role_key": role_key}),
                        json.dumps({"active": False, "role_key": role_key}),
                    ),
                )
                await conn.commit()
                return dict(row)
