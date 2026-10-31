#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
APK=artifact-apk/app-debug.apk
test -s "$APK"
mkdir -p screenshots
adb install -r "$APK"
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 5
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/01-agenda.png
# Android emulator occasionally shows a *system* Pixel Launcher ANR over an otherwise healthy app.
# Recover ONLY that system dialog; application crash/error dialogs are never dismissed.
dismiss_launcher_anr(){
    adb shell uiautomator dump /sdcard/launcher_diag.xml >/dev/null 2>&1 || true
    adb shell cat /sdcard/launcher_diag.xml >launcher_diag.xml 2>/dev/null || true
    if [ ! -s launcher_diag.xml ]; then return 0; fi
    python3 - <<'PY' >launcher_tap.txt || true
import re,xml.etree.ElementTree as ET
try: nodes=list(ET.parse("launcher_diag.xml").getroot().iter("node"))
except Exception: raise SystemExit(0)
labels=" ".join((node.attrib.get("text","")+" "+node.attrib.get("content-desc","")) for node in nodes).lower()
if not any(tag in labels for tag in ("pixel launcher isn't responding","pixel launcher is not responding","pixel launcher no responde")):
    raise SystemExit(0)
for node in nodes:
    if node.attrib.get("text","").strip().lower() in ("close app","cerrar aplicación","cerrar app","esperar","wait"):
        xy=[int(n) for n in re.findall(r"\d+",node.attrib.get("bounds",""))]
        if len(xy)==4:
            print((xy[0]+xy[2])//2,(xy[1]+xy[3])//2)
            break
PY
    if [ -s launcher_tap.txt ]; then
        read -r px py <launcher_tap.txt
        echo "Emulator-only Pixel Launcher ANR: closing stalled launcher dialog at $px,$py"
        adb shell input tap "$px" "$py" || true
        sleep 4
    fi
}
dismiss_launcher_anr
# Click in-app Calendar tab (ScheduleActivity is deliberately not exported).
for attempt in 1 2 3 4; do
  dismiss_launcher_anr
  adb shell uiautomator dump /sdcard/current_ui.xml >/dev/null || true
  adb shell cat /sdcard/current_ui.xml > current_ui.xml || true
  if grep -q -E 'content-desc="Calendario|text="Calendario"' current_ui.xml; then break; fi
  sleep 3
done
eval "$(python3 - <<'PY'
import xml.etree.ElementTree as ET,re
tree=ET.parse('current_ui.xml')
for item in tree.getroot().iter("node"):
  value=item.attrib.get("content-desc","")+' '+item.attrib.get("text","")
  if "Calendario" in value and ('pestaña' in value or 'Calendario' == item.attrib.get('text')):
    xy=list(map(int,re.findall(r'\d+',item.attrib.get('bounds',''))))
    if len(xy)==4:
      print("TAP_X="+str((xy[0]+xy[2])//2))
      print("TAP_Y="+str((xy[1]+xy[3])//2))
      break
else: raise SystemExit("No se encontró la pestaña Calendario")
PY
)"
adb shell input tap "$TAP_X" "$TAP_Y"
sleep 3
# The redesigned calendar gives its month grid precedence over the class-schedule card.
# Scroll until the original class-schedule button is visible; never tap blind.
for scroll in 1 2 3 4 5; do
  adb shell uiautomator dump /sdcard/calendar_ui.xml >/dev/null
  adb shell cat /sdcard/calendar_ui.xml > calendar_ui.xml
  if grep -q 'Abrir mi horario' calendar_ui.xml; then break; fi
  adb shell input swipe 540 1740 540 660 300
  sleep 2
done
eval "$(python3 - <<'PY'
import xml.etree.ElementTree as ET,re
for item in ET.parse('calendar_ui.xml').getroot().iter("node"):
  text=item.attrib.get('text','')
  if 'Abrir mi horario' in text:
    xy=list(map(int,re.findall(r'\d+',item.attrib.get('bounds',''))))
    if len(xy)==4:
      print("OPEN_X="+str((xy[0]+xy[2])//2))
      print("OPEN_Y="+str((xy[1]+xy[3])//2))
      break
else:raise SystemExit('No aparece Abrir mi horario en Calendario')
PY
)"
adb shell input tap "$OPEN_X" "$OPEN_Y"
sleep 4
adb shell pidof "$PKG" >/dev/null
adb shell dumpsys activity activities | grep -q "ScheduleActivity"
adb shell uiautomator dump /sdcard/schedule_ui.xml >/dev/null
adb shell cat /sdcard/schedule_ui.xml >schedule_ui.xml
grep -q "Crear horario desde una foto" schedule_ui.xml
grep -q "Crear horario manualmente" schedule_ui.xml
adb exec-out screencap -p >screenshots/02-horario-home.png
# Open the empty weekly plan using its actual button.
eval "$(python3 - <<'PY'
import xml.etree.ElementTree as ET,re
for item in ET.parse('schedule_ui.xml').getroot().iter('node'):
  if 'Ver horario completo' in item.attrib.get('text',''):
    xy=list(map(int,re.findall(r'\d+',item.attrib.get('bounds',''))))
    if len(xy)==4:
      print("WEEK_X="+str((xy[0]+xy[2])//2))
      print("WEEK_Y="+str((xy[1]+xy[3])//2))
      break
else:raise SystemExit('No se encontró Ver horario completo')
PY
)"
adb shell input tap "$WEEK_X" "$WEEK_Y"
sleep 2
adb shell uiautomator dump /sdcard/weekly_ui.xml >/dev/null
adb shell cat /sdcard/weekly_ui.xml > weekly_ui.xml
grep -q "Mi horario" weekly_ui.xml
# Verify new weekly grid is visible and the alternative list mode exists.
grep -q 'Cuadrícula' weekly_ui.xml
grep -q 'Lista' weekly_ui.xml
adb exec-out screencap -p >screenshots/03-vista-semanal.png
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity"
sleep 3
adb shell pidof "$PKG" >/dev/null
for file in screenshots/*.png;do test -s "$file";done
echo "PASS: 2.6.1 instalada; Calendario y Horario; opciones OCR/manual; cuadrícula semanal; reinicio."

# Additional design review: category modal, new task, review, and connections.
bash updates/phase22/emulator_design_qa.sh

# Reference-approved colour iconography and real picker screenshots.
bash updates/phase26/emulator_reference_qa.sh
