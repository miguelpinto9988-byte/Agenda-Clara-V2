#!/usr/bin/env python3
"""Remove the redundant Kotlin/Compose daily-view card and its private screen.

Run after phase19 (the approved + button) while reconstructing Agenda Clara.
Do not alter task data, the native editor, Agenda filters or the + control.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "AgendaClara/app"
JAVA = APP / "src/main/java/pe/agendaclara/app/MainActivity.java"
KOTLIN = APP / "src/main/java/pe/agendaclara/app/ComposeDayActivity.kt"
MANIFEST = APP / "src/main/AndroidManifest.xml"
APP_BUILD = APP / "build.gradle"
ROOT_BUILD = ROOT / "AgendaClara/build.gradle"

PROMO = "Vista moderna · Kotlin + Compose"
OLD_APP_PLUGINS = "plugins { id 'com.android.application'; id 'org.jetbrains.kotlin.android'; id 'org.jetbrains.kotlin.plugin.compose' }"
OLD_DEPENDENCIES = """dependencies {
    implementation platform('androidx.compose:compose-bom:2026.02.00')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.foundation:foundation'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.activity:activity-compose:1.10.1'
}

"""
KOTLIN_PLUGINS = (
    "    id 'org.jetbrains.kotlin.android' version '2.4.10' apply false\n",
    "    id 'org.jetbrains.kotlin.plugin.compose' version '2.4.10' apply false\n",
)


def exactly_once(content: str, old: str, replacement: str, label: str) -> str:
    if content.count(old) != 1:
        raise RuntimeError(f"Unsafe Compose removal: expected one {label}, found {content.count(old)}")
    return content.replace(old, replacement, 1)


def transform_files() -> dict:
    java = JAVA.read_text(encoding="utf-8")
    line = [s for s in java.splitlines(keepends=True) if PROMO in s]
    if len(line) != 1 or "ComposeDayActivity.class" not in line[0] or "primaryButton" not in line[0]:
        raise RuntimeError("Unexpected card code; refusing to remove other UI")
    revised_java = exactly_once(java, line[0], "", "daily-view card")
    if "setTag(\"new_task_button\")" not in revised_java or "openEditor(-1,null,null)" not in revised_java:
        raise RuntimeError("Existing + button or native editor not detected")

    manifest = MANIFEST.read_text(encoding="utf-8")
    matching = [s for s in manifest.splitlines(keepends=True) if 'android:name=".ComposeDayActivity"' in s]
    if len(matching) != 1 or "<activity" not in matching[0]:
        raise RuntimeError("Compose activity declaration differs")
    revised_manifest = exactly_once(manifest, matching[0], "", "Compose manifest activity")

    kotlin = KOTLIN.read_text(encoding="utf-8")
    if "class ComposeDayActivity : ComponentActivity()" not in kotlin:
        raise RuntimeError("Unexpected Kotlin source")
    if sorted(p.name for p in KOTLIN.parent.glob("*.kt")) != ["ComposeDayActivity.kt"]:
        raise RuntimeError("Other Kotlin classes exist; cannot remove shared Kotlin support")

    gradle = APP_BUILD.read_text(encoding="utf-8")
    gradle = exactly_once(gradle, OLD_APP_PLUGINS,
                          "plugins { id 'com.android.application' }", "Compose/Kotlin app plugins")
    gradle = exactly_once(gradle, "    buildFeatures { compose true }\n", "", "Compose build flag")
    gradle = exactly_once(gradle, "    kotlinOptions { jvmTarget = '1.8' }\n", "", "Kotlin options")
    gradle = exactly_once(gradle, OLD_DEPENDENCIES, "", "Compose dependencies")

    root_gradle = ROOT_BUILD.read_text(encoding="utf-8")
    for old in KOTLIN_PLUGINS:
        root_gradle = exactly_once(root_gradle, old, "", "unused Kotlin plugin")

    return {JAVA: revised_java, MANIFEST: revised_manifest,
            APP_BUILD: gradle, ROOT_BUILD: root_gradle}


def main() -> None:
    revised = transform_files()
    # All anchors are validated before changing a file.
    for path, content in revised.items():
        path.write_text(content, encoding="utf-8")
    KOTLIN.unlink()
    print("PASS: Compose card, private activity, manifest entry and unused dependencies removed")


if __name__ == "__main__":
    main()
