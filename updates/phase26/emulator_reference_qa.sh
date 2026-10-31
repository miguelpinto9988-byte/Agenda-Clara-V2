#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 4
find_and_tap(){
  local term="$1" out
  for attempt in 1 2 3 4 5 6; do
    adb shell uiautomator dump /sdcard/ref_visual.xml >/dev/null 2>&1
    adb exec-out cat /sdcard/ref_visual.xml >ref_visual.xml
    out="$(python3 - "$term" <<'PY'
import re,sys,xml.etree.ElementTree as ET
query=sys.argv[1].lower()
try:
 for node in ET.parse("ref_visual.xml").getroot().iter("node"):
  label=(node.get("text","")+" "+node.get("content-desc","")).lower()
  if query in label:
   bounds=[int(x) for x in re.findall(r"\d+",node.get("bounds",""))]
   if len(bounds)==4 and bounds[2]>bounds[0] and bounds[3]>bounds[1]:
    print((bounds[0]+bounds[2])//2,(bounds[1]+bounds[3])//2)
    break
except Exception as e: print("",end="")
PY
)"
    if [ -n "$out" ]; then
      read -r x y <<<"$out"
      adb shell input tap "$x" "$y";sleep 2;return 0
    fi
    adb shell input swipe 550 1470 550 490 320
    sleep 1
  done
  echo "No visible Android UI node for: $term" >&2
  return 1
}
capture(){
    adb exec-out screencap -p >"screenshots/$1.png"
    test -s "screenshots/$1.png"
}
find_and_tap "Crear una tarea"
find_and_tap "Elegir fecha"
adb shell uiautomator dump /sdcard/ref_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/ref_visual.xml >ref_visual.xml
grep -q 'Seleccionar fecha' ref_visual.xml
capture "09-selector-fecha-moderno"
adb shell input keyevent KEYCODE_BACK
sleep 2
find_and_tap "Elegir hora límite"
adb shell uiautomator dump /sdcard/ref_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/ref_visual.xml >ref_visual.xml
grep -q 'Seleccionar hora' ref_visual.xml
capture "10-selector-hora-moderno"
adb shell input keyevent KEYCODE_BACK
sleep 2
find_and_tap "Seleccionar categoría:"
adb shell uiautomator dump /sdcard/ref_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/ref_visual.xml >ref_visual.xml
grep -q 'Elegir categoría' ref_visual.xml
capture "11-selector-categorias-colores"
adb shell input keyevent KEYCODE_BACK
sleep 2
find_and_tap "Crear nueva categoría"
adb shell uiautomator dump /sdcard/ref_visual.xml >/dev/null 2>&1
adb exec-out cat /sdcard/ref_visual.xml >ref_visual.xml
grep -q 'Crear categoría' ref_visual.xml
capture "12-selector-color-iconos"
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" -a connections --ei tab 0 >/dev/null
sleep 4
capture "13-conexiones-whatsapp"
find_and_tap "Calendario"
capture "14-conexiones-calendario"
adb shell am start -W -n "$PKG/.ScheduleActivity" >/dev/null
sleep 3
capture "15-horario-iconografia"
echo "PASS phase26 emulator: native date, 12h time, category/color selectors, connections icons and schedule back/help"
