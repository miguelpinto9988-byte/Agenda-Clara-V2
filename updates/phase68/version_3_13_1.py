#!/usr/bin/env python3
"""Phase 19: bump to 3.13.1 signed preview, preserving key and package."""
from pathlib import Path
path=Path("AgendaClara/app/build.gradle")
s=path.read_text(encoding="utf-8")
if "versionCode 57" in s and "versionName '3.13.1'" in s:
    print("PASS phase19: already at 3.13.1")
else:
    assert s.count("versionCode 56") == s.count("versionName '3.13.0'") == 1, "Unexpected version"
    s=s.replace("versionCode 56", "versionCode 57", 1).replace("versionName '3.13.0'", "versionName '3.13.1'", 1)
    assert "applicationId 'pe.agendaclara.app'" in s
    assert "signingConfig signingConfigs.development" in s
    path.write_text(s, encoding="utf-8")
    print("PASS phase19: versionCode 57; signed 3.13.1 preview")
