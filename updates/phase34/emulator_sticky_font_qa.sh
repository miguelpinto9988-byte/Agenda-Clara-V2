#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
mkdir -p screenshots
previous="$(adb shell settings get system font_scale | tr -d '\r')"
if [ -z "$previous" ] || [ "$previous" = "null" ]; then previous="1.0"; fi
restore_font(){
  adb shell settings put system font_scale "$previous" || true
  adb shell am force-stop "$PKG" || true
}
trap restore_font EXIT
for font in 1.3 1.6; do
  adb shell settings put system font_scale "$font"
  adb shell am force-stop "$PKG" || true
  adb shell am start -W -n "$PKG/.MainActivity" -a new_sticky_note >/dev/null
  sleep 3
  adb shell pidof "$PKG" >/dev/null
  adb shell uiautomator dump /sdcard/sticky_font_check.xml >/dev/null 2>&1
  adb exec-out cat /sdcard/sticky_font_check.xml >sticky_font_check.xml
  grep -q 'Título de la nota' sticky_font_check.xml
  adb exec-out screencap -p >"screenshots/23-nota-fuente-$font.png"
  test -s "screenshots/23-nota-fuente-$font.png"
done
echo "PASS phase34: note editor remains functional at 1.3x and 1.6x Android font sizes"
