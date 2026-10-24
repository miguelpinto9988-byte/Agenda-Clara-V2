#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
test -s artifact-apk/app-debug.apk
mkdir -p screenshots
adb install -r artifact-apk/app-debug.apk
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 5
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/01-agenda-java.png
# ComposeDayActivity is intentionally non-exported. Open through the real public UI.
adb shell uiautomator dump /sdcard/agenda_ui.xml >/dev/null
adb shell cat /sdcard/agenda_ui.xml >agenda_ui.xml
eval "$(python3 - <<'PY'
import re, xml.etree.ElementTree as ET
root=ET.parse("agenda_ui.xml").getroot()
for node in root.iter("node"):
    value=node.attrib.get("text","")
    if "Abrir vista diaria moderna" in value:
        coords=list(map(int,re.findall(r"\d+",node.attrib["bounds"])))
        print("TAP_X="+str((coords[0]+coords[2])//2))
        print("TAP_Y="+str((coords[1]+coords[3])//2))
        break
else:
    raise SystemExit("Missing native button to Compose screen")
PY
)"
adb shell input tap "$TAP_X" "$TAP_Y"
sleep 7
adb shell pidof "$PKG" >/dev/null
adb shell dumpsys activity activities | grep -q "ComposeDayActivity"
adb shell uiautomator dump /sdcard/compose_ui.xml >/dev/null
adb shell cat /sdcard/compose_ui.xml >compose_ui.xml
grep -q "Mi día" compose_ui.xml
adb exec-out screencap -p >screenshots/02-vista-diaria-compose.png
adb shell am start -W -a inbox -n "$PKG/.MainActivity"
sleep 4
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/03-revisar-java.png
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity"
sleep 3
adb shell pidof "$PKG" >/dev/null
for file in screenshots/*.png; do test -s "$file"; done
echo "PASS: install; Java agenda; Kotlin Compose overview; review; restart."
