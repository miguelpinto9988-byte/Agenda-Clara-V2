#!/usr/bin/env python3
"""Agenda Clara 3.7.1: WhatsApp notification diagnostics and consistent native visual refresh.
Apply AFTER updates/interpretation/apply.py. No signature, database schema, or user data changes.
"""
from pathlib import Path

base=Path("AgendaClara/app/src/main")
src=base/"java/pe/agendaclara/app"

def one(file, old, new):
    p=Path(file)
    data=p.read_text(encoding="utf-8")
    matches=data.count(old)
    if matches != 1:
        raise RuntimeError(f"{p}: expected one anchor, found {matches}: {old[:110]!r}")
    p.write_text(data.replace(old,new,1),encoding="utf-8")

listener=src/"WhatsAppListener.java"
one(listener,
    'private boolean enabled(){return Prefs.get(this).getBoolean("discover",Prefs.get(this).getBoolean("capture",false));}',
    'private boolean enabled(){return Prefs.get(this).getBoolean("discover",false)||Prefs.get(this).getBoolean("capture",false);}')
one(listener,
    '@Override public void onListenerConnected(){super.onListenerConnected();scan();}',
    '''@Override public void onListenerConnected(){
        super.onListenerConnected();
        Prefs.get(this).edit().putBoolean("wa_diag_listener_connected",true)
            .putLong("wa_diag_last_connected",System.currentTimeMillis())
            .putString("wa_diag_state","Servicio Android conectado").apply();
        scan();
    }
    @Override public void onListenerDisconnected(){
        Prefs.get(this).edit().putBoolean("wa_diag_listener_connected",false)
            .putString("wa_diag_state","Servicio de notificaciones desconectado").apply();
        super.onListenerDisconnected();
    }''')
one(listener,
    '@Override public void onNotificationPosted(StatusBarNotification sbn){inspect(sbn,true);}',
    '''@Override public void onNotificationPosted(StatusBarNotification sbn){
        if(sbn!=null&&("com.whatsapp".equals(sbn.getPackageName())||"com.whatsapp.w4b".equals(sbn.getPackageName()))){
            android.content.SharedPreferences p=Prefs.get(this);
            p.edit().putLong("wa_diag_last_whatsapp",System.currentTimeMillis())
                .putInt("wa_diag_event_count",p.getInt("wa_diag_event_count",0)+1)
                .putString("wa_diag_state",enabled()?"Notificación WhatsApp detectada":"Detección de WhatsApp desactivada").apply();
        }
        inspect(sbn,true);
    }
    private void accept(String key,String body,long sent){
        // Only called AFTER explicit chat selection; never persists plaintext diagnostics.
        int proposals=ReviewFlow.receive(this,key,body,sent);
        android.content.SharedPreferences p=Prefs.get(this);
        p.edit().putLong("wa_diag_last_received",System.currentTimeMillis())
            .putInt("wa_diag_received_count",p.getInt("wa_diag_received_count",0)+1)
            .putInt("wa_diag_proposal_count",p.getInt("wa_diag_proposal_count",0)+proposals)
            .putString("wa_diag_state",proposals>0?"Actividad enviada a revisión":"Texto recibido; ninguna tarea nueva detectada").apply();
    }''')
one(listener,
    'if(!incoming||!Prefs.get(this).getBoolean("capture",false)||chat==null||!chat.selected)return;',
    '''if(!incoming)return;
            if(!Prefs.get(this).getBoolean("capture",false)){
                Prefs.get(this).edit().putString("wa_diag_state","Lectura por notificaciones desactivada").apply();
                return;
            }
            if(chat==null||!chat.selected){
                Prefs.get(this).edit().putString("wa_diag_state","Chat detectado: selección pendiente").apply();
                return;
            }
            Prefs.get(this).edit().putString("wa_diag_state","Chat autorizado; procesando notificación").apply();''')
