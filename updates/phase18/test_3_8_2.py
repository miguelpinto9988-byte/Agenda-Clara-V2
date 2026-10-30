#!/usr/bin/env python3
"""Verify no dead native helpers remain and live app paths are intact."""
from pathlib import Path

root = Path("AgendaClara")
src = root / "app/src/main/java/pe/agendaclara/app"
assert not (src / "AcademicAnnouncementInterpreter.java").exists()
assert not (src / "ScheduleMultiDays.java").exists()
for used in (
    "MultiActivityInterpreter", "MessageParser", "SchedulePhotoReview",
    "ScheduleOcr", "WhatsAppListener", "WhatsAppSessionService",
    "ScheduleActivity", "Store",
):
    assert (src / (used + ".java")).exists(), used
assert (src / "ComposeDayActivity.kt").exists()
manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
assert "WhatsAppListener" in manifest and "ScheduleActivity" in manifest
gradle = (root / "app/build.gradle").read_text(encoding="utf-8")
assert "versionCode 30" in gradle and "versionName '3.8.2'" in gradle
for f in src.glob("*.java"):
    text = f.read_text(encoding="utf-8")
    assert "AcademicAnnouncementInterpreter" not in text, f
    assert "ScheduleMultiDays" not in text, f
print("PASS: unused classes pruned, active modules retained, version 3.8.2")

# The phase-19 add-button regression runs as part of the active 3.8.2 CI.
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase19/test_top_plus_button.py"), run_name="__main__")
