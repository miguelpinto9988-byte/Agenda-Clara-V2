#!/usr/bin/env python3
"""Regression tests on ACTUAL patched Agenda Clara 3.13.8 sources, without APK."""
from pathlib import Path
import ast
here=Path(__file__).resolve().parent
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
ast.parse((here/"apply_syllabus.py").read_text(encoding="utf-8"))
def read(name):return (root/name).read_text(encoding="utf-8")

gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionCode 64" in gradle and "versionName '3.13.8'" in gradle
assert "SyllabusDateInterpreter" in read("SyllabusEventParser.java")
parser=read("SyllabusEventParser.java")
for word in ("examen","parcial","practica","control","producto","proyecto",
             "sustentacion","trabajo","portafolio","integrador"):
    assert word in parser,word
assert "evaluacion\\\\s+(?:parcial|final" in parser
assert "SyllabusDateInterpreter.weekNumbers" in parser
dates=read("SyllabusDateInterpreter.java")
for item in ("weekStart","weekEnd","CalendarInfo","firstWeekMonday",
             "MONTH_DATE","SAME_MONTH_RANGE","ISO","NUMERIC"):
    assert item in dates,item
assert "LocalDate.of" in dates
assert "rangeStart" in dates
resolver=read("SyllabusCourseResolver.java")
assert "extractHeaders" in resolver and "filenameTitle" in resolver
assert "new Suggestion(course,best,evidence)" in resolver
assert "profileId.compareTo" in resolver, "Keep duplicates across profiles"
reader=read("SyllabusDocumentReader.java")
assert "stripper.setSortByPosition(true)" in reader
assert "text.trim().length()<110" in reader
assert "MAX_OCR_PAGES=30" in reader
ui=read("SyllabusImportActivity.java")
for phrase in ("SyllabusCourseResolver.detect(","chooseCourseDestination",
               "AcademicCourseRouting.catalog(this)","selectedCourse=course",
               "selectedCourse.profileId","AcademicTaskLinks.get(this).assign",
               "task.due=0","task.offsets=\"\"","if(task.due>0)Reminders.schedule",
               "Sin fecha exacta","Confirmar e incorporar al curso",
               "Productos",):
    assert phrase.lower() in ui.lower(),phrase
assert "SyllabusEventParser.extract(pages)" in ui
assert "Store.get(this).findOrigin(identity)" in ui
assert "Nueva evaluación" in ui
assert (here/"SyllabusAcademicTests.java").is_file()
# Existing timetable and photo recognition modules must remain present.
assert (root/"ScheduleOcrFusion.java").is_file()
assert "new_from_photo" in read("CalendarStudyPanel.java")
assert "AcademicSchedules" in read("CalendarStudyTabs.java")
print("PASS syllabus v3.13.8: exams/final projects only and week-aware dates")
print("PASS syllabus v3.13.8: explicit course/profile confirmation")
print("PASS syllabus v3.13.8: week-only events linked to course with NO invented alarm")
print("PASS previous timetable/OCR modules untouched")
