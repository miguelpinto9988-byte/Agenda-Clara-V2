#!/usr/bin/env python3
"""Static checks for the newly patched verified Android project."""
from pathlib import Path
r=Path('AgendaClara')
src=r/'app/src/main/java/pe/agendaclara/app'
base=(src/'AcademicContextInterpreter.java').read_text(encoding='utf-8')
voice=(src/'VoiceQuickTask.java').read_text(encoding='utf-8')
parser=(src/'MessageParser.java').read_text(encoding='utf-8')
gradle=(r/'app/build.gradle').read_text(encoding='utf-8')
assert "versionCode 52" in gradle and "versionName '3.11.1'" in gradle
assert 'class AcademicContextInterpreter' in base
assert 'dateUncertain' in base and 'timeUncertain' in base and 'requiresReview()' in base
assert 'parse(String text,LocalDate today,Collection<String> registeredCourses)' in base
assert 'new Result()' in base and ',action;' in base
assert 'Curso reconocido (opcional)' in voice and 'Grado o sección (opcional)' in voice
assert 'AcademicContextInterpreter.Result academic' in parser
assert 'academic.requiresReview()' in parser and 'Fecha' in parser
assert 'task.notes=academicNotes.toString()' in voice
assert 'android.permission.INTERNET' not in base and 'HttpURLConnection' not in base
assert 'Store.get' not in base and 'Reminders.schedule' not in base
print('PASS: 3.11.1 academic parser is local, deterministic and review-only')
