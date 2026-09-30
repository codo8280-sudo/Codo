#!/bin/sh
set -eu
command -v flutter >/dev/null 2>&1 || { echo "Flutter SDK is required." >&2; exit 1; }
flutter create --platforms=android,ios --org ci.codo .
python tool_configure_oidc.py
flutter pub get
flutter analyze
