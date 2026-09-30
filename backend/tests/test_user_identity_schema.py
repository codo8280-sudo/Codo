from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_oidc_subject_is_namespaced_by_issuer() -> None:
    migration = (ROOT / "postgres/008_oidc_subject_namespace.sql").read_text(encoding="utf-8")
    service = (ROOT / "app/services/user_identity.py").read_text(encoding="utf-8")
    assert "on user_profiles(auth_issuer, auth_subject)" in migration
    assert "on conflict (auth_issuer, auth_subject)" in service


def test_deleted_identity_digest_is_non_linkable() -> None:
    service = (ROOT / "app/services/user_identity.py").read_text(encoding="utf-8")
    assert "secrets.token_bytes(32)" in service
    assert "privacy_events" in service
