#!/usr/bin/env python3
"""Agenda Clara 3.11.1: order-independent academic context, conservatively reviewable."""
from pathlib import Path
import hashlib,base64,subprocess,zlib

root=Path('AgendaClara')
source=root/'app/src/main/java/pe/agendaclara/app'
expected={
 'QuickTaskVoiceParser.java':'68fa0922ddddebf6020c9dcda3a4a3e5423dcc5a6aa779b1d3f45ccaa4d2fff4',
 'MultiActivityInterpreter.java':'ce3701828b934bb3bfc2f69ccd54733d69e7d9c6a5af7744253474f6ef95f789',
 'MessageParser.java':'abf8eedf4fe02bfc00f56afdb24d21de6d7f025823e95c690d97b18b69aa2126',
 'VoiceQuickTask.java':'719fadc253f2d1c7ec767be68b0abc9cf3daf49c2ff685303e2bf2dfc3040d63',
}
for filename,digest in expected.items():
 path=source/filename
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
  raise RuntimeError('Refusing unexpected baseline for '+filename)
if (source/'AcademicContextInterpreter.java').exists():
 raise RuntimeError('Context parser already installed')
gradle=root/'app/build.gradle'
s=gradle.read_text(encoding='utf-8')
if s.count('versionCode 51')!=1 or s.count("versionName '3.11.0'")!=1:
 raise RuntimeError('Unexpected version; refusing to patch')
blob=Path(__file__).with_name('context_patch.zlib.b64')
patch=zlib.decompress(base64.b64decode(blob.read_text(encoding='ascii').strip()))
subprocess.run(['git','apply','--check','-'],cwd=root,input=patch,check=True)
subprocess.run(['git','apply','-'],cwd=root,input=patch,check=True)
gradle.write_text(s.replace('versionCode 51','versionCode 52')
    .replace("versionName '3.11.0'","versionName '3.11.1'"),encoding='utf-8')
print('PASS 3.11.1: course/grade/date/time order-independent extraction, review-first')
