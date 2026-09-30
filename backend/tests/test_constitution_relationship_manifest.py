from __future__ import annotations

import json
from pathlib import Path


def test_constitution_relationship_manifest_is_candidate_only():
    path = Path(__file__).resolve().parents[1] / "manifests" / "ci_constitution_relationship_candidates.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["policy"] == "candidate_only_until_human_validation"
    relationships = payload["relationships"]
    assert len(relationships) == 2
    assert {item["effective_date"] for item in relationships} == {"2020-03-19", "2023-07-25"}
    assert all(item["relation_type"] == "modifies" for item in relationships)
    assert all(item["to_document_codo_id"] == "CODO-CI-CONSTITUTION-2016-886" for item in relationships)
