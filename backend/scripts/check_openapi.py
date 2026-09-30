from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return json.loads(text)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit("OpenAPI snapshot is not an object")
    return data


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "openapi.yaml"
    committed = _load(path)
    generated = app.openapi()
    if committed != generated:
        raise SystemExit("OpenAPI snapshot is stale. Run: PYTHONPATH=backend python backend/scripts/export_openapi.py")
    print(f"openapi_snapshot=ok paths={len(generated.get('paths', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
