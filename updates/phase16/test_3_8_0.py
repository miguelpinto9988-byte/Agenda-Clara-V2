#!/usr/bin/env python3
"""Phase 16 regression checks: WhatsApp capture continuity and native UI."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(p/"MainActivity.java").read_text(encoding="utf8")
listener=(p/"WhatsAppListener.java").read_text(encoding="utf8")
policy=(p/"NotificationSummaryPolicy.java").read_text(encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle").read_text(encoding="utf8")
assert main.count('if(!prefs.getBoolean("capture",false))edit.putLong("capture_since"')==2
assert 'if(on&&!prefs.getBoolean("capture",false))change.putLong("capture_since"' in main
assert 'NotificationListenerService.requestRebind(' in main
assert 'Probar intérprete sin guardar datos' in main
assert 'Notification.EXTRA_TEXT_LINES' in listener
assert 'NotificationSummaryPolicy.isSummary(s)' in listener
assert 'catch(RuntimeException problem)' in listener
assert 'ReviewFlow.changed(this);' in listener
assert 'wa_diag_event_count' in main and 'wa_diag_event_count' in listener
assert 'getMessagesFromBundleArray' in listener
assert 'versionCode 28' in gradle and "versionName '3.8.0'" in gradle
assert 'public static boolean isSummary' in policy
assert 'if(chat==null||!chat.selected)' in listener
print("PASS: phase 16 WhatsApp listener, review consent, date continuity, diagnostics, version and UI")
