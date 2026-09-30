from __future__ import annotations

from collections.abc import Iterable


def source_set_is_sufficient(trust_levels: Iterable[str]) -> bool:
    levels = [level for level in trust_levels if level]
    if not levels:
        return False
    if any(level == "D" for level in levels):
        return False
    # Level C is complementary. A legal conclusion needs at least one
    # official primary or institutional reproduction source (A or B).
    return any(level in {"A", "B"} for level in levels)


def normalize_question(value: str) -> str:
    return " ".join(value.strip().split())


def host_is_allowed(requested_url: str, official_url: str) -> bool:
    import urllib.parse

    def canonical(value: str) -> str:
        host = (urllib.parse.urlparse(value).hostname or "").lower().rstrip(".")
        return host[4:] if host.startswith("www.") else host

    requested = canonical(requested_url)
    official = canonical(official_url)
    if not requested or not official:
        return False
    return requested == official or requested.endswith("." + official)


INGESTION_TRANSITIONS = {
    "imported": {"to_analyze"},
    "to_analyze": {"structured"},
    "structured": {"sources_verified"},
    "sources_verified": {"legal_review"},
    "legal_review": {"validated"},
    "validated": {"published"},
    "published": {"monitored"},
    "monitored": set(),
    "failed": set(),
}


def ingestion_transition_allowed(current: str, target: str) -> bool:
    return target in INGESTION_TRANSITIONS.get(current, set())
