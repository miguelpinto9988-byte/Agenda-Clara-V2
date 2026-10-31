#!/usr/bin/env python3
"""Regression tests for large font and compact sticky-note widget."""
from pathlib import Path
import xml.etree.ElementTree as ET
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
layout=Path("AgendaClara/app/src/main/res/layout")
ui=(src/"StickyNotesUi.java").read_text()
w=(src/"StickyNotesWidget.java").read_text()
service=(src/"StickyNotesWidgetService.java").read_text()
assert "getConfiguration().fontScale" in ui
assert "frame.setMinimumHeight(noteHeight(a,large))" in ui
assert "noteHeight(a,false)" in ui and "noteHeight(a,true)+dp(a,3)" in ui
assert "OPTION_APPWIDGET_MIN_HEIGHT" in w and "OPTION_APPWIDGET_MIN_WIDTH" in w
assert "scale>=1.3f" in w and "width<235" in w and "height<170" in w
assert "widget_sticky_row_compact" in w and "widget_sticky_notes_compact" in w
assert "row(context,note,compact)" in w
assert "intent.getBooleanExtra" in service and "notes.get(position),compact" in service
assert "onAppWidgetOptionsChanged" in w
for name in ("widget_sticky_row_compact.xml","widget_sticky_notes_compact.xml"):
    root=ET.parse(layout/name).getroot()
    text=(layout/name).read_text()
    assert 'textStyle="bold"' in text
    assert 'ellipsize="end"' in text
    assert root is not None
r=(layout/"widget_sticky_row_compact.xml").read_text()
assert r.index("sticky_widget_title")<r.index("sticky_widget_calendar_icon")<r.index("sticky_widget_body")
assert '@drawable/ic_ref_date' in r and 'layout_marginEnd="6dp"' in r
nav=(src/"MainActivity.java").read_text()
nav=nav[nav.index("        nav=row();"):nav.index("        View line=new View(this);")]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
assert 'versionCode 35' in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.9.4'" in Path("AgendaClara/app/build.gradle").read_text()
print("PASS phase34: compact widget, font scaling, PNG date, unchanged bottom nav")
