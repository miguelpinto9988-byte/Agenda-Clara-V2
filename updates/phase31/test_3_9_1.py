#!/usr/bin/env python3
"""Non-destructive regression checks for Agenda Clara sticky-note widget."""
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path("AgendaClara/app/src/main")
SRC=ROOT/"java/pe/agendaclara/app"
APP=SRC/"StickyNotesWidget.java"
widget=APP.read_text(encoding="utf-8")
service=(SRC/"StickyNotesWidgetService.java").read_text(encoding="utf-8")
store=(SRC/"StickyNotesStore.java").read_text(encoding="utf-8")
main=(SRC/"MainActivity.java").read_text(encoding="utf-8")
ui=(SRC/"StickyNotesUi.java").read_text(encoding="utf-8")
manifest=(ROOT/"AndroidManifest.xml").read_text(encoding="utf-8")
category=(SRC/"CategoryRegistry.java").read_text(encoding="utf-8")
system=(SRC/"SystemReceiver.java").read_text(encoding="utf-8")
task=(SRC/"TaskWidget.java").read_text(encoding="utf-8")
assert 'public synchronized List<Note> all(){return fetch(null,null);}' in store
assert 'RemoteCollectionItems.Builder' in widget and 'StickyNotesWidgetService.class' in widget
assert 'new_sticky_note' in widget and 'sticky_widget_note' in widget
assert 'sticky_note_id' in widget and main
assert 'showEditor(this,note)' in main and 'showEditor(this,null)' in main
assert 'setOnClickFillInIntent' in widget and 'setPendingIntentTemplate' in widget
assert 'onAppWidgetOptionsChanged' in widget and 'OPTION_APPWIDGET_MIN_WIDTH' in widget
assert 'new Thread(()->StickyNotesWidget.refresh(a.getApplicationContext())' in ui
assert 'StickyNotesWidget.refresh(this)' in main
assert category.count('StickyNotesWidget.refresh(c)')==2
assert 'StickyNotesWidget.refresh(c)' in system
for text in ('sticky_yellow','sticky_pink','sticky_blue','sticky_green','sticky_purple','sticky_peach'):
    assert 'R.drawable.'+text in widget
assert 'TaskWidget.refresh(this)' in main and 'new_task' in task
nav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav
assert 'dp(26),dp(26)' in nav
assert 'ContentIconSizing.apply(nav)' not in main
assert 'android:resizeMode="horizontal|vertical"' in (ROOT/"res/xml/sticky_notes_widget_info.xml").read_text()
assert 'android:minResizeWidth="180dp"' in (ROOT/"res/xml/sticky_notes_widget_info.xml").read_text()
assert 'android:minResizeHeight="110dp"' in (ROOT/"res/xml/sticky_notes_widget_info.xml").read_text()
assert (ROOT/"res/xml/task_widget_info.xml").is_file()
for name in ("widget_sticky_notes.xml","widget_sticky_row.xml"):
    xml=ET.parse(ROOT/"res/layout"/name).getroot()
    assert xml is not None
    text=(ROOT/"res/layout"/name).read_text()
    assert 'android:textStyle="bold"' in text
for text in ('sticky_widget_header','sticky_widget_add','sticky_widget_list'):
    assert text in (ROOT/"res/layout/widget_sticky_notes.xml").read_text()
for text in ('sticky_widget_title','sticky_widget_body','sticky_widget_date','sticky_widget_art'):
    assert text in (ROOT/"res/layout/widget_sticky_row.xml").read_text()
for name in ("StickyNotesWidget","StickyNotesWidgetService"):
    assert 'android:name=".'+name+'"' in manifest
assert '@xml/sticky_notes_widget_info' in manifest
assert 'android.permission.BIND_REMOTEVIEWS' in manifest
assert 'sticky_widget_description' in (ROOT/"res/values/strings.xml").read_text()
assert 'versionCode 32' in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.9.1'" in Path("AgendaClara/app/build.gradle").read_text()
assert 'Reminders.schedule' not in widget and 't.done' not in widget
print("PASS phase31: independent resizable sticky-note widget, date, plus, live sync, bold previews and unchanged task tabs")
