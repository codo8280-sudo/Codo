from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from uuid import uuid4


def main() -> int:
    parser = argparse.ArgumentParser(description="Load reviewed-source relationship candidates without publishing them.")
    parser.add_argument(
        "--manifest",
        default="backend/manifests/ci_constitution_relationship_candidates.json",
    )
    args = parser.parse_args()

    database_url = os.getenv("CODO_DATABASE_URL", "")
    if not database_url:
        raise SystemExit("CODO_DATABASE_URL is required")

    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("Install backend/requirements.txt before running this script") from exc

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    relationships = manifest.get("relationships", [])
    if not relationships:
        raise SystemExit("Manifest contains no relationship candidates")

    inserted = 0
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for item in relationships:
                cur.execute(
                    """
                    select source_key, trust_level, verified_at
                    from legal_sources where source_key=%s and active=true
                    """,
                    (item["evidence_source_key"],),
                )
                source = cur.fetchone()
                if not source or source["verified_at"] is None or source["trust_level"] not in {"A", "B", "C"}:
                    raise SystemExit(f"Evidence source is not verified: {item['evidence_source_key']}")
                cur.execute(
                    """
                    insert into legal_relationship_candidates(
                      id, from_document_codo_id, relation_type, to_document_codo_id,
                      effective_date, evidence_source_key, evidence_url, note, created_by
                    ) values (%s,%s,%s,%s,%s,%s,%s,%s,'manifest-bootstrap')
                    on conflict (from_document_codo_id, relation_type, to_document_codo_id, evidence_source_key)
                    do update set
                      effective_date=excluded.effective_date,
                      evidence_url=excluded.evidence_url,
                      note=excluded.note
                    where legal_relationship_candidates.status='pending'
                    """,
                    (
                        str(uuid4()),
                        item["from_document_codo_id"],
                        item["relation_type"],
                        item["to_document_codo_id"],
                        item.get("effective_date"),
                        item["evidence_source_key"],
                        item.get("evidence_url"),
                        item.get("note"),
                    ),
                )
                inserted += 1
        conn.commit()

    print(f"Loaded {inserted} pending relationship candidate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
