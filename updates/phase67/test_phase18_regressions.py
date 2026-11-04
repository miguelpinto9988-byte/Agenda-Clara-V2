#!/usr/bin/env python3
"""Phase 18 static QA: all landscape badges removed, all daily phrases retained."""
from pathlib import Path
from hashlib import sha256
import json
import xml.etree.ElementTree as ET
from PIL import Image

APP = Path("AgendaClara/app/src/main")
ROOT = APP / "res/drawable-nodpi"
CODE = APP / "java/pe/agendaclara/app"
manifest = Path("AgendaClara/.mi_dia_bg_clean_v1.json")
assert manifest.is_file(), "Missing phase 17 manifest"
m = json.loads(manifest.read_text(encoding="utf-8"))
assert m["count"] == 30 and len(m["outputs"]) == len(m["source"]) == 30
assert m["algorithm"] == "mirror-nearby-scenery-feathered-v1"
found = []
for i in range(1, 31):
    path = ROOT / ("bg_mi_dia_%02d.png" % i)
    assert path.is_file(), path
    assert sha256(path.read_bytes()).hexdigest() == m["outputs"][path.name]
    with Image.open(path) as image:
        assert image.size == (1920, 864) and image.mode in ("P", "RGB")
        rgb = image.convert("RGB")
        for x, y in ((25, 25), (110, 25), (180, 60), (300, 75)):
            assert rgb.getpixel((x, y)) == rgb.getpixel((1119 - x, y)), (path, x, y)
    found.append(m["outputs"][path.name])
assert len(set(found)) == 30
assert all(m["source"][name] != m["outputs"][name] for name in m["outputs"])
header = (CODE / "MiDiaHeaderView.java").read_text(encoding="utf-8")
dashboard = (CODE / "MiDiaDashboard.java").read_text(encoding="utf-8")
rotation = (CODE / "MiDiaDailyRotation.java").read_text(encoding="utf-8")
for token in ("mi_dia_hero_edge_top", "mi_dia_hero_edge_bottom",
              "landscapeFrame.setClipChildren(true)",
              "new int[]{0xffffffff, 0x8cffffff, 0x00ffffff}",
              "new int[]{0x00ffffff, 0x58ffffff, 0xffffffff}",
              "landscape.setScaleType(ImageView.ScaleType.CENTER_CROP)",
              "greeting.setMaxLines(2)", "floatingDate"):
    assert token in header, token
assert "addQuote(activity, body, today);" in dashboard
assert "MiDiaQuickActions.add(activity, body);" in dashboard
assert "MiDiaActivitiesUi.addCourse(activity, body," in dashboard
assert "ChronoUnit.DAYS.between(EPOCH, day), 30" in rotation
assert "ChronoUnit.DAYS.between(EPOCH, day) * 7, 50" in rotation
phrases = APP / "res/values/mi_dia_frases.xml"
assert phrases.read_bytes() == Path("updates/phase51/mi_dia_frases.xml").read_bytes()
assert len(ET.parse(phrases).getroot().find("./string-array[@name='mi_dia_frases']").findall("item")) == 50
print("PASS phase18: 30 sanitized landscapes, edge fades, core home features and 50 unmodified phrases")
