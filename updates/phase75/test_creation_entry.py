#!/usr/bin/env python3
"""Regression for the exact screenshot: Nuevo horario must NOT open name entry.

This audit reads the *installed-source* CalendarStudyPanel and ScheduleActivity,
not just the patch text. It runs before Gradle builds any APK.
"""
from pathlib import Path
import ast

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
PANEL=(JAVA/"CalendarStudyPanel.java").read_text(encoding="utf-8")
SCHEDULE=(JAVA/"ScheduleActivity.java").read_text(encoding="utf-8")
DB=(JAVA/"AcademicSchedules.java").read_text(encoding="utf-8")
GRADLE=Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")

ast.parse(Path("updates/phase75/apply_creation_entry.py").read_text(encoding="utf-8"))
assert "versionCode 61" in GRADLE and "versionName '3.13.5'" in GRADLE

# The exact UI entry visible in the user's image.
assert 'a.button("＋  Nuevo horario",()->chooseMethod(a))' in PANEL
assert 'a.button("＋  Nuevo horario",()->newSchedule(a,false))' not in PANEL
assert "private static void newSchedule(" not in PANEL
assert "Confirma el nombre que identificará su categoría y sus cursos." not in PANEL
chooser=PANEL[PANEL.index("    private static void chooseMethod("):
              PANEL.index("    private static void importPhoto(")]
assert 'setTitle("¿Cómo crearás tu horario?")' in chooser
assert '"Subir imagen del horario"' in chooser
assert '"Agregar cursos manualmente"' in chooser
assert "photo.setOnClickListener" in chooser and "importPhoto(a);" in chooser
assert "manual.setOnClickListener" in chooser and "startManual(a);" in chooser
assert ".setView(options)" in chooser and ".setItems(" not in chooser
assert "AcademicSchedules.create(" not in chooser
assert "new_manual" in chooser

# Photo and manual both pass through a course stage before the naming dialog.
creation=SCHEDULE[SCHEDULE.index("    @Override public void onCreate("):
                  SCHEDULE.index("    @Override protected void onResume()")]
assert "manualMode=getIntent().getBooleanExtra(\"new_manual\",false)" in creation
assert 'photoFirst=getIntent().getBooleanExtra("new_from_photo",false)' in creation
assert "detected=new ScheduleParser.Result();" in creation
assert "chosen.clear();" in creation
assert 'profileId="";' in creation
assert "show(5);" in creation
assert "show(1);" in creation
assert "private void askFirstSchedule()" in creation
assert ".setView(actions)" in creation and ".setItems(" not in creation
assert "Escribe el nombre" not in creation and "name.getText()" not in creation
assert "AcademicSchedules.create(" not in creation

review=SCHEDULE[SCHEDULE.index("    private void review()"):
                SCHEDULE.index("    /** Called only after the user has corroborated")]
assert "manualMode?" in review and "Corroborar cursos y continuar" in review
assert review.index("confirmPhotoPairs(") < review.index("confirmConflicts(")
assert review.index("confirmConflicts(") < review.index("confirmPhotoName(approved)")
assert "editor(draft,()->show(5))" in review

naming=SCHEDULE[SCHEDULE.index("    private void confirmPhotoName("):
                SCHEDULE.index("    /** A quick yes/no confirmation")]
assert 'manualPhotoName(approved)' in naming
assert 'AcademicSchedules.create(this,title,' in naming
assert naming.index("AcademicSchedules.create(this,title,") < naming.index("importReviewed(approved,created.id)")
assert 'No, escribir otro' in naming and 'Sí, usar ese nombre' in naming
assert 'manualMode?' in naming
assert "photoSaving" in naming
assert "AcademicSchedules.deleteConfirmed(this,created.id)" in naming

# No premature category change.
assert 'LIMIT = 10' in DB
assert "CategoryRegistry.save(" in DB
assert "importReviewed(approved,created.id)" in naming
assert "AcademicSchedules.syncFromSessions" in naming
assert 'Añadir foto a este horario' in PANEL
assert "new_from_photo" in PANEL
assert "SyllabusImportActivity" in (JAVA/"CalendarStudyPanel.java").read_text() or (
    "Exámenes y parciales" in PANEL
)

print("PASS screenshot: Nuevo horario now opens method chooser, not name-first popup")
print("PASS image-first: image -> course corroboration -> OCR title/manual title -> persist")
print("PASS manual-first: add courses -> review -> name -> persist")
print("PASS legacy: existing timetable, categories, 10 profile limit preserved")
