from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent


@dataclass
class StepResult:
    key: str
    passed: bool
    blocking: bool
    detail: str


def release_plan(*, bootstrap_super_admin: bool, run_e2e: bool, require_document: bool, provider: str = "postgres") -> list[dict[str, Any]]:
    steps = [
        {"key": "migrations", "blocking": True, "description": "Apply immutable SQL migrations and verify historical checksums."},
    ]
    if bootstrap_super_admin:
        steps.append(
            {
                "key": "bootstrap-super-admin",
                "blocking": True,
                "description": "Grant SUPER_ADMIN to the explicitly supplied OIDC subject.",
            }
        )
    steps.append(
        {
            "key": "preflight",
            "blocking": True,
            "description": "Verify schema, migrations, storage, OIDC/JWKS and administrative recovery.",
        }
    )
    if provider == "supabase":
        steps.append(
            {
                "key": "provider-security",
                "blocking": True,
                "description": "Verify Supabase RLS and ensure CODO tables are not exposed through Data API roles.",
            }
        )
    if run_e2e:
        steps.append(
            {
                "key": "e2e",
                "blocking": True,
                "description": "Check deployed API contracts, identities and published corpus chain.",
            }
        )
        if require_document:
            steps.append(
                {
                    "key": "published-document", 
                    "blocking": True,
                    "description": "Require document, provenance, publication receipt and legal relationships endpoints.",
                }
            )
    return steps


def _redact(value: str) -> str:
    value = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]+", "Bearer ***", value)
    value = re.sub(r"(?i)(postgres(?:ql)?://)([^@\s]+)@", r"\1***@", value)
    value = re.sub(r"(?i)(CODO_[A-Z0-9_]*(?:TOKEN|PASSWORD|API_KEY)=)[^\s]+", r"\1***", value)
    return value.strip()


def _run_command(key: str, command: list[str], *, env: dict[str, str], blocking: bool = True) -> StepResult:
    completed = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    detail = _redact(combined[-6000:] if combined else f"exit={completed.returncode}")
    return StepResult(key=key, passed=completed.returncode == 0, blocking=blocking, detail=detail)


def _open_release_run(database_url: str, release_label: str, environment: str) -> int | None:
    if not database_url:
        return None
    try:
        import psycopg
    except ImportError:
        return None
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into staging_release_runs(release_label, environment_name, status, initiated_by, metadata)
                values (%s,%s,'running',%s,%s::jsonb)
                returning id
                """,
                (
                    release_label,
                    environment,
                    os.getenv("CODO_RELEASE_ACTOR") or "staging-release-script",
                    json.dumps({"tool": "backend/scripts/staging_release.py"}),
                ),
            )
            release_id = int(cur.fetchone()[0])
        conn.commit()
    return release_id


def _record_check(database_url: str, release_id: int | None, step: StepResult) -> None:
    if not database_url or release_id is None:
        return
    try:
        import psycopg
    except ImportError:
        return
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into staging_release_checks(release_run_id, check_key, passed, blocking, detail)
                values (%s,%s,%s,%s,%s)
                on conflict (release_run_id, check_key) do update set
                  passed=excluded.passed,
                  blocking=excluded.blocking,
                  detail=excluded.detail,
                  checked_at=now()
                """,
                (release_id, step.key, step.passed, step.blocking, step.detail[-8000:]),
            )
        conn.commit()


