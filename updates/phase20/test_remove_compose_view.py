#!/usr/bin/env python3
"""Regression: remove only the optional daily Compose view, not native agenda data."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("remove_compose", HERE / "apply_remove_compose_view.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

java = patch.JAVA.read_text(encoding="utf-8")
manifest = patch.MANIFEST.read_text(encoding="utf-8")
app_gradle = patch.APP_BUILD.read_text(encoding="utf-8")
root_gradle = patch.ROOT_BUILD.read_text(encoding="utf-8")
assert not patch.KOTLIN.exists()
assert not any(patch.KOTLIN.parent.glob("*.kt"))
for unexpected in ("Vista moderna · Kotlin + Compose", "Abrir vista diaria moderna",
                   "ComposeDayActivity", "startActivity(new Intent(this,ComposeDayActivity.class))"):
    assert unexpected not in java, unexpected
assert "ComposeDayActivity" not in manifest
assert "ComposeDayActivity" not in app_gradle
assert "org.jetbrains.kotlin" not in app_gradle + root_gradle
assert "androidx.compose" not in app_gradle + root_gradle
assert "buildFeatures { compose true }" not in app_gradle
assert "implementation 'com.google.mlkit:text-recognition:16.0.1'" in app_gradle
assert "versionCode 30" in app_gradle and "versionName '3.8.2'" in app_gradle
for essential in (
    'setTag("new_task_button")', 'openEditor(-1,null,null)',
    "TopPlusButtonMotion.install(this)", "TaskSummary.calculate(",
    "Store.get(this).all()", "void tasksPage()", "void calendarPage()",
):
    assert essential in java, essential
for retained in (".MainActivity", ".ScheduleActivity", ".WhatsAppListener"):
    assert retained in manifest, retained
assert (patch.KOTLIN.parent / "TopPlusButtonMotion.java").is_file()
assert (patch.APP / "src/main/res/drawable-nodpi/ic_top_plus_animated.png").is_file()

assert patch.exactly_once("left RIGHT end", "RIGHT", "NATIVE", "fixture") == "left NATIVE end"
for bad in ("left end", "RIGHTRIGHT"):
    try:
        patch.exactly_once(bad, "RIGHT", "", "fixture")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Missing/repeated anchor must be rejected")
print("PASS: Compose promo, screen and dependencies removed; native editor and + preserved")
