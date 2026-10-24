#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
test -s artifact-apk/app-debug.apk
mkdir -p screenshots
adb install -r artifact-apk/app-debug.apk
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 5
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/01-agenda-java.png
adb shell am start -W -n "$PKG/.ComposeDayActivity"
sleep 7
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/02-vista-diaria-compose.png
adb shell am start -W -a inbox -n "$PKG/.MainActivity"
sleep 4
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/03-revisar-java.png
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity"
sleep 3
adb shell pidof "$PKG" >/dev/null
for file in screenshots/*.png; do test -s "$file"; done
echo "PASS: install; Java agenda; Kotlin Compose overview; review; restart."
