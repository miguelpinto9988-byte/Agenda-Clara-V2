#!/usr/bin/env python3
"""Agenda Clara 3.10.2 — fix history access and smooth window motion."""
from pathlib import Path
import re
R=Path("AgendaClara")
J=R/"app/src/main/java/pe/agendaclara/app"
N=R/"whatsapp-native/main.go"
G=R/"app/build.gradle"
ANIM=R/"app/src/main/res/anim"

def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError("phase42 "+label+": expected one source anchor, got "+str(n))
    return s.replace(a,b,1)

def apply():
    service=(J/"WhatsAppSessionService.java").read_text(encoding="utf-8")
    native=N.read_text(encoding="utf-8")
    main=(J/"MainActivity.java").read_text(encoding="utf-8")
    motion=(J/"UiMotion.java").read_text(encoding="utf-8")
    popup=(J/"CreationChoices.java").read_text(encoding="utf-8")
    window=(J/"WindowLayout.java").read_text(encoding="utf-8")
    grad=G.read_text(encoding="utf-8")

    # Explicitly selected groups are authoritative for app permission.
    # Cached joined is not a permission; actual membership is server-managed.
    service=one(service,
        'JSONArray ids=new JSONArray();for(Store.Chat chat:Store.get(this).chats())if(chat.selected&&!chat.jid.isEmpty()&&chat.joined)ids.put(chat.jid);',
        'JSONArray ids=new JSONArray();for(Store.Chat chat:Store.get(this).chats())if(chat.selected&&!chat.jid.isEmpty()&&!chat.community)ids.put(chat.jid);',
        "consent selected groups without stale joined restriction")
    service=one(service,
        '''if(chat==null||!chat.selected||!chat.joined
                ||!Prefs.get(this).getBoolean("wa_reading",false))
            throw new SecurityException("El grupo no está autorizado para leer mensajes.");''',
        '''if(chat==null||!chat.selected||chat.community
                ||!Prefs.get(this).getBoolean("wa_reading",false))
            throw new SecurityException("Autoriza este grupo en Conexiones para leer sus mensajes.");''',
        "per-group explicit authorization")
    service=one(service,
        '''        requestedHistoryJid=jid;
        db.scanState(key,"history".equals(action)''',
        '''        if(!requestedHistoryJid.isEmpty()){
            db.scanState(key,requestedHistoryJid.equals(jid)
                ?"Ya existe una solicitud de este grupo en curso."
                :"Otra revisión sigue activa. Finalízala antes de solicitar otro grupo.");
            ReviewFlow.changed(this);
            return;
        }
        requestedHistoryJid=jid;
        db.scanState(key,"history".equals(action)''',
        "one active history request only")
    service=one(service,
        '''            worker.schedule(()->{
                if(jid.equals(requestedHistoryJid))requestedHistoryJid="";
                Store.Chat current=db.getChat(key);''',
        '''            worker.schedule(()->{
                if(!jid.equals(requestedHistoryJid))return;
                requestedHistoryJid="";
                Store.Chat current=db.getChat(key);''',
        "do not allow expired watchdog to overwrite another chat")
    service=one(service,"},45,TimeUnit.SECONDS);","},240,TimeUnit.SECONDS);","longer history timeout")
    service=one(service,
        '''            db.scanState(key,"Error al recuperar mensajes. Comprueba el acceso y vuelve a intentarlo.");
            ReviewFlow.changed(this);
            throw failure;''',
        '''            String detail=failure.getMessage()==null?"Error de conexión.":failure.getMessage();
            db.scanState(key,detail.contains("referencia")
                ?"Aún no hay un mensaje de referencia. Usa Revisar historial sincronizado primero."
                :"No se pudo consultar este grupo: "+detail);
            ReviewFlow.changed(this);
            throw failure;''',
        "meaningful access and reference error")

    # Native must reply even if the requested history was already processed.
    native=one(native,
        '''		if !pending {
			return
		}
	}
	t.emit(object{"type": "history_start", "jid": only})''',
        '''		if !pending {
			t.emit(object{"type":"history_done","jid":only,"messages":0,
				"failed_chunks":0,"has_pointers":true,"already_processed":true})
			return
		}
	}
	t.emit(object{"type": "history_start", "jid": only})''',
        "native already-processed completion")
    native=one(native,
        '''if a==nil { return nil,errors.New("Todavía no hay un mensaje de referencia. Revisa primero el historial sincronizado") }''',
        '''if a==nil { return nil,errors.New("No hay mensaje de referencia para este grupo. Usa primero Revisar historial sincronizado") }''',
        "helpful missing anchor message")

    main=one(main,
        'toast("Solicitud enviada. Comprueba el estado del grupo para ver el resultado.");',
        'toast("Solicitando historial de este grupo. Comprueba su estado para ver el resultado.");',
        "don't imply a request has completed")
    navBefore=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]

    window=one(window,
        '''                w.setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);
                decor.requestLayout();
                return;''',
        '''                w.setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);
                return;''',
        "avoid duplicate window layout request")
    motion=one(motion,
        'view.animate().alpha(1f).translationY(0f).setDuration(105).start();',
        '''view.animate().alpha(1f).translationY(0f).setDuration(190)
            .setInterpolator(new android.view.animation.DecelerateInterpolator(1.25f))
            .withLayer().start();''',
        "190ms efficient tab transition")
    popup=one(popup,
        'floating.animate().alpha(1f).translationY(0).setDuration(110).start();',
        '''floating.animate().alpha(1f).translationY(0).setDuration(190)
                .setInterpolator(new android.view.animation.DecelerateInterpolator(1.2f))
                .withLayer().start();''',
        "190ms efficient creation menu")

    grad=one(grad,"versionCode 42","versionCode 43","version code")
    grad=one(grad,"versionName '3.10.1'","versionName '3.10.2'","version name")

    for path,body in [
        (J/"WhatsAppSessionService.java",service),(N,native),
        (J/"MainActivity.java",main),(J/"UiMotion.java",motion),
        (J/"CreationChoices.java",popup),(J/"WindowLayout.java",window),(G,grad)]:
        path.write_text(body,encoding="utf-8")
    for filename,ms,initial,final in [
        ("agenda_dialog_fast_in.xml",200,"0.94","1.0"),
        ("agenda_dialog_fast_out.xml",160,"1.0","0.94")]:
        file=ANIM/filename
        x=file.read_text(encoding="utf-8")
        x=re.sub(r'android:duration="\d+"','android:duration="'+str(ms)+'"',x)
        x=re.sub(r'android:fromAlpha="[^"]+"','android:fromAlpha="'+initial+'"',x)
        x=re.sub(r'android:toAlpha="[^"]+"','android:toAlpha="'+final+'"',x)
        file.write_text(x,encoding="utf-8")
    navAfter=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
    if navBefore!=navAfter:raise RuntimeError("Bottom navigation has changed")
    print("PASS phase42: selected-only group access; 240s request; 190-200ms smooth motion")
if __name__=="__main__":apply()
