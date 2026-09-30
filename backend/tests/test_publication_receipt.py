from __future__ import annotations

from datetime import date

from app.services.publication import canonical_publication_payload, publication_hash


def _document():
    return {
        "codo_id": "CODO-CI-CONST-2016",
        "version_key": "consolidated-2023",
        "status": "in_force",
        "official_text": "Texte constitutionnel",
        "valid_from": date(2023, 7, 25),
        "valid_to": None,
    }


def _articles():
    return [
        {
            "codo_id": "CODO-CI-CONST-2016-ART-002",
            "article_label": "Article 2",
            "status": "in_force",
            "official_text": "Deuxième article",
            "valid_from": None,
            "valid_to": None,
            "sort_order": 2,
        },
        {
            "codo_id": "CODO-CI-CONST-2016-ART-001",
            "article_label": "Article 1",
            "status": "in_force",
            "official_text": "Premier article",
            "valid_from": None,
            "valid_to": None,
            "sort_order": 1,
        },
    ]


def test_publication_hash_is_stable_and_order_independent():
    source_hash = "a" * 64
    first = publication_hash(_document(), _articles(), source_hash)
    second = publication_hash(_document(), list(reversed(_articles())), source_hash)
    assert first == second
    assert len(first) == 64


def test_publication_hash_changes_when_official_text_changes():
    source_hash = "a" * 64
    articles = _articles()
    first = publication_hash(_document(), articles, source_hash)
    articles[0]["official_text"] = "Texte modifié"
    assert publication_hash(_document(), articles, source_hash) != first


def test_canonical_payload_carries_source_hash():
    source_hash = "b" * 64
    payload = canonical_publication_payload(_document(), _articles(), source_hash)
    assert payload["source_snapshot_hash"] == source_hash
    assert [a["codo_id"] for a in payload["articles"]] == [
        "CODO-CI-CONST-2016-ART-001",
        "CODO-CI-CONST-2016-ART-002",
    ]
