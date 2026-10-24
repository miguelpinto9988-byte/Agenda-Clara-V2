#!/usr/bin/env bash
set -euo pipefail
PKG=pe.agendaclara.app
APK=artifact-apk/app-debug.apk
test -s "$APK"
mkdir -p screenshots
adb install -r "$APK"
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/.MainActivity"
sleep 8
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/01-agenda.png

# Exercise actual Activity routes rather than mocking screen state.
adb shell am start -W -a inbox -n "$PKG/.MainActivity"
sleep 4
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/02-revisar.png

adb shell am start -W -a connections --ei tab 2 -n "$PKG/.MainActivity"
sleep 4
adb shell pidof "$PKG" >/dev/null
adb exec-out screencap -p >screenshots/03-ajustes.png

adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity"
sleep 4
adb shell pidof "$PKG" >/dev/null

for image in screenshots/*.png; do test -s "$image" || exit 1; done
echo "PASS: Inicio, bandeja Revisar, Ajustes y relanzamiento tras cierre forzado."
