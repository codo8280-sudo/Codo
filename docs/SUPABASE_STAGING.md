# CODO - Supabase staging profile

## Purpose

CODO remains provider-neutral PostgreSQL. Supabase is used as the managed PostgreSQL provider for the dedicated staging environment. The public Flutter client never talks directly to CODO legal tables through the Supabase Data API; FastAPI remains the sole public legal-data boundary.

## Current projects

### Staging

- project name: `Codo_Staging`;
- project ref: `evchtqxpthfaekpaeibh`;
- region: `eu-west-2`;
- PostgreSQL major version: 17;
- state: active and healthy.

### Production

- project name: `Codo_db`;
- project ref: `qpodvtwtquhklohdppua`;
- region: `eu-west-2`;
- PostgreSQL major version: 17;
- state: active and healthy;
- CODO schema intentionally not bootstrapped yet.

Never reuse unrelated application databases for CODO.

## Connection model

For a long-lived FastAPI container, use a direct PostgreSQL connection when IPv6 is available. GitHub Actions and other IPv4-only runtimes should use the Supabase Session pooler.

Verified staging Session pooler parameters:

```text
host=aws-0-eu-west-2.pooler.supabase.com
port=5432
user=postgres.evchtqxpthfaekpaeibh
database=postgres
sslmode=require
```

Runtime configuration:

```text
CODO_DATABASE_PROVIDER=supabase
CODO_DATABASE_URL=postgresql://postgres.evchtqxpthfaekpaeibh:<password>@aws-0-eu-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```

Do not expose the database password, access tokens, service-role keys or a connection string in Flutter or in Git.

The uploaded operational `.env.staging` and `.env.production` files are secret inputs only. They are ignored by Git and are not part of the repository source tree.

## Applied staging migrations

The staging project currently has migrations 001 through 011 applied.

Migration `010_provider_security_hardening.sql`:

- enables RLS on every CODO table in `public`;
- conditionally revokes all table privileges from `anon`, `authenticated` and `service_role`;
- revokes public execution on CODO trigger helper functions;
- revokes future default grants for tables, sequences and functions.

Migration `011_supabase_security_followup.sql`:

- pins `search_path` for CODO trigger helper functions;
- relocates pgvector outside `public` when the extension supports relocation.

The staging migration ledger stores the filename and SHA-256 of every applied repository migration.

## Current security posture

- 46 CODO tables detected;
- RLS enabled on all 46;
- generated Supabase Data API table grants revoked;
- built-in `public.rls_auto_enable()` execution revoked from public Data API roles;
- mutable function `search_path` warnings resolved;
- pgvector-in-`public` warning resolved.

Supabase may still report `RLS enabled, no policy` as informational. This is intentional for the current architecture because no direct Data API access is granted to CODO tables.

## OAuth 2.1 / OpenID Connect staging

Supabase Auth exposes an OAuth 2.1 / OpenID Connect server capability, but it is currently **disabled** on `Codo_Staging`.

The enablement screen currently requires:

- a real Site URL;
- an authorization/consent path (default shown: `/oauth/consent`);
- an implemented consent UI at that path;
- optional dynamic OAuth app registration.

The current Site URL is still `http://localhost:3000`. CODO must therefore not enable the OAuth server yet.

Before activation, the staging application must provide a real HTTPS authorization UI and then confirm creation of a **Public** mobile client using Authorization Code + PKCE, no client secret, and the CODO mobile redirect URI.

Verified OIDC metadata for staging:

```text
issuer=https://evchtqxpthfaekpaeibh.supabase.co/auth/v1
audience=authenticated
active_jwks_signing_algorithm=ES256
mobile_redirect_uri=ci.codo.app:/oauthredirect
```

The discovery document advertises several signing algorithms, but the active public JWKS currently exposes an EC/ES256 signing key. The CODO staging backend therefore uses an explicit `ES256` allowlist.

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

## GitHub staging release environment

The manual staging workflow expects these secrets in the GitHub `staging` environment:

```text
CODO_DATABASE_URL
CODO_OIDC_ISSUER
CODO_OIDC_AUDIENCE
CODO_API_BASE_URL
CODO_E2E_USER_TOKEN
CODO_E2E_ADMIN_TOKEN
```

The provided Supabase/Stitch secret files do not replace the OIDC/API/E2E values above.

## Release gate

```text
CODO_DATABASE_PROVIDER=supabase \
PYTHONPATH=backend python backend/scripts/staging_release.py \
  --provider supabase \
  --api-base https://staging-api.example \
  --release-label increment-08
```

Production promotion is prohibited until this staging gate and the corresponding E2E checks pass.
