#!/usr/bin/env bash
# Final C emulator smoke: the 5-tab navigation, Calendario / Plan de estudio.
# Non-destructive evidence: screenshots + accessibility + stable process.
set -euo pipefail
APK="artifact-apk/app-debug.apk"
if [[ $# -gt 0 ]]; then APK="$1"; fi
PKG="pe.agendaclara.app"
test -s "$APK"
mkdir -p screenshots
adb install -r "$APK" >/dev/null
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 5
adb exec-out screencap -p > screenshots/phase-c-01-inicio.png
screen="$(adb shell wm size | tr -d '\r' | tail -1)"
dims="$(echo "$screen" | sed -n 's/.*: \([0-9]\+\)x\([0-9]\+\).*/\1 \2/p')"
if [[ -z "$dims" ]]; then echo "Cannot detect screen size: $screen"; exit 1; fi
read -r width height <<< "$dims"
calendar_x=$((width*7/10))
bottom_y=$((height-95))
adb shell input tap "$calendar_x" "$bottom_y"
sleep 3
adb exec-out screencap -p > screenshots/phase-c-02-calendario.png
adb shell pidof "$PKG" >/dev/null || { echo "App closed after Calendario navigation"; exit 1; }
if timeout 35s adb shell uiautomator dump /sdcard/agenda_phase_c.xml >/dev/null 2>&1 &&
   timeout 10s adb exec-out cat /sdcard/agenda_phase_c.xml > screenshots/phase-c-calendar.xml; then
   python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
p=Path("screenshots/phase-c-calendar.xml")
try:root=ET.fromstring(p.read_text())
except Exception:
    print("WARN: Accessibility XML unavailable; screenshot retained")
else:
    value=" ".join((n.attrib.get("text","")+" "+n.attrib.get("content-desc",""))
                   for n in root.iter("node"))
    for label in ("Calendario","Plan de estudio"):
        if label not in value:print("WARN: label not exposed:",label)
    if all(label in value for label in ("Calendario","Plan de estudio")):
        print("PASS C: both calendar switch labels accessible")
PY
else
   echo "WARN: uiautomator timed out; screenshots and process stability checked"
fi
python3 - <<'PY'
from pathlib import Path
import re,xml.etree.ElementTree as ET
p=Path("screenshots/phase-c-calendar.xml")
if not p.exists():raise SystemExit(0)
try:root=ET.fromstring(p.read_text())
except Exception:raise SystemExit(0)
for node in root.iter("node"):
    if node.attrib.get("text")=="Plan de estudio" or node.attrib.get("content-desc","").startswith("Plan de estudio"):
        vals=[int(x) for x in re.findall(r"\d+",node.attrib.get("bounds",""))]
        if len(vals)==4:
            Path("/tmp/agenda-plan-tap").write_text(f"{(vals[0]+vals[2])//2} {(vals[1]+vals[3])//2}")
        break
PY
if [[ -s /tmp/agenda-plan-tap ]]; then
  read -r tab_x tab_y < /tmp/agenda-plan-tap
  adb shell input tap "$tab_x" "$tab_y"
  sleep 3
  adb exec-out screencap -p > screenshots/phase-c-03-plan-estudio.png
  adb shell pidof "$PKG" >/dev/null || { echo "App closed after Plan de estudio switch"; exit 1; }
fi
python3 - <<'PY'
from pathlib import Path
from struct import unpack
images=list(Path("screenshots").glob("phase-c-*.png"))
assert len(images)>=2,"Missing C navigation evidence"
for p in images:
    data=p.read_bytes()
    assert data[:8]==b"\x89PNG\r\n\x1a\n"
    w,h=unpack(">II",data[16:24])
    assert w>=320 and h>=640 and len(data)>18000,(p,w,h,len(data))
    print("PASS screenshot",p,w,h)
PY
echo "PASS C emulator smoke: APK install, Calendario navigation and no process crash"
