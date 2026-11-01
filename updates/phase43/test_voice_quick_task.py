#!/usr/bin/env python3
"""Regression checks for offline voice and global General category."""
from pathlib import Path
import struct
source=Path("AgendaClara")
java=source/"app/src/main/java/pe/agendaclara/app"
main=(java/"MainActivity.java").read_text("utf-8")
notes=(java/"StickyNotesStore.java").read_text("utf-8")
ui=(java/"StickyNotesUi.java").read_text("utf-8")
voice=(java/"VoiceQuickTask.java").read_text("utf-8")
scope=(java/"GeneralCategoryScope.java").read_text("utf-8")
parser=(java/"QuickTaskVoiceParser.java").read_text("utf-8")
manifest=(source/"app/src/main/AndroidManifest.xml").read_text("utf-8")
gradle=(source/"app/build.gradle").read_text("utf-8")
assert "GeneralCategoryScope.visibleIn(selectedCategory" in main
assert "GeneralCategoryScope.isGeneral(category)" in notes and "? all()" in notes
assert 'if(a.page==0)a.selectedCategory="General";' in ui
assert "isGeneral(String name)" in scope
assert "VoiceQuickTask.show(this)" in main
assert main.count("void onRequestPermissionsResult(")==1
assert "VoiceQuickTask.permissionResult(this,request,permissions,grants);" in main
assert "com.alphacephei:vosk-android" in gradle
assert "versionCode 47" in gradle and "versionName '3.10.6'" in gradle
assert "RECORD_AUDIO" in manifest
assert "new SpeechService(" in voice and "StorageService.unpack" in voice
assert "new FileOutputStream" not in voice and "MediaRecorder" not in voice
assert "transcript.setLength(0)" in voice
assert "Prioridad automática" in voice and "TaskPriority.label" in voice
assert "recordatorio" in parser and "t[ií]tulo" in parser
for symbol in ["microphone","waveform","bell","calendar","notes","check","clock"]:
    path=source/f"app/src/main/res/drawable-nodpi/ic_ref_voice_{symbol}.png"
    data=path.read_bytes()
    assert data[:8]==b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">IIBB",data[16:26])==(256,256,8,6)
print("PASS: voice dictation, permissions, transparent PNGs, automatic priority, global General view")
