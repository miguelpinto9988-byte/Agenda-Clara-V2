#!/usr/bin/env python3
"""Version the approved design as an update to Agenda Clara 3.11.3.

Applied after phase55 to preserve sequential checksum patches.
Never changes app ID, signing or data paths.
"""
from pathlib import Path

gradle = Path("AgendaClara/app/build.gradle")
if not gradle.is_file():
    raise RuntimeError("Reconstruct sources first")

text = gradle.read_text(encoding="utf-8")
if "versionCode 55" in text and "versionName '3.12.0'" in text:
    print("PASS version 3.12.0 already set")
else:
    if text.count("versionCode 54") != 1 or text.count("versionName '3.11.3'") != 1:
        raise RuntimeError("Unexpected app version: refusing to create an ambiguous update")
    text = text.replace("versionCode 54", "versionCode 55", 1)
    text = text.replace("versionName '3.11.3'", "versionName '3.12.0'", 1)
    if "applicationId 'pe.agendaclara.app'" not in text:
        raise RuntimeError("Package ID changed unexpectedly")
    gradle.write_text(text, encoding="utf-8")
    print("PASS: new versionCode 55; versionName 3.12.0; original package and signing unchanged")