def _close_release_run(database_url: str, release_id: int | None, status: str) -> None:
    if not database_url or release_id is None:
        return
    try:
        import psycopg
    except ImportError:
        return
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "update staging_release_runs set status=%s, completed_at=now() where id=%s",
                (status, release_id),
            )
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="CODO staging release gate")
    parser.add_argument("--release-label", default="increment-08")
    parser.add_argument("--environment", default="staging")
    parser.add_argument("--api-base")
    parser.add_argument("--provider", choices=("postgres", "supabase"), default=os.getenv("CODO_DATABASE_PROVIDER", "postgres"))
    parser.add_argument("--document-id")
    parser.add_argument("--query", default="Constitution")
    parser.add_argument("--bootstrap-super-admin-subject")
    parser.add_argument("--skip-e2e", action="store_true")
    parser.add_argument("--require-published-document", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--report", default=str(PROJECT_DIR / "staging-release-report.json"))
    args = parser.parse_args()

    run_e2e = not args.skip_e2e
    plan = release_plan(
        bootstrap_super_admin=bool(args.bootstrap_super_admin_subject),
        run_e2e=run_e2e,
        require_document=args.require_published_document,
        provider=args.provider,
    )
    if args.plan:
        print(json.dumps({"release_label": args.release_label, "environment": args.environment, "provider": args.provider, "steps": plan}, indent=2))
        return 0

    database_url = os.getenv("CODO_DATABASE_URL", "")
    if not database_url:
        raise SystemExit("CODO_DATABASE_URL is required for an executable staging release")
    if run_e2e and not args.api_base:
        raise SystemExit("--api-base is required unless --skip-e2e is used")
    if args.require_published_document and not args.document_id:
        raise SystemExit("--document-id is required with --require-published-document")

    env = dict(os.environ)
    results: list[StepResult] = []
    release_id: int | None = None

    migration = _run_command("migrations", [sys.executable, "scripts/migrate.py"], env=env)
    results.append(migration)
    if migration.passed:
        try:
            release_id = _open_release_run(database_url, args.release_label, args.environment)
            _record_check(database_url, release_id, migration)
        except Exception as exc:
            results.append(StepResult("release-audit-log", False, True, _redact(str(exc))))

    if migration.passed and args.bootstrap_super_admin_subject:
        bootstrap = _run_command(
            "bootstrap-super-admin",
            [sys.executable, "scripts/grant_admin_role.py", args.bootstrap_super_admin_subject, "SUPER_ADMIN"],
            env=env,
        )
        results.append(bootstrap)
        _record_check(database_url, release_id, bootstrap)

    if migration.passed:
        preflight = _run_command("preflight", [sys.executable, "scripts/staging_preflight.py"], env=env)
        results.append(preflight)
        _record_check(database_url, release_id, preflight)

    if migration.passed and args.provider == "supabase" and all(r.passed for r in results if r.blocking):
        provider_security = _run_command(
            "provider-security",
            [sys.executable, "scripts/supabase_preflight.py", "--json"],
            env=env,
        )
        results.append(provider_security)
        _record_check(database_url, release_id, provider_security)

    if run_e2e and migration.passed and all(r.passed for r in results if r.blocking):
        command = [sys.executable, "scripts/e2e_staging.py", "--api-base", args.api_base, "--query", args.query]
        if args.document_id:
            command += ["--document-id", args.document_id]
        e2e = _run_command("e2e", command, env=env)
        results.append(e2e)
        _record_check(database_url, release_id, e2e)
        if args.require_published_document:
            corpus_passed = e2e.passed and bool(args.document_id)
            corpus = StepResult(
                "published-document",
                corpus_passed,
                True,
                "Document/provenance/publication-receipt/relationships were included in E2E checks."
                if corpus_passed
                else "Published corpus chain did not pass E2E checks.",
            )
            results.append(corpus)
            _record_check(database_url, release_id, corpus)

    blocking_failures = [item for item in results if item.blocking and not item.passed]
    status = "failed" if blocking_failures else "passed"
    try:
        _close_release_run(database_url, release_id, status)
    except Exception as exc:
        results.append(StepResult("release-audit-close", False, True, _redact(str(exc))))
        status = "failed"

    report = {
        "release_label": args.release_label,
        "environment": args.environment,
        "provider": args.provider,
        "status": status,
        "release_run_id": release_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": [asdict(item) for item in results],
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if status != "passed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
