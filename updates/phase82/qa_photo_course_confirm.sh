#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
JAVA="$ROOT/AgendaClara/app/src/main/java/pe/agendaclara/app"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
javac -encoding UTF-8 -d "$OUT" \
  "$JAVA/ScheduleEntry.java" "$JAVA/ScheduleCourseColors.java" \
  "$JAVA/ScheduleParser.java" "$JAVA/ScheduleGridInterpreter.java" \
  "$JAVA/ScheduleCourseWordReview.java" "$JAVA/ScheduleCourseRecognition.java" \
  "$JAVA/SchedulePhotoReview.java" "$JAVA/ScheduleOcrFusion.java" \
  "updates/phase82/Phase82CourseConfirmationTests.java"
java -cp "$OUT" pe.agendaclara.app.Phase82CourseConfirmationTests
python3 - <<'PY'
from pathlib import Path
root=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
a=(root/'ScheduleActivity.java').read_text()
assert 'confirmExistingCourseMatches(approved,' in a
assert 'SchedulePhotoReview.rememberDecision' in a
assert 'ScheduleCourseRecognition.Relation.SHARED_WORD' in a
assert 'SchedulePhotoReview.nextPair(approved,java.util.Collections.emptySet(),rejected)' in a
assert 'PhotoWidget' not in ' '.join(p.name for p in Path('updates/phase82').glob('*.java'))
print('PASS: los nombres similares no se guardan sin consentimiento')
print('PASS: el widget Fotografía no se toca')
PY
