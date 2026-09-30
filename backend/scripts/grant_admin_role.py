from __future__ import annotations

import argparse
import os

ALLOWED_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "VALIDATEUR_JURIDIQUE",
    "DOCUMENTALISTE",
    "REDACTEUR",
    "DATA_MANAGER",
    "MODERATEUR",
    "AUDITEUR",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Grant an initial CODO administrative role to an OIDC subject.")
    parser.add_argument("subject")
    parser.add_argument("role", choices=sorted(ALLOWED_ROLES))
    args = parser.parse_args()

    database_url = os.getenv("CODO_DATABASE_URL", "")
    if not database_url:
        raise SystemExit("CODO_DATABASE_URL is required")

    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("Install backend/requirements.txt before running this script") from exc

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("select 1 from admin_roles where role_key=%s", (args.role,))
            if not cur.fetchone():
                raise SystemExit("Role is not seeded. Run database migrations first.")
            cur.execute(
                """
                insert into admin_memberships(auth_subject, role_key, active, granted_by)
                values (%s,%s,true,'bootstrap-script')
                on conflict (auth_subject, role_key) do update set
                  active=true,
                  granted_at=now(),
                  granted_by='bootstrap-script'
                """,
                (args.subject, args.role),
            )
            cur.execute(
                """
                insert into admin_security_events(actor_subject, event_type, target_subject, metadata)
                values ('bootstrap-script','membership_granted',%s,%s)
                """,
                (args.subject, {"role_key": args.role}),
            )
        conn.commit()

    print(f"Granted {args.role} to OIDC subject {args.subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
