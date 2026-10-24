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
# Click in-app Calendar tab (ScheduleActivity is deliberately not exported).
adb shell uiautomator dump /sdcard/current_ui.xml >/dev/null
adb shell cat /sdcard/current_ui.xml > current_ui.xml
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
adb shell uiautomator dump /sdcard/calendar_ui.xml >/dev/null
adb shell cat /sdcard/calendar_ui.xml > calendar_ui.xml
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
