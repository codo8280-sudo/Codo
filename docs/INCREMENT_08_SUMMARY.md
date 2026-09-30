# CODO Increment 08 - summary

Date: 29 September 2026

## Scope

Increment 08 is cumulative. It preserves Increments 01-07 and adds a provider-aware staging profile, Supabase security hardening, remote CI workflows, and explicit safeguards that keep the FastAPI API as the only public legal-data boundary.

## Supabase discovery

The connected Supabase account currently exposes only the pre-existing Ismail projects. No CODO project was created and no Ismail database was modified or reused.

A dedicated CODO Supabase project can be used later after the user selects the target organization and explicitly confirms the current project cost.

## Database provider model

New backend setting:

```text
CODO_DATABASE_PROVIDER=postgres|supabase
```

CODO remains PostgreSQL-native. `supabase` adds provider-specific security checks; it does not replace CODO OIDC or RBAC.

## Migration 010

`010_provider_security_hardening.sql`:

- enables RLS for all CODO public tables;
- revokes table privileges from Supabase `anon`, `authenticated`, and `service_role` roles when they exist;
- revokes future default privileges on tables, sequences, and functions for those roles;
- revokes PUBLIC execute on CODO trigger helper functions;
- stays portable to standard PostgreSQL by applying Supabase role statements conditionally.

## Supabase preflight

New script:

```text
backend/scripts/supabase_preflight.py
```

It validates:

- all expected CODO tables exist;
- RLS is enabled on each one;
- Supabase Data API roles exist;
- none of those roles has a grant on a CODO table;
- the PostgreSQL connection uses SSL.

It also reports PostgreSQL version and pgvector availability.

## Release gate 0.8

`backend/scripts/staging_release.py` accepts:

```text
--provider postgres
--provider supabase
```

When `supabase` is selected, the provider-security preflight is blocking and runs after the generic PostgreSQL/OIDC preflight and before E2E.

Default release label is now `increment-08`.

## Remote CI

Added:

- `.github/workflows/codo-ci.yml`
- `.github/workflows/codo-staging-release.yml`
- `backend/requirements-dev.txt`

The regular workflow executes the canonical local CI gate and requires Flutter. The staging workflow is manual and consumes only staging environment secrets.

## Versions

- API: 0.8.0
- Flutter package: 0.8.0+8
- OpenAPI paths: 36
- PostgreSQL migrations: 10

## Validation

Executed in the current container:

- Python tests: 59 passed;
- PostgreSQL integration test: 1 skipped because no disposable/staging database is configured;
- Python compile check: passed;
- OpenAPI snapshot: passed, 36 paths;
- release plan: passed for `provider=supabase`;
- GitHub workflow YAML parse: passed;
- Dart relative imports: 0 missing across 56 files;
- Flutter SDK: not installed locally, therefore native analyze/build is delegated to remote CI where Flutter is required.

## Not claimed

- no remote CODO Supabase project has been created;
- no Ismail project has been touched;
- no remote database migration has been executed;
- no OIDC HTTPS staging issuer has been deployed;
- no official Constitution PDF has been acquired from the Presidency server because both browser and container download attempts failed;
- no legal validation has been simulated.
