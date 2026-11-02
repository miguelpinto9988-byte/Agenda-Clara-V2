#!/usr/bin/env python3
"""Regression: approved widget icons, note waves, floating selector and keyboard."""
from pathlib import Path
import hashlib,struct,xml.etree.ElementTree as ET

root=Path("AgendaClara")
res=root/"app/src/main/res"
src=root/"app/src/main/java/pe/agendaclara/app"
android="{http://schemas.android.com/apk/res/android}"

for key in ("brand","voice","manual","wave","ribbon"):
 p=res/"drawable-nodpi"/("ic_ref_widget_art_"+key+".png")
 raw=p.read_bytes()
 assert raw.startswith(b"\x89PNG\r\n\x1a\n"),p
 w,h,depth,color=struct.unpack(">IIBB",raw[16:26])
 if key=="ribbon":assert (w,h,depth,color)==(900,110,8,6)
 else:assert (w,h,depth)==(256,256,8) and color in (3,6)

for name in ("widget_sticky_notes.xml","widget_sticky_notes_compact.xml"):
 root_xml=ET.parse(res/"layout"/name).getroot()
 imgs=[el.attrib.get(android+"src") for el in root_xml.iter("ImageView")]
 assert "@drawable/ic_ref_widget_art_wave" in imgs
 assert "@drawable/ic_ref_widget_art_ribbon" in imgs
 add=next(el for el in root_xml.iter("TextView") if el.attrib.get(android+"id")=="@+id/sticky_widget_add")
 assert add.attrib[android+"text"]=="＋"
 assert add.attrib[android+"contentDescription"]=="Crear una nota adhesiva"

for name in ("widget_tasks.xml","widget_sticky_row.xml","widget_sticky_row_compact.xml"):
 ET.parse(res/"layout"/name)

activity=(src/"WidgetTaskActivity.java").read_text("utf8")
for token in ("\"Agenda Clara\",\"Nueva tarea\"","widget_art_brand","widget_art_voice",
 "widget_art_manual","¿Cómo quieres agregar la tarea?","renderNormal()",
 "VoiceQuickTask.show(this)","WindowInsets.Type.ime()","applyWindowSize()"):
 assert token in activity,token
voice=(src/"VoiceQuickTask.java").read_text("utf8")
assert "widget_art_voice" in voice
assert "waveAnimator.start()" in voice and "releaseAudio()" in voice
assert "voiceActivity=Math.max" in voice
assert "WidgetTaskActivity" in voice
widget=(src/"StickyNotesWidget.java").read_text("utf8")
assert "StickyNotesStore.get(context).all()" in widget
manifest=(res.parent/"AndroidManifest.xml").read_text("utf8")
assert 'android:name=".WidgetTaskActivity" android:exported="false"' in manifest
grad=(root/"app/build.gradle").read_text("utf8")
assert "versionCode 54" in grad and "versionName '3.11.3'" in grad
# Existing icon images are not overwritten.
assert (res/"drawable-nodpi/ic_ref_widget_plus.png").is_file()
assert (res/"drawable-nodpi/sticky_yellow.png").is_file()
print("PASS 3.11.3: icon PNG, wave artwork, note widget, chooser and keyboard routes")
