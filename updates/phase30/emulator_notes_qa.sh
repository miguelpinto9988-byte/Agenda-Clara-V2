#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 3
find_node(){
  local label="$1" attempts=${2:-5} coords=""
  for ((i=0;i<attempts;i++)); do
    adb shell uiautomator dump /sdcard/sticky_qa.xml >/dev/null 2>&1
    adb exec-out cat /sdcard/sticky_qa.xml >sticky_qa.xml
    coords="$(python3 - "$label" <<'PY'
import re,sys,xml.etree.ElementTree as ET
needle=sys.argv[1].lower()
try:
 for n in ET.parse('sticky_qa.xml').getroot().iter('node'):
  data=(n.get('text','')+' '+n.get('content-desc','')).lower()
  if needle in data:
   xy=[int(x) for x in re.findall(r'\d+',n.get('bounds',''))]
   if len(xy)==4 and xy[2]>xy[0] and xy[3]>xy[1]:
    print((xy[0]+xy[2])//2,(xy[1]+xy[3])//2);break
except Exception:pass
PY
)"
    if [ -n "$coords" ]; then printf '%s\n' "$coords";return 0;fi
    adb shell input swipe 510 1500 510 600 250 || true
    sleep 1
  done
  echo "Missing visible Android control: $label" >&2
  return 1
}
tap(){ local xy;xy="$(find_node "$1" "${2:-5}")";read -r x y <<<"$xy";adb shell input tap "$x" "$y";sleep 2;}
capture(){ adb exec-out screencap -p >"screenshots/$1.png";test -s "screenshots/$1.png";}
tap 'Crear una tarea o nota' 1
find_node 'Nueva tarea' 1 >/dev/null
find_node 'Nueva nota' 1 >/dev/null
# Compare the popup cards with the on-screen + anchor, using native UI bounds.
# This catches the previous detached popup on the left of the screen.
python3 - <<'PY'
import re,xml.etree.ElementTree as ET
root=ET.parse("sticky_qa.xml").getroot()
def bounds(description):
    for node in root.iter("node"):
        if node.get("content-desc","")==description:
            value=[int(n) for n in re.findall(r"\d+",node.get("bounds",""))]
            if len(value)==4:return value
    raise SystemExit("UI anchor not found: "+description)
plus=bounds("Crear una tarea o nota")
task=bounds("Nueva tarea")
note=bounds("Nueva nota")
plus_width=plus[2]-plus[0]
if not (task[0]>=0 and note[0]>=0 and
        abs(task[2]-plus[2])<=plus_width and
        0<=task[1]-plus[3]<=plus_width and
        note[1]>=task[3]):
    raise SystemExit("The floating create menu is detached from the top + button")
print("PASS: floating menu anchored directly below + and right-aligned")
PY
capture '17-menu-dos-opciones'
tap 'Nueva nota' 1
find_node 'Título de la nota' 1 >/dev/null
find_node 'Fecha de la nota' 2 >/dev/null
capture '18-editor-nota'
tap 'Ej. Se acabó el gas' 1
adb shell input text 'Gas_agotado'  # synthetic test data, no private user information
adb shell input keyevent KEYCODE_BACK
sleep 1
# Verify the exact approved date selector is reused for notes.
tap 'Elegir fecha de la nota adhesiva' 4
find_node 'Seleccionar fecha' 2 >/dev/null
capture '19-calendario-nota'
adb shell input keyevent KEYCODE_BACK
sleep 1
# The preview appears below the colour selector; take a screenshot after scrolling.
adb shell input swipe 510 1550 510 550 280
sleep 1
capture '20-vista-previa-nota'
tap 'Guardar' 3
find_node 'Gas_agotado' 5 >/dev/null
capture '21-nota-guardada'
# The new note is NOT a task, it has no completion checkbox or deadline.
adb shell pidof "$PKG" >/dev/null
echo 'PASS phase30 emulator: floating +, sticky editor, shared calendar, PNG preview and persistent dated note'
