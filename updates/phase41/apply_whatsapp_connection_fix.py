#!/usr/bin/env python3
"""Apply the pinned Agenda Clara 3.10.4 WhatsApp correction after phase 40.
The payload is a compressed unified diff. Baseline hashes prevent cross-version edits.
No credentials, sessions or message databases are modified.
"""
from pathlib import Path
import base64
import hashlib
import subprocess
import zlib

ROOT = Path("AgendaClara")
PAYLOAD = Path(__file__).with_name("whatsapp-source.patch.zlib.b64")
EXPECTED = {
    "whatsapp-native/main.go": "388005a71d04072b536035fdcd713f7ea133419fbc6cc4173b0bad38c2956c5d",
    "whatsapp-native/main_test.go": "4bd1eca7aa87cc362fb7525aad74eb940ac698d1e76173aad8f9fd1fb94b461a",
    "app/src/main/java/pe/agendaclara/app/WhatsAppSessionService.java": "6ecb36135d8db954f619ef6996958a2f1c63c0bed32a6fe48a6d6800f7d0c827",
}
for relative, digest in EXPECTED.items():
    file = ROOT / relative
    if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise RuntimeError("Unexpected 3.10.3 baseline; abort: " + str(file))

patch = zlib.decompress(base64.b64decode(PAYLOAD.read_text(encoding="ascii").strip()))
subprocess.run(["git", "apply", "--check", "-"], input=patch, check=True)
subprocess.run(["git", "apply", "-"], input=patch, check=True)

gradle = ROOT / "app/build.gradle"
source = gradle.read_text(encoding="utf-8")
if source.count("versionCode 44") != 1 or source.count("versionName '3.10.3'") != 1:
    raise RuntimeError("Unexpected Android version; refusing to update")
gradle.write_text(source.replace("versionCode 44", "versionCode 45").replace("versionName '3.10.3'", "versionName '3.10.4'"), encoding="utf-8")
print("PASS: WhatsApp fixes installed, version 3.10.4 candidate")
