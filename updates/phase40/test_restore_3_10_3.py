#!/usr/bin/env python3
"""Do not reintroduce faulty WhatsApp gates during animation-only restore."""
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path("AgendaClara"); S=R/"app/src/main/java/pe/agendaclara/app"
java=(S/"WhatsAppSessionService.java").read_text()
go=(R/"whatsapp-native/main.go").read_text()
main=(S/"MainActivity.java").read_text()
assert 'go t.history("")' in go
assert 'case "history":' in go and 'go t.history(r.JID)' in go
assert 'case "more":' in go and 't.more(r.JID, r.Count)' in go
assert 'case *events.HistorySync:' in go
assert 'requestedHistoryJid' not in java and 'historyTarget' not in go
assert '"history".equals(action)' in java and '"more".equals(action)' in java
assert 'for(Store.Chat chat:db.chats())if(chat.selected&&!chat.jid.isEmpty())WhatsAppNative.call(request("history").put("jid",chat.jid))' in java
assert 'if(chat.selected&&!chat.jid.isEmpty()&&chat.joined)' in java
assert 'session("history",chat.jid)' in main and 'wa_history_count' in main
for file in ["agenda_restore_dialog_in.xml","agenda_restore_dialog_out.xml"]:
    x=ET.parse(R/"app/src/main/res/anim"/file).getroot()
    assert x.get("{http://schemas.android.com/apk/res/android}duration")=="300"
theme=(R/"app/src/main/res/values/styles.xml").read_text()
assert "@anim/agenda_restore_dialog_in" in theme and "@anim/agenda_restore_dialog_out" in theme
assert ".setDuration(300)" in (S/"UiMotion.java").read_text()
assert ".setDuration(300)" in (S/"CreationChoices.java").read_text()
nav=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
grad=(R/"app/build.gradle").read_text()
assert 'versionCode 44' in grad and "versionName '3.10.3'" in grad
print("PASS restore 3.10.3: general and group-specific history present; native unchanged; 300ms animations; nav untouched")
