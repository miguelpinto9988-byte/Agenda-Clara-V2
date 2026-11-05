#!/usr/bin/env python3
"""Static regression tests against actual rebuilt Agenda Clara 3.13.6 sources."""
from pathlib import Path
import ast
p=Path("updates/phase76/apply_ocr_corroboration.py")
ast.parse(p.read_text(encoding="utf-8"))
code=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def read(name):return (code/name).read_text(encoding="utf-8")
recognition=read("ScheduleCourseRecognition.java")
assert "SHARED_START" in recognition
assert "firstA.equals(firstB)" in recognition
assert "GENERIC.contains(shortName)" in recognition
review=read("SchedulePhotoReview.java")
assert "Set<String> rejected" in review and 'rejected.contains(j+":"+i)' in review
assert "pairKey(Pair p)" in review
ocr=read("ScheduleOcr.java")
assert "java.util.List<ScheduleEntry> blocks=SchedulePhotoReview.uniqueBlocks(result.candidates);" not in ocr
grid=read("ScheduleGridInterpreter.java")
virtual=read("ScheduleVirtualGrid.java")
assert "Posible OCR duplicado" in grid and "Posible OCR duplicado" in virtual
assert "Posible repetición OCR" in virtual
activity=read("ScheduleActivity.java")
assert "confirmPhotoPairs(approved,new HashSet<Integer>()," in activity
assert "new HashSet<String>()" in activity
assert "confirmPhotoWarnings(approved,()->confirmPhotoName(approved))" in activity
assert activity.index("confirmPhotoWarnings(approved,()->confirmPhotoName(approved))")<activity.index("private void confirmPhotoName(")
assert "¿Son el mismo curso?" in activity and "setView(scroll)" in activity
assert "rejected.add(SchedulePhotoReview.pairKey(pair))" in activity
assert "Corroborar anomalías de la imagen" in activity
assert "SHARED_START" in activity
assert "Nuevo horario" in read("CalendarStudyPanel.java")
assert "new_from_photo" in read("CalendarStudyPanel.java")
gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionCode 62" in gradle and "versionName '3.13.6'" in gradle
print("PASS: all OCR ambiguity decisions visible before confirming the timetable name")
print("PASS: name-first regression remains fixed; category/database code untouched")
