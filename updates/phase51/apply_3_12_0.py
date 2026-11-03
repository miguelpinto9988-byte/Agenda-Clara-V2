#!/usr/bin/env python3
"""Patch the verified 3.11.3 app to modular 3.12.0 without replacing persisted data."""
from pathlib import Path
import base64,hashlib,subprocess,zlib
ROOT=Path('AgendaClara')
GRADLE=ROOT/'app/build.gradle'
text=GRADLE.read_text(encoding='utf8')
assert text.count('versionCode 54')==1 and text.count("versionName '3.11.3'")==1,'Expected 3.11.3 baseline'
assert not (ROOT/'app/src/main/java/pe/agendaclara/app/ExamActivity.java').exists(),'Already patched'
encoded=(Path(__file__).parent/'source.patch.zlib.b64').read_text(encoding='ascii')
patch=zlib.decompress(base64.b64decode(encoded))
for check in (True,False):
    command=['git','apply','--directory=AgendaClara','-']
    if check:command.insert(2,'--check')
    subprocess.run(command,input=patch,check=True)
print('PASS 3.12.0 source patched: Mi guía, Calendar/Study plans, exams, matte icon routing')
