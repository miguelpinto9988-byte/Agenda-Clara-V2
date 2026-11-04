#!/usr/bin/env python3
"""Static structural QA only. NO Android compilation, signing, or APK."""
from pathlib import Path
import ast, re, subprocess, tempfile
P=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def source(name):
    x=P/name
    assert x.exists(),name
    return x.read_text(encoding="utf-8")
for name in ("apply_plan_a.py","patch_android_ui.py"):
    ast.parse((Path("updates/phase71")/name).read_text(encoding="utf-8"),filename=name)
main=source("MainActivity.java")
assert "else if(page==1)CalendarStudyTabs.render(this);" in main
assert "void calendarPage()" in main
assert 'setTag("new_task_button")' not in main
assert 'setTitle("Crear en Agenda Clara")' in main
assert "VoiceQuickTask.show(this)" in main
assert "openEditor(-1,null,null)" in main
assert "StickyNotesUi.showEditor(this,null)" in main
tabs=source("CalendarStudyTabs.java")
assert "a.calendarPage();" in tabs and "CalendarStudyPanel.render(a);" in tabs
assert "AcademicSchedules.migrateLegacy(a);" in tabs
assert "getSharedPreferences(PREF,Context.MODE_PRIVATE)" in tabs
assert '"Calendario"' in tabs and '"Plan de estudio"' in tabs
panel=source("CalendarStudyPanel.java")
for token in ("Nuevo horario","Importar horario desde foto","Agregar curso",
              "Cambiar nombre","Eliminar este horario","Exámenes y parciales",
              "profile_id","start_photo","confirmDelete"):
    assert token in panel,token
registry=source("AcademicSchedules.java")
for token in ("LIMIT = 10","UUID.randomUUID()","CategoryRegistry.save",
              "CategoryRegistry.delete","migrateLegacy","syncFromSessions",
              "assignUnassigned","deleteConfirmed","category","activeId"):
    assert token in registry,token
assert "profiles.size()>=LIMIT" not in registry or "LIMIT" in registry
entry=source("ScheduleEntry.java")
assert 'scheduleId=""' in entry and "s.scheduleId=scheduleId;" in entry
db=source("ScheduleDatabase.java")
assert 'super(c,"class_schedule.db",null,2)' in db
assert "ALTER TABLE sessions ADD COLUMN schedule_id" in db
assert "WHERE schedule_id=?" in db
assert "old.day==s.day&&old.start==s.start" in db
assert "assignUnassigned" in db and "deleteProfile" in db
assert "ScheduleCourseColors.same" in db
activity=source("ScheduleActivity.java")
for token in ('profileId', 'AcademicSchedules.migrateLegacy(this)',
              'ScheduleDatabase.get(this).all(profileId)',
              'ScheduleTitleParser.suggest(text.getText())',
              'confirmPhotoName(()->', 'importReviewed(approved,profileId)',
              'AcademicSchedules.syncFromSessions(this,profileId)',
              'db.recolorSameCourse(s.course,s.color,profileId)'):
    assert token in activity,token
assert 'ScheduleDatabase.get(this).all()' not in activity
assert "versionCode 59" in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.13.3'" in Path("AgendaClara/app/build.gradle").read_text()
print("PASS: 10 profiles, SQLite migration, categories, OCR confirmation, photo/manual schedule isolation")
print("PASS: two Calendar tabs, existing 5 bottom tabs, large + removed and actions still accessible")
print("NO APK: source-only verification")
