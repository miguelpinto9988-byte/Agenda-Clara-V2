#!/usr/bin/env python3
"""Source-only guards. No Gradle or Android APK commands are invoked."""
from pathlib import Path
import ast
here=Path(__file__).resolve().parent
for name in ("patch_task_routing.py","apply_plan_b.py"):
    ast.parse((here/name).read_text(encoding="utf-8"),filename=name)
expected=[
    "AcademicCourseMatcher.java","AcademicTaskLinks.java","AcademicCourseRouting.java",
    "SyllabusEventParser.java","SyllabusDocumentReader.java",
    "SyllabusImportActivity.java","PhaseBParserTests.java"
]
for file in expected:
    source=(here/file).read_text(encoding="utf-8")
    assert "package pe.agendaclara.app;" in source,file
    assert len(source)>250,file
routing=(here/"AcademicCourseRouting.java").read_text()
assert "Confirmar curso" in routing and "Guardar sin curso" in routing
assert "setSingleChoiceItems" in routing
matcher=(here/"AcademicCourseMatcher.java").read_text()
assert "matches(String text" in matcher and "score>0" in matcher
task_patch=(here/"patch_task_routing.py").read_text()
assert "AcademicCourseRouting.review(this,t.title" in task_patch
assert "AcademicCourseRouting.review(activity,spoken" in task_patch
assert "AcademicTaskLinks.get(this).assign" in task_patch
reader=(here/"SyllabusDocumentReader.java").read_text()
assert "pdfbox" in reader and "hwpf" in reader and "ZipInputStream" in reader
assert "TextRecognition.getClient" in reader and "MAX_INPUT" in reader
ui=(here/"SyllabusImportActivity.java").read_text()
for token in ("ACTION_OPEN_DOCUMENT","DocumentReader","SyllabusEventParser",
              "AcademicCourseRouting.review","15" if False else "15120",
              "10080","Guardar" if False else "Store.get(this).save(task)",
              "AcademicTaskLinks.get(this).assign","Reminders.schedule(this,task)"):
    assert token in ui,token
assert '"manual"' in ui and "Fecha" in ui
apply=(here/"apply_plan_b.py").read_text()
assert "SyllabusImportActivity" in apply and "AndroidManifest.xml" in apply
assert "poi-scratchpad:5.4.1" in apply and "pdfbox-android:2.0.27.0" in apply
assert "Gradle" in apply and "NO APK" in apply
print("PASS Entrega B: código fuente completo, rutas de confirmación y privacidad local")
print("NO APK: QA estático; no se compila la aplicación Android")
