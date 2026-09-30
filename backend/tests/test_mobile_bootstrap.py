from __future__ import annotations

import importlib.util
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tool_configure_oidc.py"


def _module():
    spec = importlib.util.spec_from_file_location("codo_tool_configure_oidc", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_android_oidc_bootstrap_sets_scheme_and_min_sdk(tmp_path: Path) -> None:
    module = _module()
    module.ROOT = tmp_path
    target = tmp_path / "android/app/build.gradle.kts"
    target.parent.mkdir(parents=True)
    target.write_text(
        "android {\n  defaultConfig {\n    minSdk = flutter.minSdkVersion\n  }\n}\n",
        encoding="utf-8",
    )

    result = module.patch_android()
    text = target.read_text(encoding="utf-8")
    assert "appAuthRedirectScheme" in text
    assert "minSdk = 24" in text
    assert "redirect-scheme" in result


def test_ios_oidc_bootstrap_sets_scheme_and_min_version(tmp_path: Path) -> None:
    module = _module()
    module.ROOT = tmp_path
    plist = tmp_path / "ios/Runner/Info.plist"
    plist.parent.mkdir(parents=True)
    with plist.open("wb") as handle:
        plistlib.dump({"CFBundleName": "CODO"}, handle)
    podfile = tmp_path / "ios/Podfile"
    podfile.write_text("# platform :ios, '12.0'\n", encoding="utf-8")

    result = module.patch_ios()
    with plist.open("rb") as handle:
        data = plistlib.load(handle)
    schemes = [
        scheme
        for item in data.get("CFBundleURLTypes", [])
        for scheme in item.get("CFBundleURLSchemes", [])
    ]
    assert "ci.codo.app" in schemes
    assert "platform :ios, '13.0'" in podfile.read_text(encoding="utf-8")
    assert "redirect-scheme" in result
