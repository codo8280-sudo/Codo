from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def main() -> int:
    target = Path(__file__).resolve().parents[1] / "openapi.yaml"
    schema = app.openapi()
    try:
        import yaml
    except ImportError:
        # JSON is valid YAML 1.2; retain the historical filename while avoiding
        # a hard runtime dependency in production.
        target.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        target.write_text(
            yaml.safe_dump(schema, allow_unicode=True, sort_keys=False, width=120),
            encoding="utf-8",
        )
    print(f"openapi_path={target}")
    print(f"openapi_paths={len(schema.get('paths', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