data=listener.read_text(encoding="utf-8")
begin='            Parcelable[] messages=e.getParcelableArray(Notification.EXTRA_MESSAGES);'
stop='\n        });'
assert data.count(begin)==1 and data.count(stop)==1
start=data.index(begin)
end=data.index(stop,start)
replacement='''            Parcelable[] messages=e.getParcelableArray(Notification.EXTRA_MESSAGES);
            boolean received=false;
            if(messages!=null&&messages.length>0){
                if(Build.VERSION.SDK_INT>=30){
                    for(Notification.MessagingStyle.Message msg:Notification.MessagingStyle.Message.getMessagesFromBundleArray(messages)){
                        String body=str(msg.getText());
                        if(!body.isEmpty()){
                            received=true;
                            accept(key,body,msg.getTimestamp()>0?msg.getTimestamp():sbn.getPostTime());
                        }
                    }
                }else{
                    for(Parcelable item:messages)if(item instanceof Bundle){
                        Bundle msg=(Bundle)item;String body=str(msg.getCharSequence("text"));
                        if(!body.isEmpty()){
                            received=true;
                            accept(key,body,msg.getLong("time",sbn.getPostTime()));
                        }
                    }
                }
            }
            if(!received){
                String body=str(e.getCharSequence(Notification.EXTRA_BIG_TEXT));
                if(body.isEmpty())body=str(e.getCharSequence(Notification.EXTRA_TEXT));
                if(!body.isEmpty())accept(key,body,sbn.getPostTime());
                else Prefs.get(this).edit().putString("wa_diag_state","Notificación sin texto visible: revisa privacidad de WhatsApp").apply();
            }'''
listener.write_text(data[:start]+replacement+data[end:],encoding="utf-8")

main=src/"MainActivity.java"
one(main,
'''                if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},32);
                else safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));render();''',
'''                // POST_NOTIFICATIONS is for showing alerts, NOT for receiving WhatsApp messages.
                // Always open Android's dedicated Notification Listener access screen.
                safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));render();''')
one(main,
    'if(on){if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));else sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));}',
    '''if(on){
                if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                else {
                    android.service.notification.NotificationListenerService.requestRebind(new ComponentName(this,WhatsAppListener.class));
                    sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));
                }
            }''')
one(main,
    '    void whatsappSettings(){\n        SharedPreferences prefs=Prefs.get(this);',
    '''    void whatsappSettings(){
        SharedPreferences prefs=Prefs.get(this);''')
# Insert diagnostics into the live Conexiones > WhatsApp screen.
one(main,
    '        subtitle(body,"Comunidades, grupos y chats · "+selected+" autorizados");',
    '''        LinearLayout diagnostic=card(body);
        diagnostic.setBackground(gradient(0xffffffff,0xfff1f5ff,22));
        diagnostic.addView(text("Diagnóstico de recepción · WhatsApp",17,INK,true));
        gap(diagnostic,6);
        boolean listenerPermission=notificationAccess();
        boolean listenerRunning=prefs.getBoolean("wa_diag_listener_connected",false);
        boolean captureOn=prefs.getBoolean("capture",false);
        diagnostic.addView(text("Acceso de Android: "+(listenerPermission?"Concedido":"Pendiente")+
            "  ·  Servicio: "+(listenerRunning?"Conectado":"No confirmado")+
            "\\nCaptura de mensajes: "+(captureOn?"Activada":"Desactivada")+
            "  ·  Chats seleccionados: "+selected,13,INK,false));
        long lastNotif=prefs.getLong("wa_diag_last_whatsapp",0);
        long lastMsg=prefs.getLong("wa_diag_last_received",0);
        diagnostic.addView(text("Última notificación: "+(lastNotif==0?"Sin registrar":new java.util.Date(lastNotif).toString())+
            "\\nÚltimo texto autorizado: "+(lastMsg==0?"Sin registrar":new java.util.Date(lastMsg).toString())+
            "\\nNotificaciones detectadas: "+prefs.getInt("wa_diag_event_count",0)+
            " · Textos recibidos: "+prefs.getInt("wa_diag_received_count",0)+
            " · Propuestas: "+prefs.getInt("wa_diag_proposal_count",0),12,MUTED,false));
        diagnostic.addView(text(prefs.getString("wa_diag_state","Sin diagnóstico todavía. Envía un mensaje de prueba desde otro dispositivo."),12,MUTED,false));
        diagnostic.addView(button("Configurar acceso de lectura",()->safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))));
        diagnostic.addView(button("Actualizar diagnóstico",()->{forceRefresh=true;render();}));
        diagnostic.addView(text("Los contadores no guardan texto de chats sin autorizar. Si WhatsApp oculta el contenido de las notificaciones, Android no puede entregarlo al intérprete.",12,MUTED,false));
        subtitle(body,"Comunidades, grupos y chats · "+selected+" autorizados");''')
