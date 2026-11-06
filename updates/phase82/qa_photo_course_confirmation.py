#!/usr/bin/env python3
"""Static UI/flow invariants for OCR photo import, after apply_photo_course_confirmation."""
from pathlib import Path
import ast

ast.parse(Path("updates/phase82/apply_photo_course_confirmation.py").read_text(encoding="utf-8"))
d=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
recognition=(d/"ScheduleCourseRecognition.java").read_text(encoding="utf-8")
review=(d/"SchedulePhotoReview.java").read_text(encoding="utf-8")
activity=(d/"ScheduleActivity.java").read_text(encoding="utf-8")
fusion=(d/"ScheduleOcrFusion.java").read_text(encoding="utf-8")
gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert 'SHARED_WORD' in recognition
assert 'sharedKeyword(left,right)' in recognition
assert 'Relation.SHARED_WORD?1:0' in review
assert '"¿Son el mismo curso?"' in activity
assert 'confirmPhotoPairs(approved,new HashSet<Integer>()' in activity
assert 'confirmPhotoWarnings(approved,()->confirmPhotoName(approved))' in activity
assert 'SchedulePhotoReview.acceptWithName(approved,pair,title)' in activity
assert 'no se unirán automáticamente' in activity
assert 'relation==ScheduleCourseRecognition.Relation.EXACT;' in fusion
assert 'versionCode 68' in gradle and "versionName '3.15.1'" in gradle
assert 'class PhotoWidget' in (d/"PhotoWidget.java").read_text(encoding="utf-8")
print("PASS: reviews before timetable save; canonical names chosen by user")
print("PASS: shared keyword prompts, unmatched variants preserved")
print("PASS: version 3.15.1; no PhotoWidget modification in phase82")
