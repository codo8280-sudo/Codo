from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app.auth import AuthenticationError, OidcAuthenticator


def _settings(**overrides):
    base = dict(
        oidc_configured=True,
        oidc_issuer="https://id.example.test",
        oidc_audience="codo-api",
        oidc_algorithms=("RS256",),
        oidc_cache_seconds=300,
        oidc_clock_skew_seconds=0,
        oidc_http_timeout_seconds=5,
        oidc_allow_insecure_http=False,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _token(private_key, audience="codo-api", issuer="https://id.example.test", algorithm="RS256"):
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": "user-123",
            "iss": issuer,
            "aud": audience,
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm=algorithm,
        headers={"kid": "key-1"},
    )


@pytest.mark.asyncio
async def test_oidc_verifies_signature_issuer_and_audience(monkeypatch):
    from app import auth as module

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk["kid"] = "key-1"
    monkeypatch.setattr(module, "settings", _settings())

    authenticator = OidcAuthenticator()

    async def fake_jwks(force=False):
        del force
        return {"keys": [public_jwk]}

    monkeypatch.setattr(authenticator, "_get_jwks", fake_jwks)
    claims = await authenticator.verify(_token(private_key))
    assert claims["sub"] == "user-123"


@pytest.mark.asyncio
async def test_oidc_rejects_wrong_audience(monkeypatch):
    from app import auth as module

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk["kid"] = "key-1"
    monkeypatch.setattr(module, "settings", _settings())
    authenticator = OidcAuthenticator()

    async def fake_jwks(force=False):
        del force
        return {"keys": [public_jwk]}

    monkeypatch.setattr(authenticator, "_get_jwks", fake_jwks)
    with pytest.raises(AuthenticationError):
        await authenticator.verify(_token(private_key, audience="other-api"))


@pytest.mark.asyncio
async def test_oidc_rejects_wrong_issuer(monkeypatch):
    from app import auth as module

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk["kid"] = "key-1"
    monkeypatch.setattr(module, "settings", _settings())
    authenticator = OidcAuthenticator()

    async def fake_jwks(force=False):
        del force
        return {"keys": [public_jwk]}

    monkeypatch.setattr(authenticator, "_get_jwks", fake_jwks)
    with pytest.raises(AuthenticationError):
        await authenticator.verify(_token(private_key, issuer="https://evil.example.test"))


@pytest.mark.asyncio
async def test_oidc_rejects_algorithm_not_allowlisted(monkeypatch):
    from app import auth as module

    monkeypatch.setattr(module, "settings", _settings())
    authenticator = OidcAuthenticator()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": "https://id.example.test",
            "aud": "codo-api",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        "not-a-production-secret-with-more-than-32-bytes",
        algorithm="HS256",
        headers={"kid": "key-1"},
    )
    with pytest.raises(AuthenticationError, match="algorithm"):
        await authenticator.verify(token)
