# CODO Mobile OIDC

## Security model

CODO mobile uses OpenID Connect Authorization Code Flow with PKCE. The mobile client is public and must never contain a client secret.

Current Flutter dependencies:

- `flutter_appauth` 12.1.x;
- `flutter_secure_storage` 11.2.x.

Access, refresh and ID tokens are stored only through platform secure storage. The API receives the access token as a Bearer token and validates signature, issuer, audience, expiry and issuance time against the configured OIDC provider.

## Compile-time configuration

```text
--dart-define=CODO_API_BASE_URL=https://api.example
--dart-define=CODO_OIDC_ISSUER=https://identity.example/realms/codo
--dart-define=CODO_OIDC_CLIENT_ID=codo-mobile
--dart-define=CODO_OIDC_REDIRECT_URL=ci.codo.app:/oauthredirect
--dart-define=CODO_OIDC_POST_LOGOUT_REDIRECT_URL=ci.codo.app:/oauthredirect
--dart-define=CODO_OIDC_SCOPES=openid,profile,email,offline_access
```

`CODO_OIDC_ALLOW_INSECURE_HTTP=true` is reserved for isolated local development. It must remain false in shared staging and production.

## Native callback

Run:

```text
./tool_bootstrap.sh
```

The bootstrap generates Android/iOS projects and `tool_configure_oidc.py` adds the custom callback scheme `ci.codo.app`, enforces Android API 24+ and iOS 13+ to match the selected authentication plugins, then runs dependency resolution and static analysis.

## Account separation

An authenticated citizen receives a `UserPrincipal`. An administrator still needs an active record in `admin_memberships`. A valid OIDC token alone never grants administrative authority.

## Account deletion

`DELETE /v1/me` removes the user profile and all dependent favorites, folders, alerts and accessibility settings through database cascades. CODO retains only a non-linkable SHA-256 deletion event. Its digest includes a fresh random nonce that is deliberately not stored, so the deleted OIDC subject cannot be recomputed from the ledger.
