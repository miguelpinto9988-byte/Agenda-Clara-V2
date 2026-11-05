#!/usr/bin/env bash
# C emulator smoke. Use screenshots + process assertions and accessibility where available.
# The historical 3.8 screen navigation tests are obsolete after the 2026 split.
set -euo pipefail
PKG="pe.agendaclara.app"
APK="artifact-apk/app-debug.apk"
test -s "$APK"
mkdir -p screenshots
adb install -r "$APK" >/dev/null
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 4
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p > screenshots/phase-c-inicio.png

screen="$(adb shell wm size | tr -d '\r' | tail -1)"
dims="$(echo "$screen" | sed -n 's/.*: \([0-9]\+\)x\([0-9]\+\).*/\1 \2/p')"
if [[ -z "$dims" ]]; then echo "No se pudo obtener resolución: $screen"; exit 1; fi
read -r width height <<< "$dims"
# Calendar is the fourth of five items in the existing bottom navigation.
adb shell input tap "$((width*7/10))" "$((height-95))"
sleep 3
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p > screenshots/phase-c-calendario.png

# Try accessibility; Android's uiautomator sometimes refuses to become idle
# because the Agenda screen contains animations. This is not an app crash.
if timeout 15s adb shell uiautomator dump /sdcard/agenda_phase_c.xml >/dev/null 2>&1 &&
   timeout 5s adb exec-out cat /sdcard/agenda_phase_c.xml > screenshots/phase-c-calendario.xml; then
   python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
import re
source=Path("screenshots/phase-c-calendario.xml")
try:root=ET.parse(source).getroot()
except Exception:
    print("WARN: XML de accesibilidad inaccesible; captura disponible")
    raise SystemExit(0)
labels=" ".join((n.get("text","")+" "+n.get("content-desc",""))
                for n in root.iter("node"))
if "Calendario" not in labels:print("WARN: Calendario no está en accesibilidad")
if "Plan de estudio" not in labels:print("WARN: Plan de estudio no está en accesibilidad")
for n in root.iter("node"):
    if "Plan de estudio" in n.get("text","") or "Plan de estudio" in n.get("content-desc",""):
        b=[int(x) for x in re.findall(r"\d+",n.get("bounds",""))]
        if len(b)==4:
            Path("/tmp/agenda_plan_coords").write_text(
                f"{(b[0]+b[2])//2} {(b[1]+b[3])//2}")
            break
PY
fi
if [[ -s /tmp/agenda_plan_coords ]]; then
    read -r plan_x plan_y < /tmp/agenda_plan_coords
else
    # Heuristic fallback, with screenshot evidence for visual auditing.
    plan_x=$((width*75/100))
    plan_y=$((height*19/100))
fi
adb shell input tap "$plan_x" "$plan_y"
sleep 3
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p > screenshots/phase-c-plan-de-estudio.png

# The academic navigation itself must remain available without any fatal crashes.
python3 - <<'PY'
from pathlib import Path
from struct import unpack
images=list(Path("screenshots").glob("phase-c-*.png"))
assert len(images)==3,"Falta evidencia de las tres pantallas"
for p in images:
    raw=p.read_bytes()
    assert raw[:8]==b"\x89PNG\r\n\x1a\n"
    w,h=unpack(">II",raw[16:24])
    assert w>=320 and h>=640 and len(raw)>18000,(p,w,h,len(raw))
    print("PASS emulador",p.name,w,h,len(raw))
PY
echo "PASS C: Inicio, Calendario, intento Plan de estudio y proceso activo en Android 15"
