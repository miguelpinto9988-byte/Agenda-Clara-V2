#!/usr/bin/env bash
# Phase 18: screenshot + foreground verification across small/large Android screens.
set -euo pipefail
APK="artifact-apk/app-debug.apk"
PKG="pe.agendaclara.app"
test -s "$APK"
mkdir -p screenshots
adb install -r "$APK" >/dev/null
restore() {
  adb shell wm size reset >/dev/null 2>&1 || true
  adb shell wm density reset >/dev/null 2>&1 || true
}
trap restore EXIT
check() {
  local label="$1" width="$2" height="$3" density="$4"
  adb shell wm size "$width"x"$height" >/dev/null
  adb shell wm density "$density" >/dev/null
  sleep 2
  adb shell am force-stop "$PKG" >/dev/null || true
  adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
  sleep 4
  test -n "$(adb shell pidof "$PKG" | tr -d '\r')" || {
    echo "FAIL: app stopped at $label"
    exit 1
  }
  adb exec-out screencap -p > "screenshots/phase18-$label.png"
  python3 - "screenshots/phase18-$label.png" "$width" "$height" <<'PY'
from pathlib import Path
from struct import unpack
import sys
p=Path(sys.argv[1]); raw=p.read_bytes()
assert raw[:8]==b'\x89PNG\r\n\x1a\n'
assert unpack('>II',raw[16:24])==(int(sys.argv[2]),int(sys.argv[3]))
assert len(raw)>14000,(p,len(raw))
print("PASS phase18 capture",p.name,len(raw))
PY
  adb shell dumpsys activity activities | grep -q "$PKG" || {
    echo "FAIL: foreground activity missing at $label"
    exit 1
  }
}
check "phone-280dp" 280 640 160
check "phone-320dp" 320 740 160
check "phone-360dp" 360 780 160
check "phone-412dp" 412 860 160
check "tablet-800dp" 800 1100 160
check "landscape-960dp" 960 600 160
restore
echo "PASS phase18: six screen configurations launched and captured"
