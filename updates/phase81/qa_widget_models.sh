#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
javac -encoding UTF-8 -d "$OUT" updates/phase81/AcademicWidgetModels.java updates/phase81/AcademicWidgetModelsTests.java
java -cp "$OUT" pe.agendaclara.app.AcademicWidgetModelsTests
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
for path in Path("updates/phase81").glob("*.xml"):
    ET.parse(path)
    print("PASS XML",path)
assert "PhotoWidget" not in " ".join(p.name for p in Path("updates/phase81").iterdir())
print("PASS: photo widget unchanged")
PY
