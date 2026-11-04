#!/usr/bin/env python3
"""Static diagnostic and normalized-asset checks for phases 15–17.
Does NOT build, sign, install or launch an APK.
"""
from pathlib import Path
import ast
import hashlib
import json
from PIL import Image
import xml.etree.ElementTree as ET

MAIN = Path("AgendaClara/app/src/main")
CODE = MAIN / "java/pe/agendaclara/app"
HEADER = CODE / "MiDiaHeaderView.java"
ROTATION = CODE / "MiDiaDailyRotation.java"
MANIFEST = Path("AgendaClara/.mi_dia_bg_clean_v1.json")
ROOT = MAIN / "res/drawable-nodpi"

for relative in ("updates/phase64/apply_header_blends.py",
                 "updates/phase65/normalize_backgrounds.py"):
    source = Path(relative)
    ast.parse(source.read_text(encoding="utf-8"), filename=str(source))

head = HEADER.read_text(encoding="utf-8")
rotation = ROTATION.read_text(encoding="utf-8")
for name in ("mi_dia_hero_edge_top", "mi_dia_hero_edge_bottom",
             "landscapeFrame.setClipChildren(true)",
             "landscapeFrame.setClipToPadding(true)",
             "new FrameLayout.LayoutParams(-1, dp(68), Gravity.TOP)",
             "new FrameLayout.LayoutParams(-1, dp(74), Gravity.BOTTOM)",
             "MiDiaDailyRotation.backgroundResource(getContext(), today)",
             "MiDiaDailyRotation.quote(getContext(), today)",
             "quote.setVisibility(View.GONE)"):
    assert name in head, name

assert "ChronoUnit.DAYS.between(EPOCH, day), 30" in rotation
assert "ChronoUnit.DAYS.between(EPOCH, day) * 7, 50" in rotation
quotes = ET.parse(MAIN / "res/values/mi_dia_frases.xml").getroot()
phrases = quotes.find("./string-array[@name='mi_dia_frases']")
assert phrases is not None and len(phrases.findall("item")) == 50
assert MANIFEST.is_file(), "Phase17 must normalize the backgrounds first"
info = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert info.get("algorithm") == "mirror-nearby-scenery-feathered-v1"
assert info.get("count") == 30
assert len(info["source"]) == len(info["outputs"]) == 30
assert info.get("patch", {}).get("opaque_until_x") == 455

found = []
for i in range(1, 31):
    file = ROOT / ("bg_mi_dia_%02d.png" % i)
    assert file.is_file(), file
    sha = hashlib.sha256(file.read_bytes()).hexdigest()
    assert info["outputs"].get(file.name) == sha, file
    with Image.open(file) as im:
        assert im.size == (1920, 864), file
        assert im.mode in ("P", "RGB"), file
    found.append(sha)
assert len(set(found)) == 30
assert len(set(info["source"].values())) == 30
assert all(info["source"][file] != info["outputs"][file] for file in info["outputs"])
print("PASS phases15-17: source badge diagnosis, white edge fades, 30 corrected unique PNGs")
print("PASS: old motivational quotes and rotation untouched; no APK generated")
