#!/usr/bin/env python3
"""Calendar 3.10.7: preserve records, show independent task/note PNG indicators."""
import base64,hashlib,json,shutil,zlib
from pathlib import Path
ROOT=Path("AgendaClara")
MAIN=ROOT/"app/src/main/java/pe/agendaclara/app/MainActivity.java"
JAVA=MAIN.parent
RES=ROOT/"app/src/main/res/drawable-nodpi"
GRADLE=ROOT/"app/build.gradle"
expected="d364f37c414081de2affbbf46b30a2c6e6d152075157002652e048cd91be141f"
if not MAIN.exists() or hashlib.sha256(MAIN.read_bytes()).hexdigest()!=expected:
    raise RuntimeError("Expected exact Agenda Clara 3.10.6 MainActivity; refusing cross-version patch")
data=json.loads(zlib.decompress(base64.b64decode(Path(__file__).with_name("calendar_impl.zlib.b64").read_text().strip())))
source=MAIN.read_text(encoding="utf-8")
begin=source.index("    void calendarPage(){")
end=source.index("    void addCell(GridLayout g",begin)
for name in ("CalendarDaySummary.java","CalendarVisuals.java"):
    dest=JAVA/name
    if dest.exists():raise RuntimeError("Refusing to overwrite "+str(dest))
if not (RES/"ic_ref_today_jump.png").is_file() or not (RES/"ic_ref_sticky_note.png").is_file():
    raise RuntimeError("Approved PNG references missing")
if hashlib.sha256((RES/"ic_ref_today_jump.png").read_bytes()).hexdigest()!="77ac80884cdc2448d8318258e2ba6d5277654e64f4fb7311ad80c7bf1578af4e":
    raise RuntimeError("Task calendar icon provenance changed")
if hashlib.sha256((RES/"ic_ref_sticky_note.png").read_bytes()).hexdigest()!="c1f9bf06eec4105f78d7cdbdc42274b797aaa2f66bc976914dd227d244533d02":
    raise RuntimeError("Sticky-note icon provenance changed")
gradle=GRADLE.read_text()
assert gradle.count("versionCode 47")==1 and gradle.count("versionName '3.10.6'")==1
MAIN.write_text(source[:begin]+data["calendar_method"]+source[end:],encoding="utf-8")
for name in ("CalendarDaySummary.java","CalendarVisuals.java"):
    (JAVA/name).write_text(data[name],encoding="utf-8")
# 256px RGBA transparent PNGs, copied from the app's existing approved artwork.
for name,old in (("task","ic_ref_today_jump.png"),("note","ic_ref_sticky_note.png")):
    target=RES/("ic_ref_calendar_"+name+".png")
    if target.exists():raise RuntimeError("Refusing to overwrite "+str(target))
    raw=(RES/old).read_bytes()
    if raw[:8]!=b"\x89PNG\r\n\x1a\n" or raw[25]!=6:raise RuntimeError("Expected RGBA PNG "+old)
    target.write_bytes(raw)
GRADLE.write_text(gradle.replace("versionCode 47","versionCode 48")
    .replace("versionName '3.10.6'","versionName '3.10.7'"))
print("PASS 3.10.7: dual calendar indicators, transparent PNG artwork, no data migration")
