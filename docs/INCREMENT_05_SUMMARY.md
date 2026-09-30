# CODO Increment 05 Summary

Date: 29 September 2026

Increment 05 is cumulative. It contains all previous increments plus OIDC/RBAC, relationship governance and staging controls.

## Added

### OIDC

- generic OpenID Connect discovery;
- JWKS retrieval and cache;
- RSA/allowed-algorithm JWT verification;
- issuer, audience, exp, iat and subject checks;
- HTTPS requirement for OIDC endpoints;
- OpenAPI HTTP Bearer security declaration.

### RBAC

- local CODO role resolution from `admin_memberships`;
- route-level ingestion roles;
- route-level legal-review roles;
- SUPER_ADMIN-only membership administration;
- protection against revoking the last SUPER_ADMIN when no bootstrap recovery exists;
- `/v1/admin/me`;
- membership list/grant/revoke API;
- security event audit records.

### Legal relationships

- pending relationship candidate table;
- candidate creation and review API;
- validation requires existing legal documents and verified A/B evidence;
- rejected and pending candidates never appear in public graph output;
- public validated relationship endpoint;
- mobile article screen retrieves validated document relationships;
- constitutional relationship candidate manifest for 2020 and 2023 amendments.

### PostgreSQL staging

- migration 006;
- migration checksum ledger;
- immutable historical migration enforcement;
- optional PostgreSQL integration test using `CODO_TEST_DATABASE_URL`;
- staging preflight script.

### Bootstrap operations

- first OIDC role grant script;
- relationship candidate bootstrap script;
- updated OIDC and deployment environment variables.

## Verification

- unit/API tests: 29 passed;
- PostgreSQL integration test: defined and skipped when no test database is configured;
- FastAPI root and health smoke tests: passed;
- Python compileall: passed;
- OpenAPI regenerated from FastAPI with 22 paths and HTTP Bearer security;
- no OIDC/admin secret is embedded in Flutter.

## Environment limitation

The build container does not provide a PostgreSQL server/client or Flutter/Dart SDK. Therefore the real PostgreSQL integration test and Flutter analyze/build must run in staging/CI.
