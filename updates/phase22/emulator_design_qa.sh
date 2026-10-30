#!/usr/bin/env bash
set -euo pipefail
# Additional non-destructive screenshots and navigation checks on a fresh emulator.
PKG=pe.agendaclara.app
mkdir -p screenshots
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
sleep 4
tap_node(){
    local label="$1" coords
    adb shell uiautomator dump /sdcard/design_ui.xml >/dev/null 2>&1
    adb exec-out cat /sdcard/design_ui.xml >design_ui.xml
    coords="$(python3 - "$label" <<'PY'
import sys,xml.etree.ElementTree as ET,re
label=sys.argv[1].lower()
for n in ET.parse("design_ui.xml").getroot().iter("node"):
    text=(n.attrib.get("text","")+" "+n.attrib.get("content-desc","")).lower()
    if label in text:
        bounds=[int(x) for x in re.findall(r"\d+",n.attrib.get("bounds",""))]
        if len(bounds)==4 and bounds[2]>bounds[0] and bounds[3]>bounds[1]:
            print((bounds[0]+bounds[2])//2,(bounds[1]+bounds[3])//2);break
else:
    raise SystemExit("Missing visible Android control: "+label)
PY
)"
    read -r x y <<<"$coords"
    adb shell input tap "$x" "$y"
    sleep 2
}
read_ui(){
    adb shell uiautomator dump /sdcard/design_ui.xml >/dev/null 2>&1
    adb exec-out cat /sdcard/design_ui.xml >design_ui.xml
}
read_ui
grep -q 'Mis categorías' design_ui.xml
grep -q 'General' design_ui.xml
grep -q 'Crear una tarea' design_ui.xml
if grep -E 'text="(Todas|Urgentes|Pendientes|Próximas|Hechas)"' design_ui.xml;then
    echo "Redundant status filters appeared again" >&2;exit 1
fi
adb exec-out screencap -p > screenshots/04-agenda-diseno.png
tap_node "Gestionar categorías"
read_ui
grep -q 'General' design_ui.xml
adb exec-out screencap -p > screenshots/05-categorias-flotante.png
adb shell input keyevent KEYCODE_BACK
sleep 2
tap_node "Crear una tarea"
read_ui
grep -q 'Nueva tarea' design_ui.xml
grep -q 'Nombre de la tarea' design_ui.xml
adb exec-out screencap -p > screenshots/06-editor-flotante.png
adb shell input keyevent KEYCODE_BACK
sleep 2
tap_node "Revisar, abrir pestaña"
read_ui
grep -q 'Revisión' design_ui.xml
adb exec-out screencap -p > screenshots/07-revision.png
tap_node "Conexiones, abrir pestaña"
read_ui
grep -q 'Conexiones' design_ui.xml
adb exec-out screencap -p > screenshots/08-conexiones.png
for item in 04-agenda-diseno 05-categorias-flotante 06-editor-flotante 07-revision 08-conexiones;do test -s "screenshots/$item.png";done
echo "PASS phase22 emulator: category manager, unchanged add-task entry, scrollable task modal, review, connections"