one(main,
    'static final int BG=0xfff4f7ff,INK=0xff101d43,GREEN=0xff2765f2,MUTED=0xff647393,RED=0xffe55c5c;',
    'static final int BG=0xfff6f8fc,INK=0xff162441,GREEN=0xff3957d7,MUTED=0xff60738b,RED=0xffd45063;')
one(main,
    'static final int VIOLET=0xff7158e8,SUCCESS=0xff078568,SURFACE=0xffffffff,PALE=0xffe9f0ff,STROKE=0xffe0e8f8;',
    'static final int VIOLET=0xff8466dc,SUCCESS=0xff0d8d83,SURFACE=0xffffffff,PALE=0xffedf0ff,STROKE=0xffdfe5f1;')
one(main,
    'c.setBackground(outlined(SURFACE,20,STROKE));c.setElevation(dp(2));',
    'c.setBackground(outlined(SURFACE,23,STROKE));c.setElevation(dp(3));')
one(main,
    'b.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x222765f2),rounded(PALE,13),null));',
    'b.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x203957d7),rounded(PALE,16),null));')
one(main,
    'button.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x30ffffff),gradient(GREEN,0xff477df4,14),null));',
    'button.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x30ffffff),gradient(GREEN,0xff7465ec,17),null));')
one(main,
    'add.setBackground(gradient(GREEN,0xff397dff,17));',
    'add.setBackground(gradient(GREEN,0xff7465ec,19));')
one(main,
    'nav.setBackgroundColor(0xffffffff);',
    'nav.setBackgroundColor(0xfffcfdff);')
one(main,
    'hero.setBackground(rounded(GREEN,22));',
    'hero.setBackground(gradient(0xff2748b9,0xff7563d9,23));')

schedule=src/"ScheduleActivity.java"
one(schedule,
    'private static final int BG=0xfff4f7ff,INK=0xff101d43,BLUE=0xff2765f2,MUTED=0xff647393,PALE=0xffe9f0ff,LINE=0xffe0e8f8,RED=0xffd84e5f;',
    'private static final int BG=0xfff6f8fc,INK=0xff162441,BLUE=0xff3957d7,MUTED=0xff60738b,PALE=0xffedf0ff,LINE=0xffdfe5f1,RED=0xffd45063;')
one(schedule,'c.setBackground(outline(0xffffffff,19));','c.setBackground(outline(0xffffffff,23));')
one(schedule,'b.setBackground(primary?bg(BLUE,15):outline(PALE,15));','b.setBackground(primary?bg(BLUE,17):outline(PALE,17));')

styles=base/"res/values/styles.xml"
s=styles.read_text(encoding="utf-8").replace("#2765F2","#3957D7").replace("#F4F7FF","#F6F8FC")
styles.write_text(s,encoding="utf-8")
styles31=base/"res/values-v31/styles.xml"
s=styles31.read_text(encoding="utf-8").replace("#2765F2","#3957D7").replace("#F4F7FF","#F6F8FC")
styles31.write_text(s,encoding="utf-8")
compose=src/"ComposeDayActivity.kt"
s=compose.read_text(encoding="utf-8").replace("0xFF2765F2","0xFF3957D7").replace("0xFFF4F7FF","0xFFF6F8FC").replace("0xFF101D43","0xFF162441")
compose.write_text(s,encoding="utf-8")
print("PASS: WhatsApp permission flow, privacy-safe diagnostics and shared UI palette applied")
