#!/usr/bin/env python3
"""Install the isolated widget rendering probe in the Android DEBUG variant only."""
from pathlib import Path
import xml.etree.ElementTree as ET

SRC = Path("AgendaClara/app/src")
STAGE = Path(__file__).resolve().parent
JAVA = SRC / "debug/java/pe/agendaclara/app/WidgetRenderProbeActivity.java"
MANIFEST = SRC / "debug/AndroidManifest.xml"
MANIFEST_TEXT = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application>
        <activity android:name=".WidgetRenderProbeActivity"
            android:exported="true" android:theme="@style/AppTheme"/>
    </application>
</manifest>
"""


def main() -> None:
    ET.fromstring(MANIFEST_TEXT)
    JAVA.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    JAVA.write_bytes((STAGE / "WidgetRenderProbeActivity.java").read_bytes())
    MANIFEST.write_text(MANIFEST_TEXT, encoding="utf-8")
    release_probe = SRC / "main/java/pe/agendaclara/app/WidgetRenderProbeActivity.java"
    if release_probe.exists():
        raise RuntimeError("QA probe must not be part of the release source set")
    print("PASS: runtime widget-rendering probe installed in debug variant only")


if __name__ == "__main__":
    main()
