# CODO Build Status - Increment 08

Date: 29 September 2026

## Nature

Increment 08 is cumulative and includes all previous increments.

## Mobile Flutter 0.8

- 35-screen product family preserved;
- OIDC Authorization Code + PKCE;
- secure token storage and refresh;
- synchronized user space;
- legal provenance, validated graph and publication receipt;
- safe fallback when API/corpus is unavailable;
- package version `0.8.0+8`.

## Backend API 0.8

- source-first legal search and CODO AI;
- OIDC/JWKS authentication;
- local CODO RBAC;
- controlled acquisition and extraction;
- blocking legal quality gate;
- publication receipt and provenance chain;
- provider-aware staging release gate;
- API version `0.8.0`;
- OpenAPI paths: 36.

## PostgreSQL

Ten immutable migrations are now defined. Migration 010 adds provider security hardening for optional Supabase staging while remaining portable to standard PostgreSQL.

## Supabase compatibility

- dedicated provider preflight;
- RLS required on every CODO table;
- Data API roles have no CODO table grants;
- future default grants are revoked;
- SSL is required by the provider preflight;
- pgvector is reported but remains optional.

The connected Supabase account currently contains only Ismail projects. CODO does not reuse them.

## Remote CI

GitHub workflows are ready for:

- push/pull-request CI;
- manual staging release gate;
- audited release report artifact.

## Validation

- tests: 59 passed;
- PostgreSQL integration: 1 skipped because no test/staging DB is configured;
- OpenAPI snapshot: passed;
- workflows YAML: passed;
- Dart relative imports: 0 missing across 56 files;
- Flutter SDK: absent locally, remote CI requires it.

## Remaining execution dependencies

1. create/select a dedicated CODO staging PostgreSQL project;
2. provide `CODO_DATABASE_URL`;
3. provide an HTTPS OIDC issuer and audience;
4. run the 10 migrations and provider preflight;
5. bootstrap the first SUPER_ADMIN;
6. acquire the official constitutional source binary;
7. perform human legal validation;
8. publish and verify the first publication receipt;
9. run full E2E and Flutter builds.
