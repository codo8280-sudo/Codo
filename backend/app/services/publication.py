from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_publication_payload(
    document: dict[str, Any],
    articles: list[dict[str, Any]],
    source_snapshot_hash: str,
) -> dict[str, Any]:
    ordered_articles = sorted(
        articles,
        key=lambda row: (int(row.get("sort_order") or 0), str(row.get("codo_id") or "")),
    )
    return {
        "document": {
            "codo_id": document["codo_id"],
            "version_key": document["version_key"],
            "status": document["status"],
            "official_text": document["official_text"],
            "valid_from": _iso(document.get("valid_from")),
            "valid_to": _iso(document.get("valid_to")),
        },
        "articles": [
            {
                "codo_id": row["codo_id"],
                "label": row["article_label"],
                "status": row["status"],
                "official_text": row["official_text"],
                "valid_from": _iso(row.get("valid_from")),
                "valid_to": _iso(row.get("valid_to")),
                "sort_order": int(row.get("sort_order") or 0),
            }
            for row in ordered_articles
        ],
        "source_snapshot_hash": source_snapshot_hash,
    }


def publication_hash(
    document: dict[str, Any],
    articles: list[dict[str, Any]],
    source_snapshot_hash: str,
) -> str:
    payload = canonical_publication_payload(document, articles, source_snapshot_hash)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    isoformat = getattr(value, "isoformat", None)
    return isoformat() if callable(isoformat) else str(value)
