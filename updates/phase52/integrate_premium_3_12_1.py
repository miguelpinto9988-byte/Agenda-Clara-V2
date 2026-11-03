#!/usr/bin/env python3
"""Integrate the verified 256px premium PNG catalog into the existing Android app.

Only ic_adapt_*.png art, catalog metadata, license notice and app version change.
User courses, notes, databases, categories and other preexisting PNGs are untouched.
"""
from pathlib import Path
from PIL import Image
import json, hashlib
BASE=Path("AgendaClara")
RES=BASE/"app/src/main/res/drawable-nodpi"
ASSETS=BASE/"app/src/main/assets"
REPORT=Path("icon_pro_artifacts")
META=REPORT/"MANIFEST.json"
GRADLE=BASE/"app/build.gradle"
CATALOG=ASSETS/"adaptive_icon_catalog.json"
info=json.loads(META.read_text(encoding="utf-8"))
icons=sorted(RES.glob("ic_adapt_*.png"))
assert info["count"]==328 and len(icons)==328, "Expected 328 icon assets"
size=sum(p.stat().st_size for p in icons)
assert size==info["png_bytes"] and size<=15_000_000, "Library size limit exceeded"
assert info["distinct_base_drawings"]>=100, "Insufficient artistic variety"
entries={x["key"]:x for x in info["icons"]}
assert len(entries)==328
checks=set()
for p in icons:
    key=p.stem.removeprefix("ic_adapt_")
    assert key in entries
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entries[key]["sha256"],key
    with Image.open(p) as im:
        assert im.size==(256,256)
        assert im.convert("RGBA").getpixel((0,0))[3]==0,key
    checks.add(entries[key]["sha256"])
assert len(checks)>=300,"Too many identical icons"
old=json.loads(CATALOG.read_text(encoding="utf-8"))
assert old["count"]==328
old["png_bytes"]=size
old["render_style"]="3D suave y detallado, objetos multicolores, transparencia PNG, sin acabado brillante uniforme"
old["icon_resolution"]=[256,256]
old["source"]="Microsoft Fluent Emoji 3D — MIT"
CATALOG.write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
licences=ASSETS/"licenses"
licences.mkdir(parents=True,exist_ok=True)
(licences/"microsoft-fluent-emoji-MIT.txt").write_text((REPORT/"LICENSE-MIT.txt").read_text(encoding="utf-8"),encoding="utf-8")
(ASSETS/"adaptive_icon_sources.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s=GRADLE.read_text(encoding="utf-8")
assert s.count("versionCode 55")==1 and s.count("versionName '3.12.0'")==1
GRADLE.write_text(s.replace("versionCode 55","versionCode 56").replace("versionName '3.12.0'","versionName '3.12.1'"),encoding="utf-8")
print(f"PASS 3.12.1 integrated {len(icons)} PNG 256px, {len(checks)} unique, {size} bytes; source/license preserved")
