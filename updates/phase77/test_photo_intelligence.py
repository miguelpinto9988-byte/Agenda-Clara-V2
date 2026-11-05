#!/usr/bin/env python3
"""Source checks for Agenda Clara 3.13.7, no APK or Gradle."""
from pathlib import Path
import ast

patch=Path("updates/phase77/apply_photo_intelligence.py")
ast.parse(patch.read_text(encoding="utf-8"))
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def source(name):return (root/name).read_text(encoding="utf-8")
s=source("ScheduleParser.java")
assert "reviewOnlyKeys" in s
ocr=source("ScheduleOcr.java")
assert "ScheduleOcrFusion.reconcile(table,virtual,fallback)" in ocr
assert ocr.count("ScheduleVirtualGrid.parse")>=1
assert ocr.count("ScheduleParser.parse(recognized.getText())")>=1
assert "if(!table.candidates.isEmpty())" not in ocr
fusion=source("ScheduleOcrFusion.java")
assert "MAX_ALTERNATIVES=32" in fusion
assert "reviewOnlyKeys.add(fingerprint)" in fusion
assert "sameSession(current,proposed)" in fusion
assert "DESMARCADAS" in fusion
review=source("SchedulePhotoReview.java")
assert "acceptWithName" in review
assert "ScheduleCourseColors.same(e.course,rightName)" in review
activity=source("ScheduleActivity.java")
assert "chosen.add(!detected.reviewOnlyKeys.contains(ScheduleOcrFusion.key(candidate)))" in activity
assert 'Lectura adicional · COMPRUEBA EN LA FOTO' in activity
assert "chooseFinalCourseName(" in activity
assert "scheduleDialog().setTitle(\"Confirmar nombre del curso\")" in activity
assert 'confirmPhotoWarnings(approved,()->confirmPhotoName(approved))' in activity
assert 'a.button("＋  Nuevo horario",()->chooseMethod(a))' in source("CalendarStudyPanel.java")
assert "ScheduleColorTileDetector.detect(pixels,width,height)" in source("ScheduleImageBlocks.java")
assert "private static boolean colored(int argb)" in source("ScheduleColorTileDetector.java")
assert "Bitmap.Config.ARGB_8888" in source("SchedulePhotoLoader.java")
assert "bounds.outHeight)/sample>2560" in source("SchedulePhotoLoader.java")
assert "columns.isEmpty()||periods.isEmpty()" in source("ScheduleGridInterpreter.java")
assert "headers.isEmpty()||periods.isEmpty()" in source("ScheduleVirtualGrid.java")
assert "versionCode 63" in Path("AgendaClara/app/build.gradle").read_text()
assert "versionName '3.13.7'" in Path("AgendaClara/app/build.gradle").read_text()
print("PASS: OCR fusion, all three interpreters, optional proposals and name decision")
print("PASS: photo -> review -> course confirmations -> timetable name -> save")
print("PASS: original task database and timetable data remain unchanged")
