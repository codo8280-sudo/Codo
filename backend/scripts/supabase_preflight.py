from __future__ import annotations

import argparse
import json

from app.config import settings
from app.services.provider_security import (
    CODO_PUBLIC_TABLES,
    SUPABASE_DATA_API_ROLES,
    TableGrant,
    TableSecurityState,
    evaluate_supabase_security,
)


def main() -> int:
    parser = argparse.ArgumentParser(description='CODO Supabase/Postgres provider security preflight')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if not settings.database_configured:
        raise SystemExit('CODO_DATABASE_URL is required')

    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit('Install backend/requirements.txt before running provider preflight') from exc

    payload: dict[str, object] = {'provider': 'supabase'}
    with psycopg.connect(settings.database_url) as conn:
        server_version = conn.execute('show server_version').fetchone()[0]
        current_user = conn.execute('select current_user').fetchone()[0]
        ssl_row = conn.execute(
            'select ssl, version, cipher from pg_stat_ssl where pid=pg_backend_pid()'
        ).fetchone()
        vector_row = conn.execute(
            "select extversion from pg_extension where extname='vector'"
        ).fetchone()
        roles = [
            row[0]
            for row in conn.execute(
                'select rolname from pg_roles where rolname = any(%s)',
                (list(SUPABASE_DATA_API_ROLES),),
            ).fetchall()
        ]
        table_rows = conn.execute(
            """
            select c.relname, c.relrowsecurity
            from pg_class c
            join pg_namespace n on n.oid=c.relnamespace
            where n.nspname='public' and c.relkind='r' and c.relname = any(%s)
            order by c.relname
            """,
            (list(CODO_PUBLIC_TABLES),),
        ).fetchall()
        grant_rows = conn.execute(
            """
            select grantee, table_name, privilege_type
            from information_schema.role_table_grants
            where table_schema='public'
              and grantee = any(%s)
              and table_name = any(%s)
            order by grantee, table_name, privilege_type
            """,
            (list(SUPABASE_DATA_API_ROLES), list(CODO_PUBLIC_TABLES)),
        ).fetchall()

    states = [TableSecurityState(str(name), bool(rls)) for name, rls in table_rows]
    grants = [TableGrant(str(role), str(table), str(privilege)) for role, table, privilege in grant_rows]
    issues = evaluate_supabase_security(table_states=states, grants=grants, existing_roles=roles)
    if not (ssl_row and ssl_row[0]):
        issues.append('ssl_not_enabled')

    payload.update(
        {
            'server_version': str(server_version),
            'current_user': str(current_user),
            'ssl': bool(ssl_row and ssl_row[0]),
            'ssl_version': str(ssl_row[1]) if ssl_row else None,
            'pgvector': str(vector_row[0]) if vector_row else None,
            'rls_tables': sum(1 for item in states if item.rls_enabled),
            'expected_tables': len(CODO_PUBLIC_TABLES),
            'data_api_grants': len(grants),
            'issues': issues,
            'status': 'passed' if not issues else 'failed',
        }
    )

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print('provider=supabase')
        print(f'server_version={server_version}')
        print(f'ssl={bool(ssl_row and ssl_row[0])}')
        print(f'pgvector={vector_row[0] if vector_row else "not-installed"}')
        for issue in issues:
            print('FAIL', issue)
        if not issues:
            print('PASS supabase-data-api-boundary=closed')
            print('PASS rls=enabled')
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
