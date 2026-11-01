#!/usr/bin/env python3
"""Install the independently validated offline voice-task source patch after phase42."""
from pathlib import Path
import base64
import hashlib
import subprocess
import zlib
root=Path("AgendaClara")
baseline={
 "app/src/main/java/pe/agendaclara/app/CreationChoices.java":"e8d932f4937c84d2f84abdf47e355bcc3b1b8a892ff2952128baf096374c8f6e",
 "app/src/main/java/pe/agendaclara/app/MainActivity.java":"b4875c0b0eca59191d65f98518393a240197a11b2d7578bb39b710b33d0ef8b6",
 "app/src/main/AndroidManifest.xml":"6155de7ecf8d8aebbb9a97531e197624fbf809eeafdf460b6f9c2f49c074b3cb",
 "app/build.gradle":"77dcefbe155260f18be95a7611b52e8c25bac4bfbca07a9e5fa198873a6b0f71",
}
for rel,expected in baseline.items():
    file=root/rel
    if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:
        raise RuntimeError("Unexpected Agenda Clara 3.10.5 baseline; refusing to patch: "+rel)
for name in ["QuickTaskVoiceParser.java","VoiceQuickTask.java"]:
    if (root/"app/src/main/java/pe/agendaclara/app"/name).exists():
        raise RuntimeError("Refusing to overwrite existing quick-task class "+name)
payload=Path(__file__).with_name("voice_patch.zlib.b64")
patch=zlib.decompress(base64.b64decode(payload.read_text(encoding="ascii").strip()))
subprocess.run(["git","apply","--check","-"],input=patch,check=True)
subprocess.run(["git","apply","-"],input=patch,check=True)
print("PASS: voice-task Android source patch applied, 3.10.6 (47)")
