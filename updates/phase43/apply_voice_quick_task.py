#!/usr/bin/env python3
"""Integrate the verified 3.10.6 offline voice feature and aggregate General view."""
from pathlib import Path
import base64
import hashlib
import shutil
import struct
import subprocess
import zlib

ROOT = Path("AgendaClara")
STAGE = Path(__file__).resolve().parent
BASELINE = {
    "app/build.gradle": "77dcefbe155260f18be95a7611b52e8c25bac4bfbca07a9e5fa198873a6b0f71",
    "app/src/main/java/pe/agendaclara/app/MainActivity.java": "b4875c0b0eca59191d65f98518393a240197a11b2d7578bb39b710b33d0ef8b6",
}
for relative, digest in BASELINE.items():
    file = ROOT / relative
    if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise RuntimeError("Unexpected 3.10.5 source baseline: " + relative)

for name in ("voice-task.patch.zlib.b64", "general-voice-fix.patch.zlib.b64"):
    patch = zlib.decompress(base64.b64decode((STAGE / name).read_text("ascii").strip()))
    subprocess.run(["git", "apply", "--check", "-"], input=patch, check=True)
    subprocess.run(["git", "apply", "-"], input=patch, check=True)

images = ("microphone", "waveform", "bell", "calendar", "notes", "check", "clock")
destination = ROOT / "app/src/main/res/drawable-nodpi"
for name in images:
    filename = "ic_ref_voice_" + name + ".png"
    source = STAGE / "assets" / filename
    target = destination / filename
    if target.exists():
        raise RuntimeError("Refusing to overwrite icon " + filename)
    raw = source.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Not a PNG: " + filename)
    w, h, depth, kind = struct.unpack(">IIBB", raw[16:26])
    if (w, h, depth, kind) != (256, 256, 8, 6):
        raise RuntimeError("Expected 256x256 RGBA transparent icon: " + filename)
    shutil.copyfile(source, target)

gradle = (ROOT / "app/build.gradle").read_text("utf-8")
if "versionCode 47" not in gradle or "versionName '3.10.6'" not in gradle:
    raise RuntimeError("Unexpected Android version after applying patch")
if not (ROOT / "app/src/main/java/pe/agendaclara/app/GeneralCategoryScope.java").is_file():
    raise RuntimeError("General aggregate view is missing")
print("PASS: Vosk offline voice task, seven vivid transparent icons and General aggregate view 3.10.6")
