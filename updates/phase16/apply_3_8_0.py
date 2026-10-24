#!/usr/bin/env python3
"""Phase 16: robust notification capture, verified interpretation and consistent Android UI.
Run after updates/phase15/apply_3_7_1.py. Does not touch keystores or the database schema.
"""
from pathlib import Path
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def rep(name,old,new):
    p=src/name
    t=p.read_text(encoding="utf-8")
    n=t.count(old)
    if n!=1:
        raise RuntimeError(f"Phase 16: {name}: expected one anchor, found {n}: {old[:110]!r}")
    p.write_text(t.replace(old,new,1),encoding="utf-8")

rep("WhatsAppListener.java",
    'private void submit(Runnable r){if(!worker.isShutdown())try{worker.execute(r);}catch(RejectedExecutionException ignored){}}',
    '''private void submit(Runnable r){
        if(!worker.isShutdown())try{worker.execute(()->{
            try{r.run();}catch(RuntimeException problem){
                // Never log message text or chat names.
                android.util.Log.e("AgendaCapture","Error de captura: "+problem.getClass().getSimpleName());
                Prefs.get(this).edit().putString("wa_diag_state",
                    "Error leyendo una notificación ("+problem.getClass().getSimpleName()+"). Revisa acceso y vuelve a probar.").apply();
                ReviewFlow.changed(this);
            }
        });}catch(RejectedExecutionException ignored){}
    }''')
rep("WhatsAppListener.java",
    'try{StatusBarNotification[] list=getActiveNotifications();if(list!=null)for(StatusBarNotification n:list)inspect(n,false);}catch(SecurityException|IllegalStateException ignored){}',
    '''try{StatusBarNotification[] list=getActiveNotifications();if(list!=null)for(StatusBarNotification n:list)inspect(n,false);}
        catch(SecurityException|IllegalStateException problem){
            Prefs.get(this).edit().putString("wa_diag_state",
                "No se pudieron consultar las notificaciones: comprueba el acceso del sistema.").apply();
            ReviewFlow.changed(this);
        }''')
rep("WhatsAppListener.java",
    '                .putString("wa_diag_state",enabled()?"Notificación WhatsApp detectada":"Detección de WhatsApp desactivada").apply();',
    '''                .putString("wa_diag_state",enabled()?"Notificación WhatsApp detectada":"Detección de WhatsApp desactivada").apply();
            ReviewFlow.changed(this);''')
rep("WhatsAppListener.java",
    '''            if(!received){
                String body=str(e.getCharSequence(Notification.EXTRA_BIG_TEXT));
                if(body.isEmpty())body=str(e.getCharSequence(Notification.EXTRA_TEXT));
                if(!body.isEmpty())accept(key,body,sbn.getPostTime());
                else Prefs.get(this).edit().putString("wa_diag_state","Notificación sin texto visible: revisa privacidad de WhatsApp").apply();
            }''',
    '''            if(!received){
                // Android may expose bundled text lines instead of MessagingStyle on some devices.
                CharSequence[] lines=e.getCharSequenceArray(Notification.EXTRA_TEXT_LINES);
                if(lines!=null)for(CharSequence line:lines){
                    String body=str(line);
                    if(!body.isEmpty()&&!isGenericSummary(body)){
                        received=true;
                        accept(key,body,sbn.getPostTime());
                    }
                }
            }
            if(!received){
                String body=str(e.getCharSequence(Notification.EXTRA_BIG_TEXT));
                if(body.isEmpty())body=str(e.getCharSequence(Notification.EXTRA_TEXT));
                if(!body.isEmpty()&&!isGenericSummary(body))accept(key,body,sbn.getPostTime());
                else Prefs.get(this).edit().putString("wa_diag_state",
                    "Notificación sin texto de mensaje: comprueba la vista previa y la privacidad en WhatsApp.").apply();
            }''')
rep("WhatsAppListener.java",
    '    private String str(CharSequence s){return s==null?"":s.toString().trim();}',
    '''    private String str(CharSequence s){return s==null?"":s.toString().trim();}
    private static boolean isGenericSummary(String s){
        return NotificationSummaryPolicy.isSummary(s);
    }''')
(src/"NotificationSummaryPolicy.java").write_text('''package pe.agendaclara.app;
import java.util.Locale;
/** Avoid passing aggregate notification-count summaries to task interpretation. */
public final class NotificationSummaryPolicy {
    private NotificationSummaryPolicy(){}
    public static boolean isSummary(String message){
        if(message==null)return true;
        String s=message.trim().toLowerCase(Locale.ROOT);
        if(s.isEmpty())return true;
        return s.matches("\\\\d+\\\\s+(?:mensajes?|messages?|chats?)\\\\s+(?:nuevos?|new|sin leer|unread)(?:\\\\b.*)?")
            || s.matches("\\\\d+\\\\s+(?:new|unread)\\\\s+(?:messages?|chats?)(?:\\\\b.*)?")
            || s.matches("(?:notificaciones|notifications)\\\\s+(?:de|from)\\\\s+whatsapp");
    }
}
''',encoding="utf-8")
rep("MainActivity.java",
    'if(enabled!=null)for(String item:enabled.split(":"))if(component.equals(item))return true;return false;',
    '''if(enabled!=null)for(String item:enabled.split(":")){
            ComponentName name=ComponentName.unflattenFromString(item);
            if(name!=null&&name.equals(new ComponentName(this,WhatsAppListener.class)))return true;
        }
        return false;''')
