# CODO - Supabase staging profile

## Purpose

CODO remains provider-neutral PostgreSQL. Supabase is supported as an optional managed PostgreSQL staging provider. The public Flutter client never talks directly to CODO legal tables through the Supabase Data API; FastAPI remains the sole public legal-data boundary.

## Current project discovery

At Increment 08, the connected Supabase account only exposes the existing Ismail projects. CODO must use a dedicated project and must never reuse those databases.

## Connection model

For a long-lived FastAPI container, use a direct PostgreSQL connection when IPv6 is available. If the runtime network is IPv4-only, use the Supabase shared pooler in session mode. Keep migrations on a session/direct connection, not transaction pooling.

Set:

```text
CODO_DATABASE_PROVIDER=supabase
CODO_DATABASE_URL=postgresql://...
```

Do not expose the database password, service-role keys or a connection string in Flutter.

## Security model

Migration `010_provider_security_hardening.sql`:

- enables RLS on every CODO table in `public`;
- conditionally revokes all table privileges from `anon`, `authenticated` and `service_role` when those roles exist;
- revokes public execution on CODO trigger helper functions;
- remains portable to standard PostgreSQL because Supabase role operations are conditional.

CODO does not depend on Supabase Auth for authorization. OIDC remains the identity protocol and CODO RBAC remains authoritative in PostgreSQL.

## Provider preflight

Run after migrations:

```text
PYTHONPATH=backend python backend/scripts/supabase_preflight.py --json
```

Blocking conditions:

- a CODO table is missing;
- RLS is disabled on a CODO table;
- Supabase Data API roles are absent when provider is declared `supabase`;
- any `anon`, `authenticated` or `service_role` table grant exists on a CODO table.

The report also records PostgreSQL version, SSL state and pgvector availability.

## Release gate

```text
CODO_DATABASE_PROVIDER=supabase \
PYTHONPATH=backend python backend/scripts/staging_release.py \
  --provider supabase \
  --api-base https://staging-api.example \
  --release-label increment-08
```

The provider-security check runs after the generic database/OIDC preflight and before E2E.

## Project creation

Creating a new Supabase project may have a cost. CODO project creation is intentionally not automated until the user selects the target Supabase organization and explicitly confirms the current project cost.
