#!/usr/bin/env python3
"""Static guards; behavioral cases run separately using javac/java."""
from pathlib import Path
root=Path("AgendaClara")
java=root/"app/src/main/java/pe/agendaclara/app"
parser=(java/"QuickTaskVoiceParser.java").read_text(encoding="utf-8")
ui=(java/"VoiceQuickTask.java").read_text(encoding="utf-8")
gradle=(root/"app/build.gradle").read_text(encoding="utf-8")
assert "DEFAULT_DEADLINE=LocalTime.of(23,59)" in parser
assert "private static Result parseCommands" in parser
assert "private static String cleanedTitle" in parser
assert "private static final Pattern RELATIVE" in parser
assert "if(!out.hadDate){out.date=today;}" in parser
assert "if(!out.hadTime)out.time=DEFAULT_DEADLINE;" in parser
assert "final LocalDate recordingDate;" in ui
assert "QuickTaskVoiceParser.parse(spoken,recordingDate)" in ui
assert "Hora no mencionada: 11:59 p. m." in ui
assert "No se crea ni guarda ningún archivo de grabación" in ui
assert "versionCode 49" in gradle and "versionName '3.10.8'" in gradle
print("PASS structural guards: natural language, timeline, default deadline and privacy")
