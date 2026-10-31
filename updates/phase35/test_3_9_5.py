#!/usr/bin/env python3
"""Static regression guards for the privacy-first WhatsApp understanding prototype."""
from pathlib import Path
P=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
m=(P/'MessageParser.java').read_text(encoding='utf-8')
c=(P/'ConversationAnalyzer.java').read_text(encoding='utf-8')
e=(P/'WhatsAppUnderstandingEngine.java').read_text(encoding='utf-8')
review=(P/'ReviewFlow.java').read_text(encoding='utf-8')
assert 'WhatsAppUnderstandingEngine.split(bounded)' in m
assert 'validCount>1' in m
assert 'WhatsAppUnderstandingEngine.merge(out)' in c
assert 'WhatsAppUnderstandingEngine.applyCorrections(grouped,ordered,zone)' in c
assert 'private static final long DUPLICATE_WINDOW=48L' in c
assert 'explicitlyContinues' in c
assert 'return result;' in e and 'public static boolean related(' in e
assert 'sameDate' in e and 'Posible corrección contextual' in e
assert 'No accidental correlation' not in e or 'sender' in e
assert 'offerProposal' in review and 'offerLinked' in review
assert 'db.offerProposal(' in review
assert 'new Task(' not in e
assert 'HttpURLConnection' not in e and 'Socket' not in e
assert 'versionCode 36' in Path('AgendaClara/app/build.gradle').read_text()
assert "versionName '3.9.5'" in Path('AgendaClara/app/build.gradle').read_text()
print('PASS phase35 static: review-only, offline, multi-activity, dedup, dates and version')
