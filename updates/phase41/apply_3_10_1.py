#!/usr/bin/env python3
"""3.10.1: bound historical WhatsApp requests to one selected chat, fast dialog transitions."""
from pathlib import Path
ROOT=Path('AgendaClara')
JAVA=ROOT/'app/src/main/java/pe/agendaclara/app'
GO=ROOT/'whatsapp-native/main.go'
GO_TESTS=ROOT/'whatsapp-native/main_test.go'
STYLE=ROOT/'app/src/main/res/values/styles.xml'
GRADLE=ROOT/'app/build.gradle'

def one(src,old,new,label):
    n=src.count(old)
    if n!=1:raise RuntimeError(f'phase41 {label}: expected one match, got {n}')
    return src.replace(old,new,1)

def apply():
    go=GO.read_text(encoding='utf-8'); gt=GO_TESTS.read_text(encoding='utf-8')
    java=(JAVA/'WhatsAppSessionService.java').read_text(encoding='utf-8')
    styles=STYLE.read_text(encoding='utf-8')
    motion=(JAVA/'UiMotion.java').read_text(encoding='utf-8')
    menu=(JAVA/'CreationChoices.java').read_text(encoding='utf-8')
    grad=GRADLE.read_text(encoding='utf-8')
    go=one(go, '\thistoryLock   sync.Mutex\n\tclient        *whatsmeow.Client',
       '\thistoryLock   sync.Mutex\n\thistoryTarget string // explicitly requested JID, never consent set\n\tclient        *whatsmeow.Client','transport target')
    go=one(go, '''\t\t\thasConsent := t.enabled && len(t.selected) > 0
\t\t\tt.mu.Unlock()
\t\t\tt.saveNotifications()
\t\t\tif hasConsent {
\t\t\t\tgo t.history("")
\t\t\t}
\t\t\treturn''', '''\t\t\tt.mu.Unlock()
\t\t\t// Store only encrypted metadata. Consent never starts an account-wide scan.
\t\t\tt.saveNotifications()
\t\t\treturn''','remove automatic history')
    go=one(go, '''\tcase *events.HistorySync:
\t\tif e.Data != nil {
\t\t\tt.processHistory(e.Data, "", nil)
\t\t}''', '''\tcase *events.HistorySync:
\t\t// A protocol response may contain several conversations. Only process the
\t\t// chat of the explicit user request; unsolicited sync data is ignored.
\t\tt.mu.Lock()
\t\trequested := t.historyTarget
\t\tt.mu.Unlock()
\t\tif e.Data != nil && requested != "" && t.allowed(requested) {
\t\t\tcount := t.processHistory(e.Data, requested, map[string]bool{requested:true})
\t\t\tt.emit(object{"type":"history_done","jid":requested,"messages":count,"failed_chunks":0,"has_pointers":false})
\t\t}''','on-demand native response scope')
    go=one(go,'\t\tt.selected = next\n\t\tt.enabled = r.Enabled', '''\t\tt.selected = next
\t\tt.enabled = r.Enabled
\t\tif !r.Enabled || !next[t.historyTarget] { t.historyTarget = "" }''','revocation clears target')
    go=one(go, '''\tcase "history":
\t\tif !t.allowed(r.JID) {
\t\t\treturn fail("Autoriza primero la lectura del grupo")
\t\t}
\t\tgo t.history(r.JID)
\tcase "more":
\t\tif err := t.more(r.JID, r.Count); err != nil {
\t\t\treturn fail(err.Error())
\t\t}''','''\tcase "history":
\t\tif r.JID == "" || !t.allowed(r.JID) { return fail("Selecciona un grupo autorizado") }
\t\tt.mu.Lock(); t.historyTarget = r.JID; t.mu.Unlock()
\t\tgo t.history(r.JID)
\tcase "more":
\t\tif r.JID == "" || !t.allowed(r.JID) { return fail("Selecciona un grupo autorizado") }
\t\tt.mu.Lock(); t.historyTarget = r.JID; t.mu.Unlock()
\t\tif err := t.more(r.JID, r.Count); err != nil {
\t\t\tt.mu.Lock(); if t.historyTarget == r.JID {t.historyTarget = ""}; t.mu.Unlock()
\t\t\treturn fail(err.Error())
\t\t}''','explicit request target')
    go=one(go,'\tcase "stop":\n\t\tt.mu.Lock()\n\t\tt.enabled = false',
       '\tcase "stop":\n\t\tt.mu.Lock()\n\t\tt.historyTarget = ""\n\t\tt.enabled = false','clear native scope on stop')
    java=one(java,'    private volatile boolean initialized=false,stopping=false;',
       '    private volatile boolean initialized=false,stopping=false;\n    private volatile String requestedHistoryJid="";', 'Java historical target')
    java=one(java,'        db.scanState(key,"history".equals(action)',
       '        requestedHistoryJid=jid;\n        db.scanState(key,"history".equals(action)', 'set target before request')
    java=one(java, '''            worker.schedule(()->{
                Store.Chat current=db.getChat(key);''',
       '''            worker.schedule(()->{
                if(jid.equals(requestedHistoryJid))requestedHistoryJid="";
                Store.Chat current=db.getChat(key);''','expire target on timeout')
    java=one(java,'        }catch(Exception failure){\n            db.scanState(key,"Error al recuperar mensajes.',
       '        }catch(Exception failure){\n            if(jid.equals(requestedHistoryJid))requestedHistoryJid="";\n            db.scanState(key,"Error al recuperar mensajes.','clear target on error')
    java=one(java, '''            Prefs.get(this).edit().putBoolean("wa_linked",true).putBoolean("wa_connected",true).remove("wa_pair_code").putString("wa_status","Conectado · cargando tus grupos").apply();consents();for(Store.Chat chat:db.chats())if(chat.selected&&!chat.jid.isEmpty())WhatsAppNative.call(request("history").put("jid",chat.jid));''',
       '''            Prefs.get(this).edit().putBoolean("wa_linked",true).putBoolean("wa_connected",true).remove("wa_pair_code").putString("wa_status","Conectado · grupos disponibles. El historial se solicita por grupo.").apply();
            consents(); // Never automatically request every previously authorized chat.''','stop all-group retrieval on reconnect')
    java=one(java, '''            if(chat==null||!chat.selected||!Prefs.get(this).getBoolean("wa_reading",false))return;''',
       '''            if(chat==null||!chat.selected||!Prefs.get(this).getBoolean("wa_reading",false))return;
            if(e.optBoolean("historical")&&!e.optString("jid").equals(requestedHistoryJid))return;''',
       'block historical messages from other JIDs')
    java=one(java, '''        }else if("history_start".equals(type)){
            String jid=e.optString("jid");for(Store.Chat chat:db.chats())if(chat.selected&&!chat.jid.isEmpty()&&(jid.isEmpty()||jid.equals(chat.jid)))db.scanState(chat.key,"Revisando mensajes disponibles…");
        }else if("history_done".equals(type)){
            String jid=e.optString("jid");for(Store.Chat chat:db.chats())if(chat.selected&&!chat.jid.isEmpty()&&(jid.isEmpty()||jid.equals(chat.jid))){
                int count=ReviewFlow.analyzeLinked(this,chat.key,true,"");int messages=db.messageCount(chat.key);
                db.scanState(chat.key,messages+" mensajes guardados · "+count+" propuestas nuevas"+(e.optInt("failed_chunks")>0?" · historial parcial":"")+(messages==0?". WhatsApp aún no entregó historial de este grupo.":""));
            }''',
       '''        }else if("history_start".equals(type)){
            String jid=e.optString("jid");
            if(!jid.isEmpty()&&jid.equals(requestedHistoryJid)){
                Store.Chat chat=db.getChat(Store.linkedKey(jid));
                if(chat!=null&&chat.selected)db.scanState(chat.key,"Revisando mensajes disponibles…");
            }
        }else if("history_done".equals(type)){
            String jid=e.optString("jid");
            if(!jid.isEmpty()&&jid.equals(requestedHistoryJid)){
                Store.Chat chat=db.getChat(Store.linkedKey(jid));
                if(chat!=null&&chat.selected){
                    int count=ReviewFlow.analyzeLinked(this,chat.key,true,"");
                    int messages=db.messageCount(chat.key);
                    db.scanState(chat.key,messages+" mensajes guardados · "+count+" propuestas nuevas"
                        +(e.optInt("failed_chunks")>0?" · historial parcial":"")
                        +(messages==0?". WhatsApp aún no entregó historial de este grupo.":""));
                }
                requestedHistoryJid="";
            }''','strict per-JID status and proposal analysis')
    java=one(java, '''        }else if("disconnected".equals(type)){
            Prefs.get(this).edit().putBoolean("wa_connected",false)''',
        '''        }else if("disconnected".equals(type)){
            requestedHistoryJid="";
            Prefs.get(this).edit().putBoolean("wa_connected",false)''','reset on disconnect')
    styles=one(styles, '''        <item name="android:windowEnterAnimation">@android:anim/fade_in</item>
        <item name="android:windowExitAnimation">@android:anim/fade_out</item>''',
       '''        <item name="android:windowEnterAnimation">@anim/agenda_dialog_fast_in</item>
        <item name="android:windowExitAnimation">@anim/agenda_dialog_fast_out</item>''','quick dialog animation resources')
    motion=one(motion,'setDuration(195).start();','setDuration(105).start();','faster navigation reveal')
    menu=one(menu,'setDuration(190).start();','setDuration(110).start();','faster floating menu')
    gt+='''\nfunc TestHistoricalExtractionDoesNotIncludeAnotherAuthorizedGroup(t *testing.T) {
    ctx:=context.Background()
    c,err:=sqlstore.New(ctx,"sqlite3","file:"+filepath.Join(t.TempDir(),"multi.db")+"?_foreign_keys=on",nil)
    if err!=nil{t.Fatal(err)}
    defer c.Close()
    device,err:=c.GetFirstDevice(ctx);if err!=nil{t.Fatal(err)}
    tr:=&transport{client:whatsmeow.NewClient(device,nil),selected:map[string]bool{"111@g.us":true,"222@g.us":true},
        enabled:true,days:90,anchors:map[string]*types.MessageInfo{},queue:make(chan object,10),stop:make(chan struct{})}
    stamp:=uint64(time.Now().Add(-time.Hour).Unix())
    conv:=func(jid string)*waHistorySync.Conversation{
        return &waHistorySync.Conversation{ID:proto.String(jid),Messages:[]*waHistorySync.HistorySyncMsg{
            {Message:&waWeb.WebMessageInfo{Key:&waCommon.MessageKey{RemoteJID:proto.String(jid),
                Participant:proto.String("999@s.whatsapp.net"),ID:proto.String("abc"),FromMe:proto.Bool(false)},
                MessageTimestamp:&stamp,Message:&waE2E.Message{Conversation:proto.String("Entrega mañana")}}}}}
    }
    batch:=&waHistorySync.HistorySync{Conversations:[]*waHistorySync.Conversation{conv("111@g.us"),conv("222@g.us")}}
    if n:=tr.processHistory(batch,"111@g.us",map[string]bool{"111@g.us":true});n!=1{t.Fatalf("expected one message, got %d",n)}
    if len(tr.queue)!=1{t.Fatalf("unexpected queue count %d",len(tr.queue))}
    event:=<-tr.queue
    if event["jid"]!="111@g.us"{t.Fatalf("different group escaped filter %v",event)}
    if _,ok:=tr.anchors["222@g.us"];ok{t.Fatal("unrequested group anchor retained")}
}
'''
    grad=one(grad,'versionCode 41','versionCode 42','new version code')
    grad=one(grad,"versionName '3.10.0'","versionName '3.10.1'",'new version')
    for path,content in [(GO,go),(GO_TESTS,gt),(JAVA/'WhatsAppSessionService.java',java),
       (STYLE,styles),(JAVA/'UiMotion.java',motion),(JAVA/'CreationChoices.java',menu),(GRADLE,grad)]:
        path.write_text(content,encoding='utf-8')
    anim=ROOT/'app/src/main/res/anim';anim.mkdir(parents=True,exist_ok=True)
    for name,ms,start,end in [('agenda_dialog_fast_in.xml',110,'0.92','1.0'),('agenda_dialog_fast_out.xml',75,'1.0','0.92')]:
        (anim/name).write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<alpha xmlns:android="http://schemas.android.com/apk/res/android"
 android:fromAlpha="{start}" android:toAlpha="{end}" android:duration="{ms}"
 android:interpolator="@android:interpolator/decelerate_quad"/>
''',encoding='utf-8')
    print('PASS phase41: one requested history group, Go and Java filters, fast dialog transitions')
if __name__=='__main__':apply()
