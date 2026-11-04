#!/usr/bin/env python3
"""Bump post-phase14 user-approved APK to 3.13.0 without changing signing or data."""
from pathlib import Path
app = Path("AgendaClara/app/build.gradle")
old = app.read_text(encoding="utf-8")
if "versionCode 56" in old and "versionName '3.13.0'" in old:
    print("PASS 3.13.0 already staged")
else:
    if old.count("versionCode 55") != 1 or old.count("versionName '3.12.0'") != 1:
        raise RuntimeError("Unexpected existing version; refusing dangerous or ambiguous upgrade")
    updated = old.replace("versionCode 55", "versionCode 56", 1).replace(
        "versionName '3.12.0'", "versionName '3.13.0'", 1)
    if "applicationId 'pe.agendaclara.app'" not in updated:
        raise RuntimeError("App identifier changed unexpectedly")
    if "signingConfig signingConfigs.development" not in updated:
        raise RuntimeError("Existing signing key configuration changed")
    app.write_text(updated, encoding="utf-8")
    print("PASS version 3.13.0 (code 56); package and signing unchanged")
