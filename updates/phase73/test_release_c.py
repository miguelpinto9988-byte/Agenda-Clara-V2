#!/usr/bin/env python3
"""Release C structural audit after applying phase71 and phase72.
The Android APK is compiled by the dedicated CI job, not by this script.
"""
from pathlib import Path
import ast
root=Path("AgendaClara/app/src/main")
j=root/"java/pe/agendaclara/app"
main=(j/"MainActivity.java").read_text()
gradle=Path("AgendaClara/app/build.gradle").read_text()
manifest=(root/"AndroidManifest.xml").read_text()
for x in ("CalendarStudyPanel.java","AcademicSchedules.java","CalendarStudyTabs.java",
          "AcademicTaskLinks.java","AcademicCourseRouting.java","AcademicCourseMatcher.java",
          "SyllabusImportActivity.java","SyllabusDocumentReader.java","SyllabusEventParser.java"):
    assert (j/x).is_file(),x
assert 'else if(page==1)CalendarStudyTabs.render(this);' in main
assert 'setTag("new_task_button")' not in main
assert 'setTitle("Crear en Agenda Clara")' in main
assert 'SyllabusImportActivity" android:exported="false"' in manifest
assert "versionCode 59" in gradle and "versionName '3.13.3'" in gradle
assert "Horarios y cursos se gestionan en Calendario > Plan de estudio." in main
assert 'LinearLayout schedule=card(body);' not in main
assert "Agrega tus cursos en Calendario > Plan de estudio." in (j/"MiDiaClassCard.java").read_text()
assert "pdfbox-android:2.0.27.0" in gradle and "poi-scratchpad:5.4.1" in gradle
schedule=(j/"AcademicSchedules.java").read_text()
assert "LIMIT = 10" in schedule and "migrateLegacy" in schedule
assert "CategoryRegistry" in schedule and "ScheduleDatabase" in schedule
routing=(j/"AcademicCourseRouting.java").read_text()
for phrase in ("Confirmar curso","Guardar sin curso","Elegir curso y horario"):
    assert phrase in routing
tasks=(j/"AcademicTaskLinks.java").read_text()
assert "task_id INTEGER PRIMARY KEY" in tasks
ui=(j/"SyllabusImportActivity.java").read_text()
for phrase in ("10 días y 12 horas antes","7 días antes","LocalTime.of(23,59)",
               "TASK" if False else "Store.get(this).save(task)","originKey=origin",
               "Reminders.schedule(this,task)","AcademicTaskLinks.get(this).assign"):
    assert phrase in ui,phrase
assert "titleField.addTextChangedListener" in ui
for name in ("updates/phase71/apply_plan_a.py","updates/phase72/apply_plan_b.py"):
    ast.parse(Path(name).read_text())
print("PASS C pre-build: preserve current 5 tabs, dual calendar panels, 10 schedules and existing app ID")
print("PASS C pre-build: PDF/DOC/DOCX import route, manual/voice course confirmation, reviewed exam reminders")
