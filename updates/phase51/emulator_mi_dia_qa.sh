#!/usr/bin/env bash
# Regression test for the new home; the old calendar, voice and widget tests
# are still run afterwards. Needs the signed debug APK already installed.
set -euo pipefail
PKG=pe.agendaclara.app
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 5
for attempt in 1 2 3 4 5; do
  if adb shell uiautomator dump /sdcard/mi_dia_ui.xml >mi_dia_dump.log 2>&1 &&
     adb exec-out cat /sdcard/mi_dia_ui.xml >mi_dia_ui.xml; then
    break
  fi
  cat mi_dia_dump.log || true
  sleep 3
done
test -s mi_dia_ui.xml || { echo "ERROR: no accessible Mi día UI"; exit 1; }
python3 - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse("mi_dia_ui.xml").getroot()
nodes=list(root.iter("node"))
text=" ".join((n.get("text","")+" "+n.get("content-desc","")) for n in nodes)
checks=("Aquí tienes tu día, en un vistazo.", "Tu día en números",
        "Tareas", "Eventos", "Estudio", "Progreso", "Mi día",
        "Inicio")
missing=[label for label in checks if label not in text]
assert not missing, "Missing new home UI: "+repr(missing)+"; visible: "+text[:1000]
assert "Paisaje ilustrado del día" in text, "Offline header landscape is missing"
print("PASS phase51 emulator: daily greeting, landscape, summary cards and navigation")
PY
mkdir -p screenshots
adb exec-out screencap -p > screenshots/27-inicio-mi-dia.png
test -s screenshots/27-inicio-mi-dia.png
