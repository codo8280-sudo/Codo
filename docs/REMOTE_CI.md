# CODO - remote CI and staging release

## Pull request / push validation

`.github/workflows/codo-ci.yml` runs the same `./tool_ci.sh` used locally:

1. Python compile check;
2. backend tests;
3. OpenAPI snapshot verification;
4. Dart relative import integrity;
5. Flutter dependency resolution;
6. Dart format;
7. Flutter analyze;
8. Flutter tests when present.

CI requires Flutter instead of silently skipping it.

## Manual staging release

`.github/workflows/codo-staging-release.yml` is manual only. It consumes GitHub Environment `staging` secrets and invokes the canonical `backend/scripts/staging_release.py` script.

Required staging secrets:

```text
CODO_DATABASE_URL
CODO_OIDC_ISSUER
CODO_OIDC_AUDIENCE
CODO_API_BASE_URL
```

Optional E2E secrets:

```text
CODO_E2E_USER_TOKEN
CODO_E2E_ADMIN_TOKEN
```

No secret is written into the release report. The report is uploaded as a CI artifact for audit.
