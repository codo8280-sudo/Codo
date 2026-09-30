from __future__ import annotations

import argparse
import os
import sys

import httpx


def _headers(token: str | None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="CODO staging end-to-end contract checks")
    parser.add_argument("--api-base", required=True)
    parser.add_argument("--user-token", default=os.getenv("CODO_E2E_USER_TOKEN"))
    parser.add_argument("--admin-token", default=os.getenv("CODO_E2E_ADMIN_TOKEN"))
    parser.add_argument("--document-id")
    parser.add_argument("--query", default="Constitution")
    args = parser.parse_args()

    base = args.api_base.rstrip("/")
    failures: list[str] = []
    passes: list[str] = []

    def require(condition: bool, name: str, detail: str = "") -> None:
        if condition:
            passes.append(name + (f": {detail}" if detail else ""))
        else:
            failures.append(name + (f": {detail}" if detail else ""))

    with httpx.Client(timeout=20, follow_redirects=False) as client:
        try:
            response = client.get(f"{base}/health/live")
            require(response.status_code == 200, "liveness", f"status={response.status_code}")
        except httpx.HTTPError as exc:
            failures.append(f"liveness: {exc}")
            response = None

        try:
            ready = client.get(f"{base}/health/ready")
            require(ready.status_code == 200, "readiness", f"status={ready.status_code} body={ready.text[:300]}")
        except httpx.HTTPError as exc:
            failures.append(f"readiness: {exc}")

        try:
            search = client.get(f"{base}/v1/search", params={"q": args.query})
            require(search.status_code == 200, "public-search", f"status={search.status_code}")
            if search.status_code == 200:
                payload = search.json()
                require(isinstance(payload.get("results"), list), "public-search-shape")
        except (httpx.HTTPError, ValueError) as exc:
            failures.append(f"public-search: {exc}")

        if args.user_token:
            try:
                profile = client.get(f"{base}/v1/me", headers=_headers(args.user_token))
                require(profile.status_code == 200, "user-profile", f"status={profile.status_code}")
                if profile.status_code == 200:
                    data = profile.json()
                    require(bool(data.get("auth_subject")), "user-profile-subject")
            except (httpx.HTTPError, ValueError) as exc:
                failures.append(f"user-profile: {exc}")

        if args.admin_token:
            try:
                admin = client.get(f"{base}/v1/admin/me", headers=_headers(args.admin_token))
                require(admin.status_code == 200, "admin-profile", f"status={admin.status_code}")
                if admin.status_code == 200:
                    require(bool(admin.json().get("roles")), "admin-roles")
            except (httpx.HTTPError, ValueError) as exc:
                failures.append(f"admin-profile: {exc}")

        if args.document_id:
            encoded = httpx.URL(f"{base}/v1/documents/{args.document_id}")
            try:
                document = client.get(encoded)
                require(document.status_code == 200, "document", f"status={document.status_code}")
                provenance = client.get(f"{base}/v1/documents/{args.document_id}/provenance")
                require(provenance.status_code == 200, "provenance", f"status={provenance.status_code}")
                if provenance.status_code == 200:
                    sources = provenance.json().get("sources", [])
                    require(bool(sources), "provenance-has-sources")
                    for item in sources:
                        digest = str(item.get("content_hash", ""))
                        require(len(digest) == 64, "provenance-sha256", digest[:16])
                        require(item.get("trust_level") in {"A", "B", "C"}, "provenance-trust-level")
                receipt = client.get(f"{base}/v1/documents/{args.document_id}/publication-receipt")
                require(receipt.status_code == 200, "publication-receipt", f"status={receipt.status_code}")
                if receipt.status_code == 200:
                    receipt_data = receipt.json()
                    require(len(str(receipt_data.get("publication_hash", ""))) == 64, "publication-receipt-hash")
                    require(len(str(receipt_data.get("source_snapshot_hash", ""))) == 64, "publication-source-hash")
                relationships = client.get(f"{base}/v1/legal/documents/{args.document_id}/relationships")
                require(relationships.status_code == 200, "relationships", f"status={relationships.status_code}")
            except (httpx.HTTPError, ValueError) as exc:
                failures.append(f"document-chain: {exc}")

    for item in passes:
        print("PASS", item)
    for item in failures:
        print("FAIL", item)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
