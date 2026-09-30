from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage"


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("CODO_DATABASE_URL", "")
    database_provider: str = os.getenv("CODO_DATABASE_PROVIDER", "postgres").strip().lower() or "postgres"
    public_max_results: int = _int("CODO_PUBLIC_MAX_RESULTS", 20)
    storage_dir: Path = Path(os.getenv("CODO_STORAGE_DIR", str(DEFAULT_STORAGE_DIR)))
    acquisition_max_bytes: int = _int("CODO_ACQUISITION_MAX_BYTES", 50 * 1024 * 1024)

    embedding_url: str = os.getenv("CODO_EMBEDDING_URL", "")
    embedding_api_key: str = os.getenv("CODO_EMBEDDING_API_KEY", "")
    embedding_model: str = os.getenv("CODO_EMBEDDING_MODEL", "")

    llm_url: str = os.getenv("CODO_LLM_URL", "")
    llm_api_key: str = os.getenv("CODO_LLM_API_KEY", "")
    llm_model: str = os.getenv("CODO_LLM_MODEL", "")

    admin_bootstrap_token: str = os.getenv("CODO_ADMIN_BOOTSTRAP_TOKEN", "")

    oidc_issuer: str = os.getenv("CODO_OIDC_ISSUER", "")
    oidc_audience: str = os.getenv("CODO_OIDC_AUDIENCE", "")
    oidc_algorithms: tuple[str, ...] = tuple(
        item.strip() for item in os.getenv("CODO_OIDC_ALGORITHMS", "RS256").split(",") if item.strip()
    )
    oidc_cache_seconds: int = _int("CODO_OIDC_CACHE_SECONDS", 300)
    oidc_clock_skew_seconds: int = _int("CODO_OIDC_CLOCK_SKEW_SECONDS", 30)
    oidc_http_timeout_seconds: int = _int("CODO_OIDC_HTTP_TIMEOUT_SECONDS", 5)
    oidc_allow_insecure_http: bool = os.getenv("CODO_OIDC_ALLOW_INSECURE_HTTP", "false").lower() == "true"

    @property
    def database_configured(self) -> bool:
        return bool(self.database_url)

    @property
    def semantic_search_configured(self) -> bool:
        return bool(self.embedding_url and self.embedding_model)

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_url and self.llm_model)

    @property
    def oidc_configured(self) -> bool:
        return bool(self.oidc_issuer and self.oidc_audience and self.oidc_algorithms)


settings = Settings()
