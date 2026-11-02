#!/usr/bin/env python3
"""Agenda Clara 3.10.8: add natural-language voice task parsing with strict baseline guards."""
from pathlib import Path
import base64
import hashlib
import subprocess
import zlib

root = Path("AgendaClara")
expected = {
    "app/src/main/java/pe/agendaclara/app/QuickTaskVoiceParser.java": "9d715ac1a8f3e2e72384f12929314567e5448bfc56f92dfce1d919e48d0357dc",
    "app/src/main/java/pe/agendaclara/app/VoiceQuickTask.java": "775813e618d4cb3709b69814575e655d7c138fa4a5238d1e56d9c7ab3a0fdacd",
}
for name, digest in expected.items():
    file = root / name
    if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise RuntimeError("Unexpected 3.10.7 source, refusing patch: " + name)
gradle = root / "app/build.gradle"
source = gradle.read_text(encoding="utf-8")
if source.count("versionCode 48") != 1 or source.count("versionName '3.10.7'") != 1:
    raise RuntimeError("Unexpected app version, refusing patch")
blob = Path(__file__).with_name("natural_voice.patch.zlib.b64")
patch = zlib.decompress(base64.b64decode(blob.read_text(encoding="ascii").strip()))
subprocess.run(["git", "apply", "--check", "-"], input=patch, check=True)
subprocess.run(["git", "apply", "-"], input=patch, check=True)
gradle.write_text(source.replace("versionCode 48", "versionCode 49")
    .replace("versionName '3.10.7'", "versionName '3.10.8'"), encoding="utf-8")
print("PASS 3.10.8: natural speech, relative dates, default 23:59, review UI, preserved privacy")
