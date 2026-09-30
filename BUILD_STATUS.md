# CODO Build Status - Increment 08

Date: 30 September 2026

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

Eleven additive migrations are defined.

- migrations 001-010 remain unchanged and immutable;
- migration 010 closes the Supabase Data API boundary for CODO tables;
- migration 011 fixes Supabase security-linter findings by pinning trigger-function `search_path` and relocating pgvector outside `public` when the extension is relocatable.

## Supabase staging

A dedicated CODO staging project is now provisioned and bootstrapped:

- project: `Codo_Staging`;
- project ref: `evchtqxpthfaekpaeibh`;
- PostgreSQL: 17;
- 46 CODO tables present;
- RLS enabled on all 46 CODO tables;
- migrations 001-011 applied;
- migration ledger populated with immutable SHA-256 hashes;
- six official legal-source registry entries and nine legal domains seeded;
- Supabase security warnings for `SECURITY DEFINER`, mutable function `search_path` and pgvector in `public` resolved.

The remaining `RLS enabled, no policy` advisor messages are informational and expected because CODO does not expose these tables through the Supabase Data API. FastAPI remains the public boundary and Data API grants are revoked.

## Production database

`Codo_db` is intentionally untouched at this stage:

- no CODO tables;
- no CODO migrations;
- no production bootstrap has been performed.

Production migration is blocked until staging release-gate and E2E validation succeed.

## Remote CI

The repository now contains a normalized source tree instead of a ZIP-only payload.

GitHub workflows are installed for:

- push/pull-request CI;
- manual staging release gate;
- audited release report artifact.

## Validation

- local backend tests: 59 passed;
- PostgreSQL integration: 1 skipped locally because no direct test DB driver/connection was configured in that runtime;
- Python compilation: passed;
- OpenAPI snapshot: passed in the prepared source baseline;
- Dart relative imports: 0 missing across 56 files in the prepared source baseline;
- dedicated Supabase staging schema: bootstrapped and security-checked.

## Remaining execution dependencies

1. configure staging runtime secret `CODO_DATABASE_URL`;
2. configure HTTPS OIDC issuer and audience;
3. configure `CODO_API_BASE_URL`, `CODO_E2E_USER_TOKEN` and `CODO_E2E_ADMIN_TOKEN` for the staging GitHub environment;
4. bootstrap the first OIDC-backed `SUPER_ADMIN`;
5. acquire the first official constitutional source binary and store its immutable snapshot;
6. perform human legal validation;
7. publish and verify the first publication receipt;
8. run full staging E2E and Flutter builds;
9. only after the staging gate is green, promote the same immutable migrations to `Codo_db`.
