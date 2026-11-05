#!/usr/bin/env python3
"""Source-level photo-first flow audit; never invokes Gradle or APK packaging."""
from pathlib import Path
import ast

base=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
patch=Path("updates/phase74/apply_photo_first.py")
ast.parse(patch.read_text(encoding="utf-8"))
schedule=(base/"ScheduleActivity.java").read_text(encoding="utf-8")
panel=(base/"CalendarStudyPanel.java").read_text(encoding="utf-8")
parser=(base/"ScheduleTitleParser.java").read_text(encoding="utf-8")
gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")

assert "versionCode 60" in gradle and "versionName '3.13.4'" in gradle
assert 'intent.putExtra("new_from_photo",true);' in panel
entry=panel[panel.index("    private static void importPhoto"):panel.index("    private static void details")]
assert "newSchedule(a,true)" not in entry, "Photo path must not request name first"
assert "AcademicSchedules.create" not in entry, "Photo path must not precreate category"
assert "Límite de diez horarios" in entry
assert '"Añadir foto a este horario"' in panel
assert 'photoFirst=getIntent().getBooleanExtra("new_from_photo",false)' in schedule
assert 'profileId="";\n            show(1);' in schedule
review=schedule[schedule.index("    private void review()"):schedule.index("    /** Called only after the user has corroborated")]
assert review.index("confirmPhotoPairs") < review.index("confirmConflicts") < review.index("confirmPhotoName(approved)")
assert "Paso 2 de 3 · Corroborar cursos" in schedule
assert "Paso 3 de 3 · Nombre del horario" in schedule
assert "No, escribir otro" in schedule and "Sí, usar ese nombre" in schedule
assert '"Escribe el nombre del horario"' in schedule
assert 'AcademicSchedules.create(this,title,' in schedule
assert schedule.index("AcademicSchedules.create(this,title,") < schedule.index("importReviewed(approved,created.id)")
assert "AcademicSchedules.deleteConfirmed(this,created.id)" in schedule, "Failed profile should rollback"
assert "Guardar en "+'"+target.name' in schedule, "Appending must preserve existing timetable"
assert "draft=new ScheduleEntry()" in schedule and "editor(draft,()->show(5))" in schedule
assert 'ScheduleReminders.rebuild(this)' in schedule
assert "private static final Pattern WEEK" in parser and 'return "Semana "+week.group(1)' in parser

# Source-only safeguards around inherited core academic data:
assert "ScheduleDatabase.get(this).all(profileId)" in schedule
assert "SchedulePhotoReview.uniqueBlocks" in schedule
assert "AcademicSchedules.syncFromSessions" in schedule
assert "AcademicSchedules.activeId" in (base/"CalendarStudyTabs.java").read_text() or (
    "AcademicSchedules.migrateLegacy" in (base/"CalendarStudyTabs.java").read_text()
)
print("PASS: image-first, course review, title confirmation, manual fallback, no premature category")
print("PASS: limit ten, existing timetable import, OCR week names, no APK build")
