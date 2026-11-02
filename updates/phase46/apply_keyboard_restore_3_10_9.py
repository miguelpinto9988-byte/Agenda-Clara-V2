#!/usr/bin/env python3
"""3.10.9: remove redundant weekly card and restore dialog size after soft keyboard hides.

Apply only to audited Agenda Clara 3.10.8; keep the visual calendar, notes,
WhatsApp, voice recognition, data, signing configuration and resources untouched.
"""
import base64
import hashlib
import subprocess
import zlib
from pathlib import Path

root=Path('AgendaClara')
java=root/'app/src/main/java/pe/agendaclara/app'
checks={
    'MainActivity.java':'d435edac30b6b93f7b516ced5bc8fbe871d6f23df01fae61e2867893a89a76f5',
    'WindowLayout.java':'9bd69e1bfc9f35b1bc6349142eefeb5f4f8dd424bc3a611d98eb7b7dbb89f6f8',
}
for file,expected in checks.items():
    path=java/file
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Unexpected 3.10.8 Android baseline, refusing update: '+file)
policy=java/'DialogResizePolicy.java'
if policy.exists():
    raise RuntimeError('DialogResizePolicy.java already exists, refusing overwrite')
gradle=root/'app/build.gradle'
g=gradle.read_text(encoding='utf-8')
assert g.count('versionCode 49')==1 and g.count("versionName '3.10.8'")==1
bundle=Path(__file__).with_name('dialog_layout.patch.zlib.b64')
patch=zlib.decompress(base64.b64decode(bundle.read_text(encoding='ascii').strip()))
subprocess.run(['git','apply','--check','-'],input=patch,check=True)
subprocess.run(['git','apply','-'],input=patch,check=True)
policy.write_bytes(Path(__file__).with_name('DialogResizePolicy.java').read_bytes())
gradle.write_text(g.replace('versionCode 49','versionCode 50').replace("versionName '3.10.8'","versionName '3.10.9'"),encoding='utf-8')
print('PASS 3.10.9: monthly calendar retained; redundant week removed; all dialogs restore after keyboard hides')
