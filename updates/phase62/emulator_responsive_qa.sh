#!/usr/bin/env bash
# Phase 14 responsive smoke: same signed APK on two compact phones + landscape.
# Runs in Android 15 emulator; restores original geometry afterwards.
set -euo pipefail
APK="artifact-apk/app-debug.apk"
if [ "$#" -gt 0 ]; then APK="$1"; fi
test -s "$APK"
mkdir -p screenshots
PKG=pe.agendaclara.app

restore_display() {
  adb shell wm size reset >/dev/null 2>&1 || true
  adb shell wm density reset >/dev/null 2>&1 || true
}
trap restore_display EXIT
adb install -r "$APK" >/dev/null

capture_case() {
  local label="$1" width="$2" height="$3" density="$4"
  adb shell wm size "$width"x"$height" >/dev/null
  adb shell wm density "$density" >/dev/null
  sleep 2
  adb shell am force-stop "$PKG" >/dev/null || true
  adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
  sleep 4
  local output="screenshots/phase14-$label.png"
  adb exec-out screencap -p > "$output"
  python3 - "$output" "$width" "$height" <<'PY'
from pathlib import Path
from struct import unpack
import sys
p=Path(sys.argv[1])
raw=p.read_bytes()
assert raw[:8] == bytes((137, 80, 78, 71, 13, 10, 26, 10)), p
w,h = unpack(">II",raw[16:24])
expect=(int(sys.argv[2]),int(sys.argv[3]))
assert (w,h) == expect, ("Unexpected capture geometry", (w,h), expect)
assert len(raw)>14000, ("Screen appears blank or rendering failed",len(raw))
print("PASS",p.name,w,h,len(raw))
PY
  adb shell dumpsys activity activities | grep -q "$PKG" || {
    echo "ERROR: Agenda Clara did not remain in activity stack at $label"
    exit 1
  }
}
capture_case "compact-320dp" 320 740 160
capture_case "phone-360dp" 360 780 160
capture_case "landscape-960dp" 960 600 160
restore_display
echo "PASS phase14: compact phones and horizontal layout render, screenshots retained"
