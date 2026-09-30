from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def request_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def endpoint(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Acquire the first official CODO corpus candidate, extract it and generate a review draft. "
            "This script intentionally stops before structuring, legal validation and publication."
        )
    )
    parser.add_argument("--api-base", required=True)
    parser.add_argument("--admin-token", required=True)
    parser.add_argument(
        "--manifest",
        default="backend/manifests/ci_constitution_2016_consolidated_2023.json",
    )
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    source = manifest["primary_source"]
    metadata = manifest["document_metadata"]

    acquired = request_json(
        "POST",
        endpoint(args.api_base, "/v1/admin/ingestion/acquire"),
        args.admin_token,
        {"source_key": source["source_key"], "source_url": source["source_url"]},
    )
    job_id = acquired["job_id"]
    print(json.dumps({"stage": "acquired", **acquired}, ensure_ascii=False, indent=2))

    extracted = request_json(
        "POST",
        endpoint(args.api_base, f"/v1/admin/ingestion/{job_id}/extract"),
        args.admin_token,
        {},
    )
    print(json.dumps({"stage": "extracted", **extracted}, ensure_ascii=False, indent=2))

    draft = request_json(
        "POST",
        endpoint(args.api_base, f"/v1/admin/ingestion/{job_id}/draft"),
        args.admin_token,
        metadata,
    )
    print(json.dumps({"stage": "draft", "job_id": job_id, **draft}, ensure_ascii=False, indent=2))
    print(
        "STOP: human documentary/legal review is required before /structure, legal-decision, validation and publication.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
