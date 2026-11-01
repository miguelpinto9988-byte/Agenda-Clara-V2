#!/usr/bin/env python3
"""Install verified offline Vosk Spanish model (Apache-2.0) into APK assets."""
from pathlib import Path
import hashlib
import io
import urllib.request
import zipfile

URLS = [
    "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
    "https://github.com/BartekReterski/VoskModels/releases/download/v1/vosk-model-small-es-0.42.zip",
]
EXPECTED = "09b239888f633ef2f0b4e09736e3d9936acfd810bc65d53fad45261762c6511f"
OUT = Path("AgendaClara/app/src/main/assets/vosk_es")
if OUT.exists():
    raise RuntimeError("Refusing to overwrite existing Vosk model directory")
payload = None
for url in URLS:
    try:
        print("Downloading official model or verified mirror", flush=True)
        request = urllib.request.Request(url, headers={"User-Agent": "AgendaClara-Installer/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read(50_000_000)
        if hashlib.sha256(raw).hexdigest() != EXPECTED:
            raise RuntimeError("Model SHA-256 does not match pinned archive")
        payload = raw
        break
    except Exception as error:
        print("Model source unavailable:", str(error)[:100], flush=True)
if payload is None:
    raise RuntimeError("Could not obtain the verified Vosk Spanish model; no incomplete APK will be built")
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    members = archive.infolist()
    for info in members:
        parts = Path(info.filename).parts
        if info.is_dir() or len(parts) < 2:
            continue
        relative = Path(*parts[1:])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("Untrusted model archive path")
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(info))
# StorageService checks uuid to refresh the extracted private model assets.
(OUT / "uuid").write_text("AgendaClara-es-0.42-" + EXPECTED + "\n", encoding="utf-8")
assert (OUT / "am/final.mdl").is_file() and (OUT / "conf/model.conf").is_file()
print("PASS: verified Spanish Vosk 0.42 model installed in APK assets, no audio recordings")
