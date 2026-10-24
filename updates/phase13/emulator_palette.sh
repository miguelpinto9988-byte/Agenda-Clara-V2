#!/usr/bin/env bash
set -euo pipefail
APK=artifact-apk/app-debug.apk
PKG=pe.agendaclara.app
mkdir -p screenshots
test -s "$APK"
adb install -r "$APK"
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 9
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p > screenshots/01-agenda.png
function tap_label() {
  local label="$1" file="$2"
  adb shell uiautomator dump "/sdcard/$file" >/dev/null
  adb shell cat "/sdcard/$file" > "$file"
  eval "$(python3 - "$label" "$file" <<'PY'
import sys, re, xml.etree.ElementTree as ET
label, file = sys.argv[1:]
for item in ET.parse(file).getroot().iter('node'):
    text=item.attrib.get('text','')+' '+item.attrib.get('content-desc','')
    if label.casefold() in text.casefold():
        bb=list(map(int,re.findall(r'\d+',item.attrib.get('bounds',''))))
        if len(bb)==4:
            print('TOUCH_X='+str((bb[0]+bb[2])//2))
            print('TOUCH_Y='+str((bb[1]+bb[3])//2))
            break
else: raise SystemExit('NO ENCONTRADO: '+label)
PY
)"
  adb shell input tap "$TOUCH_X" "$TOUCH_Y"
}
tap_label "Calendario" main.xml
sleep 2
tap_label "Abrir mi horario" calendar.xml
sleep 3
adb shell dumpsys activity activities | grep -q ScheduleActivity
adb exec-out screencap -p >screenshots/02-horario.png
tap_label "Crear clase manualmente" home.xml
sleep 3
adb shell uiautomator dump /sdcard/manual.xml >/dev/null
adb shell cat /sdcard/manual.xml > manual.xml
grep -q "72 tonos" manual.xml
grep -q "Más colores" manual.xml
adb exec-out screencap -p > screenshots/03-paleta-colores.png
tap_label "Más colores" manual.xml
sleep 2
adb shell uiautomator dump /sdcard/mixer.xml >/dev/null
adb shell cat /sdcard/mixer.xml > mixer.xml
grep -q "Personalizar color" mixer.xml
grep -q "Saturación" mixer.xml
grep -q "Brillo" mixer.xml
adb exec-out screencap -p > screenshots/04-mezclador-hsv.png
echo "PASS: APK instalada; horario en Calendario; 72 colores HSV y mezclador visible."
