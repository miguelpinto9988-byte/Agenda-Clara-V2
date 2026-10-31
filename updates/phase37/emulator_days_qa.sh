#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 3
adb shell uiautomator dump /sdcard/schedule_from_calendar.xml >/dev/null 2>&1
adb exec-out cat /sdcard/schedule_from_calendar.xml >schedule_from_calendar.xml
python3 - <<'PY'
import re,subprocess,xml.etree.ElementTree as ET
root=ET.parse('schedule_from_calendar.xml').getroot()
for node in root.iter('node'):
    label=(node.get('content-desc','')+' '+node.get('text',''))
    if 'Calendario' in label and 'pestaña' in label:
        b=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
        if len(b)==4:
            subprocess.run(['adb','shell','input','tap',str((b[0]+b[2])//2),str((b[1]+b[3])//2)],check=True)
            break
else:raise SystemExit('Missing Calendar navigation tab')
PY
# The class schedule section can be below the visible part of the month.
# Scroll until its real button is visible rather than assuming a fixed viewport.
sleep 2
found_schedule=0
for attempt in 1 2 3 4 5 6; do
  adb shell uiautomator dump /sdcard/schedule_from_calendar.xml >/dev/null 2>&1
  adb exec-out cat /sdcard/schedule_from_calendar.xml >schedule_from_calendar.xml
  if python3 - <<'PY'
import re,subprocess,xml.etree.ElementTree as ET
root=ET.parse('schedule_from_calendar.xml').getroot()
for node in root.iter('node'):
    label=(node.get('content-desc','')+' '+node.get('text',''))
    if 'Abrir mi horario' in label:
        b=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
        if len(b)==4:
            subprocess.run(['adb','shell','input','tap',str((b[0]+b[2])//2),str((b[1]+b[3])//2)],check=True)
            print("PASS: open class schedule from scrolled Calendar screen")
            break
else:raise SystemExit(1)
PY
  then found_schedule=1;break;fi
  adb shell input swipe 530 1330 530 650 300
  sleep 1
done
if [ "$found_schedule" -ne 1 ]; then
  echo 'Missing class schedule entry in Calendar after scrolling' >&2
  exit 1
fi
sleep 3
adb shell uiautomator dump /sdcard/schedule_day_editor.xml >/dev/null 2>&1
adb exec-out cat /sdcard/schedule_day_editor.xml >schedule_day_editor.xml
python3 - <<'PY'
import re,xml.etree.ElementTree as ET,subprocess
root=ET.parse('schedule_day_editor.xml').getroot()
for node in root.iter('node'):
    label=node.get('text','')+' '+node.get('content-desc','')
    if 'Crear clase manualmente' in label:
        xy=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
        assert len(xy)==4
        subprocess.run(['adb','shell','input','tap',str((xy[0]+xy[2])//2),str((xy[1]+xy[3])//2)],check=True)
        break
else:
    raise SystemExit('Could not find manual class editor entry point')
PY
sleep 2
# Long color palette is intentionally unchanged; reach the day/time controls by scrolling.
found=0
for attempt in 1 2 3 4 5 6 7; do
  adb shell uiautomator dump /sdcard/schedule_day_editor.xml >/dev/null 2>&1
  adb exec-out cat /sdcard/schedule_day_editor.xml >schedule_day_editor.xml
  if python3 - <<'PYCODE'
import xml.etree.ElementTree as ET
root=ET.parse('schedule_day_editor.xml').getroot()
values=' '.join((n.get('text','')+' '+n.get('content-desc','')) for n in root.iter('node'))
assert 'Días y horarios' in values and 'AM' in values and 'PM' in values
PYCODE
  then found=1; break; fi
  adb shell input swipe 540 1410 540 540 330
  sleep 1
done
if [ "$found" -ne 1 ]; then
  echo 'ERROR: Could not locate the AM/PM day editor after scrolling' >&2
  exit 1
fi
echo 'PASS: schedule day editor exposes independent 12h AM/PM time controls'
adb exec-out screencap -p >screenshots/24-horarios-12h-am-pm.png
test -s screenshots/24-horarios-12h-am-pm.png