rep("MainActivity.java",
    '''                Prefs.get(this).edit().putBoolean("discover",true).putBoolean("capture",true).putLong("capture_since",System.currentTimeMillis()).apply();
                // POST_NOTIFICATIONS''',
    '''                SharedPreferences prefs=Prefs.get(this);
                SharedPreferences.Editor edit=prefs.edit().putBoolean("discover",true).putBoolean("capture",true);
                if(!prefs.getBoolean("capture",false))edit.putLong("capture_since",System.currentTimeMillis());
                edit.apply();
                // POST_NOTIFICATIONS''')
rep("MainActivity.java",
    '''                    Prefs.get(this).edit().putBoolean("discover",true).putBoolean("capture",true).putLong("capture_since",System.currentTimeMillis()).apply();
                    if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));''',
    '''                    SharedPreferences prefs=Prefs.get(this);
                    SharedPreferences.Editor edit=prefs.edit().putBoolean("discover",true).putBoolean("capture",true);
                    if(!prefs.getBoolean("capture",false))edit.putLong("capture_since",System.currentTimeMillis());
                    edit.apply();
                    if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));''')
rep("MainActivity.java",
    '''            prefs.edit().putBoolean("discover",on).putBoolean("capture",on).putLong("capture_since",System.currentTimeMillis()).apply();
            if(on){''',
    '''            SharedPreferences.Editor change=prefs.edit().putBoolean("discover",on).putBoolean("capture",on);
            if(on&&!prefs.getBoolean("capture",false))change.putLong("capture_since",System.currentTimeMillis());
            change.apply();
            if(on){''')
rep("MainActivity.java",
    '''"wa_pair_code","wa_pair_expires","capture","discover"})''',
    '''"wa_pair_code","wa_pair_expires","capture","discover","wa_diag_state","wa_diag_event_count","wa_diag_received_count","wa_diag_proposal_count","wa_diag_last_whatsapp","wa_diag_last_received"})''')
rep("MainActivity.java",
    '        diagnostic.addView(button("Actualizar diagnóstico",()->{forceRefresh=true;render();}));',
    '''        diagnostic.addView(button("Actualizar diagnóstico",()->{forceRefresh=true;render();}));
        diagnostic.addView(button("Probar intérprete sin guardar datos",()->{
            String sample="Para mañana deben entregar el informe y preparar una exposición.";
            int found=MessageParser.parse(sample,System.currentTimeMillis(),
                java.time.ZoneId.systemDefault(),false).size();
            dialogBuilder().setTitle("Prueba local del intérprete")
                .setMessage("Propuestas detectadas: "+found+
                    "\\\\nEsta prueba no lee WhatsApp, no guarda mensajes y no crea tareas. "+
                    (found>0?"El análisis básico funciona; comprueba ahora el permiso de recepción.":"No se ha reconocido la muestra: revisa el clasificador."))
                .setPositiveButton("Entendido",null).show();
        }));''')
rep("MainActivity.java",
    '        if(Prefs.get(this).getBoolean("wa_linked",false)&&Prefs.get(this).getBoolean("wa_reading",false)&&!WhatsAppSessionService.running)session("resume",null);new Thread(',
    '''        if(Prefs.get(this).getBoolean("wa_linked",false)&&Prefs.get(this).getBoolean("wa_reading",false)&&!WhatsAppSessionService.running)session("resume",null);
        if(Prefs.get(this).getBoolean("capture",false)&&notificationAccess()){
            try{android.service.notification.NotificationListenerService.requestRebind(
                new ComponentName(this,WhatsAppListener.class));}catch(SecurityException ignored){}
        }
        new Thread(''')
# Shared refinements use existing Android-native components; no WebView or external UI assets.
rep("MainActivity.java",
    'TextView t=new TextView(this);t.setText(s);t.setTextSize(UiPreferences.scaled(this,size));t.setTextColor(UiPreferences.foreground(this,color,MUTED));',
    'TextView t=new TextView(this);t.setText(s);t.setTextSize(UiPreferences.scaled(this,size));t.setLineSpacing(dp(2),1.04f);t.setTextColor(UiPreferences.foreground(this,color,MUTED));')
rep("MainActivity.java",
    'c.setPadding(dp(16),dp(15),dp(16),dp(15));c.setBackground(outlined(SURFACE,23,STROKE));c.setElevation(dp(3));',
    'c.setPadding(dp(18),dp(17),dp(18),dp(17));c.setBackground(outlined(SURFACE,24,STROKE));c.setElevation(dp(3));')
rep("MainActivity.java",
    'nav.setPadding(dp(7),dp(6),dp(7),dp(7));',
    'nav.setPadding(dp(10),dp(8),dp(10),dp(9));')
rep("MainActivity.java",
    'item.setBackground(rounded(page==n?PALE:0xffffffff,15));',
    'item.setBackground(rounded(page==n?PALE:0xfffcfdff,18));')
rep("MainActivity.java",
    'item.setPadding(0,dp(5),0,dp(4));',
    'item.setPadding(0,dp(7),0,dp(6));')
rep("MainActivity.java",
    'names.addView(headerDate);names.addView(headerTitle);',
    'names.addView(headerDate);gap(names,4);names.addView(headerTitle);')
grad=Path("AgendaClara/app/build.gradle")
b=grad.read_text(encoding="utf-8")
assert b.count("versionCode 27")==1 and b.count("versionName '3.7.0'")==1
grad.write_text(b.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.8.0'"),encoding="utf-8")
print("PASS: phase 16 capture continuity, Android listener diagnostics, fallback notification text and refreshed native UI")
