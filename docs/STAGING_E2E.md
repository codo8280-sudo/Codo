# CODO Staging E2E

The staging gate is intentionally external to unit tests because the build container does not provide PostgreSQL, Flutter or a deployed OIDC provider.

## Server checks

After deploying PostgreSQL, OIDC and the API:

```text
python backend/scripts/staging_preflight.py
```

Then execute:

```text
export CODO_E2E_USER_TOKEN='...'
export CODO_E2E_ADMIN_TOKEN='...'

python backend/scripts/e2e_staging.py \
  --api-base https://api.staging.example \
  --document-id CODO-CI-CONST-2016
```

The E2E script verifies:

- liveness and readiness;
- public search;
- OIDC user profile;
- administrative role resolution;
- a published document;
- provenance entries and SHA-256 hashes;
- publication receipt and its SHA-256 hashes;
- trust levels;
- public validated graph relationships.

It does not publish or mutate legal content.

## Local identity-provider reference

`backend/compose.identity-dev.yaml` starts Keycloak 26.7.4 and imports `backend/keycloak/codo-realm.json` for backend/browser testing on localhost. It is development-only and is not a production identity architecture.

No test citizen is pre-created. Create users through the local Keycloak admin console or the registration screen so that default credentials are never committed to the project.


## Full release gate

Increment 07 adds `backend/scripts/staging_release.py`, which combines migrations, preflight and E2E into one auditable release gate. See `docs/RELEASE_GATE.md`.
