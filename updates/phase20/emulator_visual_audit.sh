#!/usr/bin/env bash
set -euo pipefail
bash updates/phase11/emulator_schedule_plus.sh
PKG=pe.agendaclara.app
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 3
adb shell uiautomator dump /sdcard/phase6.xml >/dev/null
adb shell cat /sdcard/phase6.xml > screenshots/phase6-home.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse('screenshots/phase6-home.xml').getroot()
for n in root.iter('node'):
    value=(n.attrib.get('text','')+' '+n.attrib.get('content-desc','')).strip()
    if value and ('Conexiones' in value or 'Añadir' in value or 'Agregar' in value):
        print(value,n.attrib.get('bounds'))
PY
# Navigate by accessibility/text bounds, not hard-coded screen coordinates.
python3 - <<'PY' > /tmp/phase6-connections-tap
import xml.etree.ElementTree as ET,re
root=ET.parse('screenshots/phase6-home.xml').getroot()
for n in root.iter('node'):
    value=(n.attrib.get('text','')+' '+n.attrib.get('content-desc','')).lower()
    if n.attrib.get('clickable')=='true' and ('conexiones, abrir pestaña' in n.attrib.get('content-desc','').lower() or n.attrib.get('content-desc','').lower().strip()=='ir a conexiones'):
        nums=list(map(int,re.findall(r'\d+',n.attrib.get('bounds',''))))
        if len(nums)==4:
            print((nums[0]+nums[2])//2,(nums[1]+nums[3])//2)
            break
PY
if test -s /tmp/phase6-connections-tap;then
  read -r X Y < /tmp/phase6-connections-tap
  adb shell input tap "$X" "$Y"
  sleep 3
  adb shell uiautomator dump /sdcard/phase8-check.xml >/dev/null
  adb shell cat /sdcard/phase8-check.xml >screenshots/phase8-check.xml
  python3 - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse('screenshots/phase8-check.xml').getroot()
texts=[n.attrib.get('text','') for n in root.iter('node')]
descs=[n.attrib.get('content-desc','').lower() for n in root.iter('node')]
if 'Mi agenda' in texts and not any('conexiones' in d and 'seleccionad' in d for d in descs):
    raise SystemExit('FAIL: Still on Mi agenda; Connections screenshot rejected')
print('PASS: Connections navigation no longer matches unchanged home screen')
PY
  adb exec-out screencap -p >screenshots/04-conexiones.png
  adb shell uiautomator dump /sdcard/phase6-connections.xml >/dev/null
  adb shell cat /sdcard/phase6-connections.xml >screenshots/phase6-conexiones.xml
else
  echo "FAIL: Conexiones navigation missing" >&2; exit 1
fi
adb shell am force-stop "$PKG"
for f in screenshots/*.png;do test -s "$f";done
echo "PASS: screenshot suite; available visual states captured"
