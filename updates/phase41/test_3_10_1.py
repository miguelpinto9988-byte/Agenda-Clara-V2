#!/usr/bin/env python3
"""Verify one-JID history gates and fast-dialog resource integration."""
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path('AgendaClara')
java=(root/'app/src/main/java/pe/agendaclara/app/WhatsAppSessionService.java').read_text()
go=(root/'whatsapp-native/main.go').read_text()
assert 'for(Store.Chat chat:db.chats())if(chat.selected&&!chat.jid.isEmpty())WhatsAppNative.call(request("history")' not in java
assert 'go t.history("")' not in go
assert 'requestedHistoryJid=jid;' in java
assert 'requestedHistoryJid="";' in java
assert 'e.optBoolean("historical")&&!e.optString("jid").equals(requestedHistoryJid)' in java
assert java.count('!jid.isEmpty()&&jid.equals(requestedHistoryJid)')==2
assert 'db.getChat(Store.linkedKey(jid))' in java
assert 'requestHistory(action,value,count)' in java
assert 'historyTarget string' in go
assert 't.historyTarget = r.JID' in go
assert 't.processHistory(e.Data, requested, map[string]bool{requested:' in go
assert 'go t.history(r.JID)' in go
assert 'if !r.Enabled || !next[t.historyTarget]' in go
assert 'TestHistoricalExtractionDoesNotIncludeAnotherAuthorizedGroup' in (root/'whatsapp-native/main_test.go').read_text()
for name in ['agenda_dialog_fast_in.xml','agenda_dialog_fast_out.xml']:
    ET.parse(root/'app/src/main/res/anim'/name)
assert '@anim/agenda_dialog_fast_in' in (root/'app/src/main/res/values/styles.xml').read_text()
assert 'setDuration(105)' in (root/'app/src/main/java/pe/agendaclara/app/UiMotion.java').read_text()
assert 'setDuration(110)' in (root/'app/src/main/java/pe/agendaclara/app/CreationChoices.java').read_text()
main=(root/'app/src/main/java/pe/agendaclara/app/MainActivity.java').read_text()
nav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav
assert 'versionCode 42' in (root/'app/build.gradle').read_text()
assert "versionName '3.10.1'" in (root/'app/build.gradle').read_text()
print('PASS phase41: single-group history in Java and native, no background history scan, faster animations, original nav')
