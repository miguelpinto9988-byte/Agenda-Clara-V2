#!/usr/bin/env bash
set -euo pipefail
bash updates/phase20/emulator_visual_audit.sh
PKG=pe.agendaclara.app
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 2
adb shell uiautomator dump /sdcard/phase7.xml >/dev/null
adb shell cat /sdcard/phase7.xml >screenshots/phase7-ui.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET,re
from pathlib import Path
root=ET.parse('screenshots/phase7-ui.xml').getroot()
labels=[]
for n in root.iter('node'):
    text=(n.attrib.get('text','')+' '+n.attrib.get('content-desc','')).strip()
    if text:labels.append(text)
Path('screenshots/phase7-audit.txt').write_text('UI hierarchy labels: '+str(len(labels))+'\n'+'\n'.join(labels[:120]))
print('PASS: UI hierarchy inspected,',len(labels),'labels')
PY
# The visual audit reports actual captured states, never an invented design match.
for f in screenshots/*.png;do
  test -s "$f"
  file "$f"
done
echo "PASS: screenshot and hierarchy evidence archived"
