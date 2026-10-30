#!/usr/bin/env python3
"""3.8.2: retire unreferenced Java helpers after all historical migrations.

The sequential update scripts MUST remain: they reconstruct the current source
from the checked-in 1.3.0 ZIP. Deleting them would break the build.
"""
from pathlib import Path
import re

root = Path("AgendaClara")
src = root / "app/src/main/java/pe/agendaclara/app"
manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
obsolete = ("AcademicAnnouncementInterpreter", "ScheduleMultiDays")
production = tuple(src.glob("*.java")) + tuple(src.glob("*.kt"))

for name in obsolete:
    target = src / (name + ".java")
    if not target.is_file():
        raise RuntimeError(f"Missing expected legacy Java class: {target}")
    symbol = re.compile(r"\b" + re.escape(name) + r"\b")
    references = [
        str(p) for p in production
        if p != target and p.exists()
        and symbol.search(p.read_text(encoding="utf-8"))
    ]
    if symbol.search(manifest):
        references.append("AndroidManifest.xml")
    if references:
        raise RuntimeError(f"Cannot remove {name}: production references exist: {references}")
    target.unlink()
    print(f"REMOVED unused Java class: {name}")

build = root / "app/build.gradle"
text = build.read_text(encoding="utf-8")
for old in ("versionCode 29", "versionName '3.8.1'"):
    if text.count(old) != 1:
        raise RuntimeError(f"Unsafe Gradle update: expected exactly one {old}")
text = text.replace("versionCode 29", "versionCode 30")
text = text.replace("versionName '3.8.1'", "versionName '3.8.2'")
build.write_text(text, encoding="utf-8")
print("PASS: safe native source cleanup, build 3.8.2")

# Install the optional approved top-right + artwork and native press state
# after all legacy 3.8.2 migrations, leaving original navigation untouched.
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase19/apply_top_plus_button.py"), run_name="__main__")

# Remove the unused Compose-only landing card and its secondary activity.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase20/apply_remove_compose_view.py"), run_name="__main__")
