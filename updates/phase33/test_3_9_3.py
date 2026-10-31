#!/usr/bin/env python3
"""Regression for six PNG sticky papers and the existing calendar PNG throughout."""
from pathlib import Path
import struct,xml.etree.ElementTree as ET
SRC=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
DRAW=Path("AgendaClara/app/src/main/res/drawable-nodpi")
LAYOUT=Path("AgendaClara/app/src/main/res/layout")
ui=(SRC/"StickyNotesUi.java").read_text(encoding="utf-8")
widget=(SRC/"StickyNotesWidget.java").read_text(encoding="utf-8")
xml=(LAYOUT/"widget_sticky_row.xml").read_text(encoding="utf-8")
nav=(SRC/"MainActivity.java").read_text(encoding="utf-8")
nav=nav[nav.index("        nav=row();"):nav.index("        View line=new View(this);")]
assert 'new UiDesign.OutlineIcon(' in nav and "dp(26),dp(26)" in nav
assert "TextView date=text(a,note.day.format(" in ui
assert 'ApprovedPng.view(a,"date",20)' in ui
assert "dateIconSpace.rightMargin=dp(a,8)" in ui
assert "content.addView(dateRow)" in ui
assert 'ImageView.ScaleType.FIT_XY' in ui and 'FrameLayout preview' in ui
assert 'UiDesign.text(' in ui or 'a.text(' in ui
assert 'DATE.format(note.day)' in widget and '"▦' not in widget
assert "sticky_widget_calendar_icon" in xml
assert '@drawable/ic_ref_date' in xml and 'android:layout_marginEnd="8dp"' in xml
assert 'android:textStyle="bold"' in xml
ET.parse(LAYOUT/"widget_sticky_row.xml")
assert (DRAW/"ic_ref_date.png").read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
for name in ("yellow","pink","blue","green","purple","peach"):
    data=(DRAW/("sticky_"+name+".png")).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack(">II",data[16:24])==(800,460)
    assert len(data)>15000, name
assert 'versionCode 34' in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.9.3'" in Path("AgendaClara/app/build.gradle").read_text()
assert 'StickyNotesStore.get(a).save(note)' in ui
assert 'sticky_note_id' in widget
print("PASS phase33: six polished PNGs; calendar PNG/date gap in editor/agenda/widget; bold text; original navigation")
