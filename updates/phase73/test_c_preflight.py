#!/usr/bin/env python3
"""Phase C preflight: audit A+B sources before enabling Android compilation."""
from pathlib import Path
import ast
from xml.etree import ElementTree as ET
root=Path("AgendaClara/app/src/main")
java=root/"java/pe/agendaclara/app"
for p in ("MainActivity.java","VoiceQuickTask.java","AcademicSchedules.java",
          "CalendarStudyPanel.java","CalendarStudyTabs.java","AcademicCourseMatcher.java",
          "AcademicTaskLinks.java","AcademicCourseRouting.java","SyllabusEventParser.java",
          "SyllabusDocumentReader.java","SyllabusImportActivity.java"):
    assert (java/p).is_file(),p
main=(java/"MainActivity.java").read_text()
assert "CalendarStudyTabs.render(this)" in main
assert "AcademicCourseRouting.review(this,t.title" in main
voice=(java/"VoiceQuickTask.java").read_text()
assert "AcademicCourseRouting.review(activity,spoken" in voice
panel=(java/"CalendarStudyPanel.java").read_text()
assert "SyllabusImportActivity.class" in panel
assert "Agregar examen o entrega manualmente" in panel
links=(java/"AcademicTaskLinks.java").read_text()
assert "profile_id" in links and "task_id" in links
reader=(java/"SyllabusDocumentReader.java").read_text()
assert "MAX_INPUT=12*1024*1024" in reader
assert "MAX_PAGES=120" in reader
assert "Tasks.await(ocr.process" in reader
screen=(java/"SyllabusImportActivity.java").read_text()
assert "ACTION_OPEN_DOCUMENT" in screen
assert "reminderSelection" in screen
assert "row.title.trim().length()<3" in screen
assert "Store.get(this).findOrigin(origin)" in screen
assert "AcademicTaskLinks.get(this).assign" in screen
assert "15120" in screen and "10080" in screen
manifest=ET.parse(root/"AndroidManifest.xml").getroot()
android="{http://schemas.android.com/apk/res/android}"
activities=manifest.findall(".//activity")
assert sum(1 for x in activities if x.get(android+"name")==".SyllabusImportActivity")==1
assert next(x for x in activities if x.get(android+"name")==".SyllabusImportActivity").get(android+"exported")=="false"
gradle=Path("AgendaClara/app/build.gradle").read_text()
for dependency in ("com.tom-roush:pdfbox-android","org.apache.poi:poi-scratchpad",
                   "com.google.mlkit:text-recognition"):
    assert dependency in gradle,dependency
assert "versionCode 59" in gradle and "versionName '3.13.3'" in gradle
print("PASS Entrega C preflight: pestañas, categorías, voz, manual, OCR, importación, recordatorios y manifest")
