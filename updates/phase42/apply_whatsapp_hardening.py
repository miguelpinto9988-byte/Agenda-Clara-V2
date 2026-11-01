#!/usr/bin/env python3
"""Apply 3.10.5 WhatsApp hardening to the exact 3.10.4 build source only."""
from pathlib import Path
import base64
import hashlib
import subprocess
import zlib

root = Path("AgendaClara")
baseline = {
    "whatsapp-native/main.go": "a086039c4d43e21a2e91f6b29a1883a7c7cee1702807804e49959d55ba62f9de",
    "whatsapp-native/main_test.go": "632dc8811375f6843bca5a1b475dba6e66ccef26422604d2b79a4932e99b2361",
    "app/src/main/java/pe/agendaclara/app/WhatsAppSessionService.java": "52864beff92c7b40c2f420693535290a2fcc2af8bd6f488e5a8971eb4751d49d"
}
for relative, expected in baseline.items():
    target = root / relative
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise RuntimeError("Unexpected 3.10.4 baseline; refusing to patch: " + relative)
gradle = (root / "app/build.gradle").read_text(encoding="utf-8")
assert gradle.count("versionCode 45") == 1 and gradle.count("versionName '3.10.4'") == 1
payload = Path(__file__).with_name("whatsapp-hardening.patch.zlib.b64")
patch = zlib.decompress(base64.b64decode(payload.read_text(encoding="ascii").strip()))
subprocess.run(["git", "apply", "--check", "-"], input=patch, check=True)
subprocess.run(["git", "apply", "-"], input=patch, check=True)
print("PASS 3.10.5: invalid pairing codes clear, failure events classified, tests added")
