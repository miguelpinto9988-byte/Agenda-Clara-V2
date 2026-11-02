#!/usr/bin/env python3
from pathlib import Path
import struct
root=Path("AgendaClara")
r=root/"app/src/main"
src=r/"java/pe/agendaclara/app"
w=(src/"TaskWidget.java").read_text()
v=(src/"VoiceQuickTask.java").read_text()
a=(src/"WidgetTaskActivity.java").read_text()
m=(r/"AndroidManifest.xml").read_text()
layout=(r/"res/layout/widget_tasks.xml").read_text()
gradle=(root/"app/build.gradle").read_text()
assert "Intent(c,WidgetTaskActivity.class)" in w and "ACTION_CREATE" in w
assert "widget_subtitle" in w and "widget_subtitle" in layout
assert "Mis tareas de hoy" in layout and "#A8ECFF" in layout
assert "Tarea rápida por voz" in a and "Tarea normal" in a
assert "ModernPickers.showDate(this" in a and "ModernPickers.showTime(this" in a
assert "new Task()" in a and "TaskWidget.refresh(this)" in a
assert "SOFT_INPUT_ADJUST_RESIZE" in a and "WindowManager.LayoutParams.WRAP_CONTENT" in a
assert "instanceof WidgetTaskActivity" in v and "ValueAnimator" in v
assert "waveAnimator.cancel()" in v and "voiceActivity" in v
assert 'android:name=".WidgetTaskActivity"' in m and 'android:exported="false"' in m
assert "versionCode 51" in gradle and "versionName '3.11.0'" in gradle
for name in ("brand","plus","voice","manual","cancel"):
    png=(r/"res/drawable-nodpi"/("ic_ref_widget_"+name+".png")).read_bytes()
    assert png[:8]==b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II",png[16:24])==(256,256) and png[25]==6
    assert len(png)<250000
print("PASS 3.11.0 widget: two floating flows, keyboard size policy, animated voice, five transparent PNG icons")
