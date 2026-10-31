#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 3
adb shell uiautomator dump /sdcard/agenda_calendar_icons.xml >/dev/null 2>&1
adb exec-out cat /sdcard/agenda_calendar_icons.xml >agenda_calendar_icons.xml
python3 - <<'PY'
import re,subprocess,xml.etree.ElementTree as ET
root=ET.parse('agenda_calendar_icons.xml').getroot()
for node in root.iter('node'):
    text=' '.join((node.get('text',''),node.get('content-desc','')))
    if 'Calendario' in text and 'pestaña' in text:
        bounds=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
        assert len(bounds)==4
        subprocess.run(['adb','shell','input','tap',str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2)],check=True)
        break
else:raise SystemExit('Calendar tab not found')
PY
sleep 2
adb shell uiautomator dump /sdcard/agenda_calendar_icons.xml >/dev/null 2>&1
adb exec-out cat /sdcard/agenda_calendar_icons.xml >agenda_calendar_icons.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse('agenda_calendar_icons.xml').getroot()
content=' '.join((n.get('text','')+' '+n.get('content-desc','')) for n in root.iter('node'))
assert 'Ir a hoy' in content
assert 'Horario de clases' in content
assert '▣' not in content and '▦' not in content
print('PASS: Calendar displays accessible labels without obsolete square glyphs')
PY
adb exec-out screencap -p >screenshots/25-calendario-dos-iconos-png.png
test -s screenshots/25-calendario-dos-iconos-png.png
