#!/usr/bin/env python3
"""Sanity-check patch integration with the native schedule activity."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
activity=(p/"ScheduleActivity.java").read_text(encoding="utf8")
ocr=(p/"ScheduleOcr.java").read_text(encoding="utf8")
core=(p/"SchedulePhotoReview.java").read_text(encoding="utf8")
db=(p/"ScheduleDatabase.java").read_text(encoding="utf8")
build=Path("AgendaClara/app/build.gradle").read_text(encoding="utf8")
assert "ETAPA 1 · Vista general" in activity
assert "ETAPA 2 · Cursos" in activity
assert "ETAPA 3 · Corroboración" in activity
assert "confirmPhotoPairs(approved,new HashSet<Integer>()" in activity
assert 'setPositiveButton("Sí · mismo curso"' in activity
assert 'setNegativeButton("No · cursos distintos"' in activity
assert "chosen.set(index,true)" not in activity
assert "ScheduleCourseColors.confidentMatch(previous.course,other.course)" not in activity
assert "selected[current.day-1]=true;" in activity
assert "corroboration(table,glance)" in ocr and "corroboration(virtual,glance)" in ocr
assert "SchedulePhotoReview.uniqueBlocks" in ocr
assert "public static void accept(" in core and "public static void reject(" in core
assert "ScheduleCourseColors.same(old.course,s.course)" in db
assert "versionCode 29" in build and "versionName '3.8.1'" in build
print("PASS: 3.8.1 3-stage OCR, explicit user consent, daily edit isolation, no bulk mutation, version")
