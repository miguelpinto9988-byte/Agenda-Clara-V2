#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
# Widget cannot be placed into an arbitrary launcher headlessly; this checks
# Android registration and the same route triggered by its + action.
adb shell dumpsys package "$PKG" >widget_pkg.txt
grep -q 'StickyNotesWidget' widget_pkg.txt
grep -q 'StickyNotesWidgetService' widget_pkg.txt
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity" -a new_sticky_note >/dev/null
sleep 3
adb shell pidof "$PKG" >/dev/null
adb shell uiautomator dump /sdcard/sticky_widget_qa.xml >/dev/null 2>&1
adb exec-out cat /sdcard/sticky_widget_qa.xml >sticky_widget_qa.xml
grep -q 'Título de la nota' sticky_widget_qa.xml
grep -q 'Fecha de la nota' sticky_widget_qa.xml
adb exec-out screencap -p >screenshots/22-widget-nota-editor.png
test -s screenshots/22-widget-nota-editor.png
echo "PASS phase31 emulator: widget provider/service installed, add-note route opens dated editor."
