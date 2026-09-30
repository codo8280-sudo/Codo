#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT"

printf '%s\n' '[CODO] Python syntax'
PYTHONPATH=backend python -m compileall -q backend/app backend/scripts backend/tests

printf '%s\n' '[CODO] Backend tests'
PYTHONPATH=backend python -m pytest -q backend/tests

printf '%s\n' '[CODO] OpenAPI snapshot'
PYTHONPATH=backend python backend/scripts/check_openapi.py

printf '%s\n' '[CODO] Dart relative import integrity'
python - <<'PY'
from pathlib import Path
import re
root=Path('lib')
missing=[]
for path in root.rglob('*.dart'):
    text=path.read_text(encoding='utf-8')
    for match in re.finditer(r"import\s+['\"]([^'\"]+)['\"]", text):
        ref=match.group(1)
        if ref.startswith(('dart:','package:')):
            continue
        target=(path.parent/ref).resolve()
        if not target.exists():
            missing.append(f'{path}: {ref}')
if missing:
    raise SystemExit('Missing Dart relative imports:\n'+'\n'.join(missing))
print(f'dart_relative_imports=ok files={len(list(root.rglob("*.dart")))}')
PY

if command -v flutter >/dev/null 2>&1; then
  printf '%s\n' '[CODO] Flutter dependencies'
  flutter pub get
  printf '%s\n' '[CODO] Flutter format'
  dart format --output=none --set-exit-if-changed lib
  printf '%s\n' '[CODO] Flutter analyze'
  flutter analyze
  if [ -d test ]; then
    printf '%s\n' '[CODO] Flutter tests'
    flutter test
  fi
else
  if [ "${CODO_CI_REQUIRE_FLUTTER:-false}" = "true" ]; then
    printf '%s\n' 'Flutter SDK is required but not installed.' >&2
    exit 1
  fi
  printf '%s\n' '[CODO] Flutter SDK absent: Flutter checks skipped (set CODO_CI_REQUIRE_FLUTTER=true to make this blocking).'
fi
