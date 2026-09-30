from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
import jwt
from jwt import InvalidTokenError, PyJWK

from .config import settings


class AuthenticationError(ValueError):
    pass


@dataclass
class _CacheEntry:
    value: dict[str, Any]
    expires_at: float


class OidcAuthenticator:
    def __init__(self) -> None:
        self._metadata: _CacheEntry | None = None
        self._jwks: _CacheEntry | None = None
        self._lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return settings.oidc_configured

    async def verify(self, token: str) -> dict[str, Any]:
        if not self.configured:
            raise AuthenticationError("OIDC authentication is not configured")
        try:
            header = jwt.get_unverified_header(token)
        except InvalidTokenError as exc:
            raise AuthenticationError("Malformed bearer token") from exc

        algorithm = header.get("alg")
        if algorithm not in settings.oidc_algorithms:
            raise AuthenticationError("Token signing algorithm is not allowed")
        kid = header.get("kid")
        if not kid:
            raise AuthenticationError("Bearer token does not contain a key id")

        jwks = await self._get_jwks()
        jwk_data = next((item for item in jwks.get("keys", []) if item.get("kid") == kid), None)
        if jwk_data is None:
            self._jwks = None
            jwks = await self._get_jwks(force=True)
            jwk_data = next((item for item in jwks.get("keys", []) if item.get("kid") == kid), None)
        if jwk_data is None:
            raise AuthenticationError("No trusted signing key matches the bearer token")

        try:
            key = PyJWK.from_dict(jwk_data).key
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(settings.oidc_algorithms),
                audience=settings.oidc_audience,
                issuer=settings.oidc_issuer,
                leeway=settings.oidc_clock_skew_seconds,
                options={
                    "require": ["sub", "iss", "aud", "exp", "iat"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
        except InvalidTokenError as exc:
            raise AuthenticationError("Bearer token validation failed") from exc

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Bearer token subject is missing")
        return claims

    async def _get_metadata(self, force: bool = False) -> dict[str, Any]:
        now = time.monotonic()
        if not force and self._metadata and self._metadata.expires_at > now:
            return self._metadata.value
        async with self._lock:
            now = time.monotonic()
            if not force and self._metadata and self._metadata.expires_at > now:
                return self._metadata.value
            issuer = settings.oidc_issuer.rstrip("/")
            url = f"{issuer}/.well-known/openid-configuration"
            payload = await self._fetch_json(url)
            if payload.get("issuer") != settings.oidc_issuer:
                raise AuthenticationError("OIDC discovery issuer does not match CODO_OIDC_ISSUER")
            jwks_uri = payload.get("jwks_uri")
            if not isinstance(jwks_uri, str) or not jwks_uri:
                raise AuthenticationError("OIDC discovery document has no jwks_uri")
            self._validate_remote_url(jwks_uri)
            self._metadata = _CacheEntry(payload, now + settings.oidc_cache_seconds)
            return payload

    async def _get_jwks(self, force: bool = False) -> dict[str, Any]:
        now = time.monotonic()
        if not force and self._jwks and self._jwks.expires_at > now:
            return self._jwks.value
        metadata = await self._get_metadata(force=force)
        payload = await self._fetch_json(str(metadata["jwks_uri"]))
        if not isinstance(payload.get("keys"), list):
            raise AuthenticationError("OIDC JWKS response has no keys array")
        self._jwks = _CacheEntry(payload, now + settings.oidc_cache_seconds)
        return payload

    async def _fetch_json(self, url: str) -> dict[str, Any]:
        self._validate_remote_url(url)
        timeout = httpx.Timeout(settings.oidc_http_timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
                response = await client.get(url, headers={"Accept": "application/json"})
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AuthenticationError("Unable to retrieve OIDC metadata") from exc
        if not isinstance(payload, dict):
            raise AuthenticationError("OIDC endpoint returned an invalid JSON object")
        return payload

    def _validate_remote_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" and not settings.oidc_allow_insecure_http:
            raise AuthenticationError("OIDC endpoints must use HTTPS")
        if not parsed.hostname:
            raise AuthenticationError("OIDC endpoint URL is invalid")


oidc_authenticator = OidcAuthenticator()
