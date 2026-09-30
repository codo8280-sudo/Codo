from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEME = "ci.codo.app"
ANDROID_MIN_SDK = 24
IOS_MIN_VERSION = "13.0"


def patch_android() -> str:
    candidates = [
        ROOT / "android/app/build.gradle.kts",
        ROOT / "android/app/build.gradle",
    ]
    target = next((p for p in candidates if p.exists()), None)
    if target is None:
        return "android=not-generated"

    text = target.read_text(encoding="utf-8")
    changes: list[str] = []

    if "appAuthRedirectScheme" not in text:
        marker = "defaultConfig {"
        if marker not in text:
            raise RuntimeError(f"Cannot find defaultConfig in {target}")
        if target.suffix == ".kts":
            addition = f'\n        manifestPlaceholders["appAuthRedirectScheme"] = "{SCHEME}"'
        else:
            addition = f"\n        manifestPlaceholders += [appAuthRedirectScheme: '{SCHEME}']"
        text = text.replace(marker, marker + addition, 1)
        changes.append("redirect-scheme")

    # flutter_appauth 12.x requires Android API 24+. Flutter templates may
    # inherit flutter.minSdkVersion, so replace that expression explicitly.
    replacements = [
        ("minSdk = flutter.minSdkVersion", f"minSdk = {ANDROID_MIN_SDK}"),
        ("minSdkVersion flutter.minSdkVersion", f"minSdkVersion {ANDROID_MIN_SDK}"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changes.append(f"min-sdk-{ANDROID_MIN_SDK}")
            break

    target.write_text(text, encoding="utf-8")
    state = ",".join(changes) if changes else "already-configured"
    return f"android={state}:{target.relative_to(ROOT)}"


def patch_ios() -> str:
    messages: list[str] = []

    target = ROOT / "ios/Runner/Info.plist"
    if not target.exists():
        messages.append("not-generated")
    else:
        with target.open("rb") as handle:
            data = plistlib.load(handle)
        url_types = list(data.get("CFBundleURLTypes", []))
        has_scheme = any(
            isinstance(item, dict) and SCHEME in item.get("CFBundleURLSchemes", [])
            for item in url_types
        )
        if not has_scheme:
            url_types.append({"CFBundleTypeRole": "Editor", "CFBundleURLSchemes": [SCHEME]})
            data["CFBundleURLTypes"] = url_types
            with target.open("wb") as handle:
                plistlib.dump(data, handle, sort_keys=False)
            messages.append("redirect-scheme")

    podfile = ROOT / "ios/Podfile"
    if podfile.exists():
        pod_text = podfile.read_text(encoding="utf-8")
        import re
        platform_pattern = re.compile(r"^\s*#?\s*platform\s*:ios,\s*['\"]([^'\"]+)['\"]", re.MULTILINE)
        match = platform_pattern.search(pod_text)
        desired = f"platform :ios, '{IOS_MIN_VERSION}'"
        if match:
            try:
                current = tuple(int(x) for x in match.group(1).split("."))
            except ValueError:
                current = (0,)
            if current < (13, 0):
                pod_text = platform_pattern.sub(desired, pod_text, count=1)
                podfile.write_text(pod_text, encoding="utf-8")
                messages.append("min-ios-13")
        else:
            podfile.write_text(desired + "\n" + pod_text, encoding="utf-8")
            messages.append("min-ios-13")

    state = ",".join(messages) if messages else "already-configured"
    return f"ios={state}"



if __name__ == "__main__":
    print(patch_android())
    print(patch_ios())
