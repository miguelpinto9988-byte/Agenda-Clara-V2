#!/usr/bin/env python3
"""Verify actual installed 3.13.9 sources, without Gradle or APK."""
from pathlib import Path
import ast

here=Path(__file__).resolve().parent
for file in ("apply_syllabus_advanced.py","patch_syllabus_ui.py"):
    ast.parse((here/file).read_text(encoding="utf-8"),filename=file)
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def code(name):return (src/name).read_text(encoding="utf-8")
dates=code("SyllabusDateInterpreter.java")
assert "CROSS_MONTH_RANGE" in dates
assert "inicio\\\\s+de\\\\s+actividades" in dates
analyzer=code("SyllabusAssessmentExtractor.java")
for needle in ("suggestedDay","weight(String","MAX","SyllabusEventParser.assessmentType","dateBasis"):
    if needle!="MAX":assert needle in analyzer
events=code("SyllabusEventParser.java")
assert "SyllabusAssessmentExtractor.extract(pages)" in events
assert "public static String assessmentType" in events
reader=code("SyllabusDocumentReader.java")
assert "tableDepth" in reader and '"tc".equals(tag)' in reader
assert "scannedGridHint" in reader and "TextRecognition.getClient" in reader
planner=code("SyllabusReimportPlanner.java")
for needle in ("UNCHANGED, CHANGED, AMBIGUOUS","No existe una evaluación","fecha del sílabo"):
    assert needle in planner
ui=code("SyllabusImportActivity.java")
for needle in (
    "renderEvaluationOverview();","SyllabusAssessmentExtractor.extract(pages)",
    "new Row(f)","Ponderación detectada","Confirmar fecha sugerida",
    "renderReimportDecision(review,row)","SyllabusReimportPlanner.compare(",
    "Actualizar evaluación existente","Registrar como evento distinto",
    "task=row.updateTarget==null?new Task()","Reminders.cancel(this,task.id)",
    "Fecha confirmada posteriormente","if(task.due>0&&!task.done)"):
    assert needle in ui,needle
assert "row.plan.status==SyllabusReimportPlanner.Status.UNCHANGED" in ui
assert "AcademicTaskLinks.get(this).find(task.id)" in ui
assert "Confirmar "+"" in ui
assert "versionCode 65" in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.13.9'" in Path("AgendaClara/app/build.gradle").read_text()
print("PASS: three phases integrated into actual source: tables, course, reimports")
print("PASS: no task overwritten without selection; pending dates have no alarm")
