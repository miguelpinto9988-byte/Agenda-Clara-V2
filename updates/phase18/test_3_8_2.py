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
assert not (src / "ComposeDayActivity.kt").exists()
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

# Check removal of Compose without changing the approved add-task button.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase20/test_remove_compose_view.py"), run_name="__main__")

# Validate custom categories, automatic priority and responsive UI.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase21/test_redesign.py"), run_name="__main__")

# Regression of typography, icons, modal bounds, schedule, and unchanged +.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase22/test_visual_system.py"),run_name="__main__")

# Ensure all unrelated calendar, reminder and task functionality survives phase23.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase23/test_remove_duration.py"), run_name="__main__")

# Verify category color, typography weight, school sessions and unchanged plus button.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase24/test_bold_tinted_ui.py"), run_name="__main__")

# Validate safe layouts and all-screen bold without altering user data.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase25/test_global_layout_fix.py"), run_name="__main__")

# Validate stable iconography, category picker, date/time flows and unchanged +.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase26/test_reference_redesign.py"),run_name="__main__")

# Verify original PNG assets, category icon persistence and UI compatibility.
runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase27/test_png_visuals.py"),run_name="__main__")
