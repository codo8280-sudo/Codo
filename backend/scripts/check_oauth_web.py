from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "oauth_web"
HTML = (WEB / "oauth" / "consent" / "index.html").read_text(encoding="utf-8")
JS = (WEB / "assets" / "consent.js").read_text(encoding="utf-8")

required = [
    WEB / "index.html",
    WEB / "oauth" / "consent" / "index.html",
    WEB / "assets" / "app.css",
    WEB / "assets" / "consent.js",
    WEB / "robots.txt",
    WEB / ".nojekyll",
]
missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:
    raise SystemExit("oauth_web missing files: " + ", ".join(missing))

for forbidden in ("sb_secret_", "service_role", "SUPABASE_SERVICE_ROLE", "innerHTML", "document.write", "eval("):
    if forbidden in HTML or forbidden in JS:
        raise SystemExit(f"oauth_web forbidden token: {forbidden}")

if "sb_publishable_" not in JS:
    raise SystemExit("oauth_web must use a publishable Supabase key")
if "sessionStorage" not in JS or "localStorage" in JS:
    raise SystemExit("oauth_web session storage policy violated")
if "frame-ancestors 'none'" not in HTML:
    raise SystemExit("oauth_web CSP frame protection missing")
if "https://evchtqxpthfaekpaeibh.supabase.co" not in HTML or "https://evchtqxpthfaekpaeibh.supabase.co" not in JS:
    raise SystemExit("oauth_web staging Supabase origin mismatch")
if "ci.codo.app:/oauthredirect" not in JS:
    raise SystemExit("oauth_web mobile redirect allowlist missing")
for endpoint in (
    "/token?grant_type=password",
    "/token?grant_type=refresh_token",
    "/oauth/authorizations/",
    "/consent",
):
    if endpoint not in JS:
        raise SystemExit(f"oauth_web OAuth endpoint contract missing: {endpoint}")

print("oauth_web_contract=ok")
