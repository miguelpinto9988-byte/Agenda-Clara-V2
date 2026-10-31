#!/usr/bin/env python3
from pathlib import Path
R=Path("AgendaClara"); J=R/"app/src/main/java/pe/agendaclara/app"
a=(J/"WhatsAppSessionService.java").read_text()
assert "chat.selected&&!chat.jid.isEmpty()&&!chat.community" in a
assert "if(chat==null||!chat.selected||chat.community" in a
assert "Otra revisión sigue activa" in a
assert "},240,TimeUnit.SECONDS);" in a
assert "if(!jid.equals(requestedHistoryJid))return;" in a
assert 'e.optBoolean("historical")&&!e.optString("jid").equals(requestedHistoryJid)' in a
assert 'requestedHistoryJid="";' in a
go=(R/"whatsapp-native/main.go").read_text()
assert '"already_processed":true' in go
assert 't.processHistory(e.Data, requested, map[string]bool{requested:true})' in go
assert 'go t.history(r.JID)' in go
assert 'if r.JID == "" || !t.allowed(r.JID)' in go
assert "go t.history(\"\")" not in go
m=(J/"UiMotion.java").read_text()
p=(J/"CreationChoices.java").read_text()
assert ".setDuration(190)" in m and ".withLayer().start();" in m
assert ".setDuration(190)" in p and ".withLayer().start();" in p
w=(J/"WindowLayout.java").read_text()
assert "decor.requestLayout();" not in w[w.index("final Runnable fit"):w.index("listener[0]=fit::run")]
for name,d in (("agenda_dialog_fast_in.xml",200),("agenda_dialog_fast_out.xml",160)):
    assert f'android:duration="{d}"' in (R/"app/src/main/res/anim"/name).read_text()
main=(J/"MainActivity.java").read_text()
nav=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
assert "new UiDesign.OutlineIcon(" in nav and "dp(26),dp(26)" in nav
assert "versionCode 43" in (R/"app/build.gradle").read_text()
assert "versionName '3.10.2'" in (R/"app/build.gradle").read_text()
print("PASS phase42: selected group validation, request duration, scope, compositor-based UI transitions")
