#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 5
adb shell uiautomator dump /sdcard/calendar_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/calendar_visual.xml >calendar_visual.xml
python3 - <<'PY'
import re,subprocess,xml.etree.ElementTree as ET
root=ET.parse('calendar_visual.xml').getroot()
for item in root.iter('node'):
    t=(item.get('content-desc','')+' '+item.get('text',''))
    if 'Calendario' in t and 'pestaña' in t:
        b=list(map(int,re.findall(r'\d+',item.get('bounds',''))))
        if len(b)==4:
            subprocess.run(['adb','shell','input','tap',str((b[0]+b[2])//2),str((b[1]+b[3])//2)],check=True)
            break
else:raise SystemExit('Calendar navigation tab not found')
PY
sleep 3
adb shell uiautomator dump /sdcard/calendar_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/calendar_visual.xml >calendar_visual.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse('calendar_visual.xml').getroot()
strings=' '.join((n.get('text','')+' '+n.get('content-desc','')) for n in root.iter('node'))
for label in ('Mi mes','Leyenda del calendario: Tareas','Leyenda del calendario: Notas','Leyenda del calendario: Ambos'):
    assert label in strings,'Missing visual element: '+label
assert any((n.get('content-desc','') or '').startswith('20') and 'tarea' in (n.get('content-desc','') or '') and 'nota' in (n.get('content-desc','') or '') for n in root.iter('node')),'Calendar accessible day counts missing'
print('PASS 3.10.7 emulator: month, task/note/both legend, accessible date cells')
PY
mkdir -p screenshots
adb exec-out screencap -p > screenshots/26-calendario-tareas-notas-ambos.png
test -s screenshots/26-calendario-tareas-notas-ambos.png
