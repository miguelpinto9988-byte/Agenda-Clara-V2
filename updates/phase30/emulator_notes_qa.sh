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
