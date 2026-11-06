#!/usr/bin/env bash
set -euo pipefail
DIR=AgendaClara/app/src/main/java/pe/agendaclara/app
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
javac -encoding UTF-8 -d "$OUT" \
  "$DIR/SyllabusEventParser.java" \
  "$DIR/SyllabusDateInterpreter.java" \
  "$DIR/SyllabusReviewIntelligence.java" \
  "$DIR/SyllabusTableInterpreter.java" \
  "$DIR/SyllabusRevisionComparator.java" \
  "$DIR/SyllabusImportPipeline.java" \
  "$DIR/SyllabusContextualPartials.java" \
  updates/phase79/Phase79ReviewTests.java \
  updates/phase80/Phase80Tests.java \
  updates/phase85/Phase85ContextTests.java
java -cp "$OUT" pe.agendaclara.app.Phase79ReviewTests
java -cp "$OUT" pe.agendaclara.app.Phase80Tests
java -cp "$OUT" pe.agendaclara.app.Phase85ContextTests
echo "PASS: syllabus reader preserves older review/table functionality and contextualizes numbered partials"
