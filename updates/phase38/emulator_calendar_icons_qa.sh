#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 3
adb shell uiautomator dump /sdcard/agenda_calendar_icons.xml >/dev/null 2>&1
adb exec-out cat /sdcard/agenda_calendar_icons.xml >agenda_calendar_icons.xml
python3 - <<'PY'
import re,subprocess,xml.etree.ElementTree as ET
root=ET.parse('agenda_calendar_icons.xml').getroot()
for node in root.iter('node'):
    text=' '.join((node.get('text',''),node.get('content-desc','')))
    if 'Calendario' in text and 'pestaña' in text:
        bounds=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
        assert len(bounds)==4
        subprocess.run(['adb','shell','input','tap',str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2)],check=True)
        break
else:raise SystemExit('Calendar tab not found')
PY
sleep 2
# The month grid is taller than one viewport. UIAutomator serializes only visible
# nodes, so verify both controls while scrolling instead of requiring one snapshot.
python3 - <<'PY'
import subprocess
import time
import xml.etree.ElementTree as ET

required = {"Ir a hoy", "Plan de estudio"}
found = set()
for attempt in range(8):
    subprocess.run(["adb", "shell", "uiautomator", "dump",
                    "/sdcard/agenda_calendar_icons.xml"],
                   check=True, stdout=subprocess.DEVNULL)
    content = subprocess.check_output(
        ["adb", "exec-out", "cat", "/sdcard/agenda_calendar_icons.xml"]
    ).decode("utf-8", errors="replace")
    root = ET.fromstring(content)
    visible = " ".join(
        (node.get("text", "") + " " + node.get("content-desc", ""))
        for node in root.iter("node")
    )
    if "▣" in visible or "▦" in visible:
        raise AssertionError("Legacy square glyph remains visible in Calendar")
    found.update(label for label in required if label in visible)
    if found == required:
        print("PASS: Calendar accessible labels visible after scrolling; obsolete glyphs absent")
        break
    subprocess.run(["adb", "shell", "input", "swipe", "540", "1740",
                    "540", "630", "340"], check=True)
    time.sleep(2)
else:
    raise AssertionError(
        "Calendar/Study panel controls not found after scrolling: " + ", ".join(sorted(required - found))
    )
PY
adb exec-out screencap -p >screenshots/25-calendario-dos-iconos-png.png
test -s screenshots/25-calendario-dos-iconos-png.png
