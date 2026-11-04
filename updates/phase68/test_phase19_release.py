#!/usr/bin/env python3
"""Phase 19: assert exact release version and sanitized resource manifest."""
from pathlib import Path
import ast
import hashlib
import json
gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionCode 57" in gradle and "versionName '3.13.1'" in gradle
assert "applicationId 'pe.agendaclara.app'" in gradle
assert "signingConfig signingConfigs.development" in gradle
for name in ("updates/phase67/test_phase18_regressions.py", "updates/phase68/version_3_13_1.py"):
    ast.parse(Path(name).read_text(encoding="utf-8"), filename=name)
manifest=json.loads(Path("AgendaClara/.mi_dia_bg_clean_v1.json").read_text(encoding="utf-8"))
root=Path("AgendaClara/app/src/main/res/drawable-nodpi")
assert len(manifest["outputs"]) == 30
assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
           for name,digest in manifest["outputs"].items())
print("PASS phase19: correct 3.13.1 signing config, package and 30 revised backgrounds")
