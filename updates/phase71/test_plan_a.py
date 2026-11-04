#!/usr/bin/env python3
"""Static regression tests for Agenda Clara 3.13.3 / Entrega A."""
from pathlib import Path
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(root/"MainActivity.java").read_text()
assert "else if(page==1)CalendarStudyTabs.render(this);" in main
assert "void calendarPage()" in main
tabs=(root/"CalendarStudyTabs.java").read_text()
assert "a.calendarPage();" in tabs
assert "CalendarStudyPanel.render(a);" in tabs
assert "AcademicSchedules.importLegacy(a,names);" in tabs
assert 'a.getSharedPreferences(PREF,Context.MODE_PRIVATE)' in tabs
store=(root/"AcademicSchedules.java").read_text()
assert "LIMIT = 10" in store
assert "UUID.randomUUID()" in store
assert "ScheduleDatabase" in tabs
assert "profiles.size()>=LIMIT" in store
assert "uniqueCourses" in store and "importLegacy" in store
panel=(root/"CalendarStudyPanel.java").read_text()
for token in ("Nuevo horario","Confirmar nombre del horario","Agregar curso",
              "Editar nombre del horario","Exámenes y parciales"):
    assert token in panel,token
assert "ScheduleActivity.class" in panel
assert "versionCode 59" in Path("AgendaClara/app/build.gradle").read_text()
print("PASS: entrega A panel dual, límite 10, persistencia, migración y navegación al horario existente")
