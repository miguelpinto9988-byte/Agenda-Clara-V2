#!/usr/bin/env python3
"""Regression assertions for notification permission and UI integration."""
from pathlib import Path
base=Path("AgendaClara/app/src/main")
j=base/"java/pe/agendaclara/app"
listener=(j/"WhatsAppListener.java").read_text(encoding="utf-8")
main=(j/"MainActivity.java").read_text(encoding="utf-8")
schedule=(j/"ScheduleActivity.java").read_text(encoding="utf-8")
assert 'getBoolean("discover",false)||Prefs.get(this).getBoolean("capture",false)' in listener
assert 'onListenerDisconnected()' in listener
assert 'wa_diag_last_whatsapp' in listener
assert 'wa_diag_last_received' in listener
assert 'wa_diag_proposal_count' in listener
assert 'ReviewFlow.receive(this,key,body,sent)' in listener
assert 'if(chat==null||!chat.selected)' in listener
assert 'if(!received)' in listener
assert 'new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)' in main
assert 'diagnostic.addView(text("Diagnóstico de recepción · WhatsApp"' in main
assert 'requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},32)' not in main[main.index("void connectWhatsapp()"):main.index("void session(")]
assert '0xff3957d7' in main and '0xff3957d7' in schedule
assert (j/"ComposeDayActivity.kt").exists()
print("PASS: WhatsApp read-access path, listener diagnostics, chat consent and shared palette")
