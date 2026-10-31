#!/usr/bin/env python3
"""3.10.0: selected WhatsApp history reliability, recoverable dialogs, faster pickers and actionable alarms."""
from pathlib import Path
SRC=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
def one(text,old,new,label):
    count=text.count(old)
    if count!=1:raise RuntimeError(f"phase40 {label}: expected 1 match, got {count}")
    return text.replace(old,new,1)

def run():
    names=["WindowLayout.java","ModernPickers.java","MainActivity.java",
           "WhatsAppSessionService.java","ReviewFlow.java","Reminders.java",
           "ReminderReceiver.java","ScheduleReminders.java",
           "ScheduleAlarmReceiver.java"]
    src={n:(SRC/n).read_text(encoding="utf-8") for n in names}
    grad=GRADLE.read_text(encoding="utf-8")

    # Restore the dialog's natural height after the IME closes, and remove the
    # global-layout observer when the dialog detaches.
    w=src["WindowLayout.java"]
    start=w.index("        View decor=w.getDecorView();final int[] last={-1};")
    end=w.index("\n    }\n    static final class DialogScroll",start)
    w=w[:start]+'''        View decor=w.getDecorView();
        final int[] previousHeight={-1};
        final android.view.ViewTreeObserver.OnGlobalLayoutListener[] listener={null};
        final Runnable fit=()->{
            if(a.isFinishing()||a.isDestroyed()||!decor.isAttachedToWindow())return;
            Rect safe=available(a,decor);
            int width=Math.min(dp(a,600),Math.max(dp(a,180),safe.width()-dp(a,48)));
            int max=Math.max(dp(a,120),safe.height()-dp(a,56));
            if(previousHeight[0]!=max){
                // A previous fixed height must never persist after closing IME.
                previousHeight[0]=max;
                w.setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);
                decor.requestLayout();
                return;
            }
            WindowManager.LayoutParams current=w.getAttributes();
            int target=decor.getMeasuredHeight()>max?max:WindowManager.LayoutParams.WRAP_CONTENT;
            if(current.width!=width||current.height!=target)w.setLayout(width,target);
        };
        listener[0]=fit::run;
        decor.getViewTreeObserver().addOnGlobalLayoutListener(listener[0]);
        decor.addOnAttachStateChangeListener(new View.OnAttachStateChangeListener(){
            @Override public void onViewAttachedToWindow(View v){previousHeight[0]=-1;v.post(fit);}
            @Override public void onViewDetachedFromWindow(View v){
                if(v.getViewTreeObserver().isAlive())
                    v.getViewTreeObserver().removeOnGlobalLayoutListener(listener[0]);
            }
        });
        decor.post(fit);'''+w[end:]
    src["WindowLayout.java"]=w

    # Time dial: create the 12 text cells once and repaint selected values only.
    picker=src["ModernPickers.java"]
    picker=one(picker,
        '''        final Runnable[] redraw={null};
        redraw[0]=()->{
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));''',
        '''        final Runnable[] redraw={null};
        final TextView[] dialCells=new TextView[13];
        final int[] lastHighlighted={0};
        redraw[0]=()->{
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));''',
        "time dial cache")
    picker=one(picker,
        '''            dial.removeAllViews();
            for(int j=1;j<=12;j++){
                final int value=j;double theta=2*Math.PI*j/12.0-Math.PI/2;
                TextView cell=label(a,String.valueOf(j),15,j==hour[0]?0xffffffff:INK);
                cell.setGravity(Gravity.CENTER);
                if(j==hour[0])cell.setBackground(ModernGlyph.rounded(a,BLUE,0,24));
                FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(dp(a,38),dp(a,38));
                lp.leftMargin=dp(a,122-19+(int)Math.round(91*Math.cos(theta)));
                lp.topMargin=dp(a,122-19+(int)Math.round(91*Math.sin(theta)));
                dial.addView(cell,lp);
                cell.setOnClickListener(v->{hour[0]=value;hours.setValue(value);redraw[0].run();});
            }''',
        '''            if(dialCells[1]==null){
                for(int j=1;j<=12;j++){
                    final int value=j;double theta=2*Math.PI*j/12.0-Math.PI/2;
                    TextView cell=label(a,String.valueOf(j),15,INK);
                    cell.setGravity(Gravity.CENTER);
                    FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(dp(a,38),dp(a,38));
                    lp.leftMargin=dp(a,122-19+(int)Math.round(91*Math.cos(theta)));
                    lp.topMargin=dp(a,122-19+(int)Math.round(91*Math.sin(theta)));
                    dialCells[j]=cell;dial.addView(cell,lp);
                    cell.setOnClickListener(v->hours.setValue(value));
                }
            }
            if(lastHighlighted[0]!=hour[0]){
                if(lastHighlighted[0]>0){
                    TextView old=dialCells[lastHighlighted[0]];
                    old.setTextColor(INK);old.setBackground(null);
                }
                TextView selected=dialCells[hour[0]];
                selected.setTextColor(0xffffffff);
                selected.setBackground(ModernGlyph.rounded(a,BLUE,0,24));
                lastHighlighted[0]=hour[0];
            }''',
        "no dial recreation on time change")
    src["ModernPickers.java"]=picker

    # History requests now have honest progress/connected-state diagnostics.
    main=src["MainActivity.java"]
    main=one(main,
        '''            Prefs.get(this).edit().putInt("wa_history_count",choice[0]).apply();try{WhatsAppSessionService.start(this,"more",chat.jid,choice[0]);toast("Solicitando "+choice[0]+" mensajes anteriores. La entrega depende de WhatsApp.");}catch(IllegalStateException|SecurityException e){toast("Abre la app y reanuda la conexión.");}render();''',
        '''            if(!Prefs.get(this).getBoolean("wa_connected",false)||!WhatsAppSessionService.running){
                toast("Conexión no activa. Reanúdala antes de solicitar mensajes anteriores.");
                Store.get(this).scanState(chat.key,"Solicitud pendiente: vuelve a conectar WhatsApp.");
                session("resume",null);render();return;
            }
            Prefs.get(this).edit().putInt("wa_history_count",choice[0]).apply();
            try{
                Store.get(this).scanState(chat.key,"Solicitando "+choice[0]+" mensajes anteriores…");
                WhatsAppSessionService.start(this,"more",chat.jid,choice[0]);
                toast("Solicitud enviada. Comprueba el estado del grupo para ver el resultado.");
            }catch(IllegalStateException|SecurityException e){
                Store.get(this).scanState(chat.key,"No se pudo solicitar el historial. Comprueba la conexión.");
                toast("No se pudo solicitar el historial.");
            }
            render();''',
        "historical request feedback")
    main=one(main,
        '''                details.addView(button("Revisar historial sincronizado",()->session("history",chat.jid)));''',
        '''                details.addView(button("Revisar historial sincronizado",()->{
                    if(!Prefs.get(this).getBoolean("wa_connected",false)||!WhatsAppSessionService.running){
                        toast("Reanuda la conexión de WhatsApp antes de revisar.");
                        session("resume",null);return;
                    }
                    Store.get(this).scanState(chat.key,"Solicitando revisión del historial…");
                    session("history",chat.jid);render();
                }));''',
        "history button connectivity check")
    main=one(main,
        '''        if(!Reminders.canNotify(this)||!Reminders.exact(this)){LinearLayout c=card(body);c.addView(text("Revisa tus avisos",15,INK,true));c.addView(text(!Reminders.canNotify(this)?"Activa las notificaciones en Conexiones para recibir recordatorios.":"Activa «Alarmas y recordatorios» para avisos a la hora elegida. Sin ese permiso, Android puede retrasarlos.",13,MUTED,false));c.addView(button("Ir a Conexiones",()->{page=3;render();}));}''',
        '''        if(!Reminders.canNotify(this)||!Reminders.exact(this)){
            LinearLayout c=card(body);c.addView(text("Revisa tus avisos",15,INK,true));
            c.addView(text(!Reminders.canNotify(this)
                ?"El canal de avisos o los permisos de Android están bloqueados. Configura las notificaciones de Agenda Clara."
                :"Permite «Alarmas y recordatorios» para avisos puntuales; sin ello Android puede retrasarlos.",13,MUTED,false));
            c.addView(button(!Reminders.canNotify(this)?"Configurar notificaciones":"Configurar alarmas",()->{
                Intent settings=!Reminders.canNotify(this)
                    ?new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                       .putExtra(Settings.EXTRA_APP_PACKAGE,getPackageName())
                    :new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                       .setData(Uri.parse("package:"+getPackageName()));
                safeStart(settings);
            }));
        }''',
        "directly fix blocked reminders settings")
    src["MainActivity.java"]=main

    service=src["WhatsAppSessionService.java"]
    service=one(service,
        '''                else if("history".equals(action)){consents();WhatsAppNative.call(request("history").put("jid",value));}
                else if("more".equals(action)){if(!HistoryPageOptions.valid(count))throw new IllegalArgumentException("Elige de 10 a 50 mensajes, en pasos de 10.");consents();WhatsAppNative.call(request("more").put("jid",value).put("count",count));}''',
        '''                else if("history".equals(action)||"more".equals(action))
                    requestHistory(action,value,count);''',
        "history request centralized")
    service=one(service,
        '''    private void error(String message){''',
        '''    private void requestHistory(String action,String jid,int count)throws Exception{
        if(jid==null||jid.trim().isEmpty())throw new IllegalArgumentException("Selecciona un grupo válido.");
        Store db=Store.get(this);String key=Store.linkedKey(jid);
        Store.Chat chat=db.getChat(key);
        if(chat==null||!chat.selected||!chat.joined
                ||!Prefs.get(this).getBoolean("wa_reading",false))
            throw new SecurityException("El grupo no está autorizado para leer mensajes.");
        if("more".equals(action)&&!HistoryPageOptions.valid(count))
            throw new IllegalArgumentException("Elige de 10 a 50 mensajes.");
        if(!Prefs.get(this).getBoolean("wa_connected",false)){
            db.scanState(key,"WhatsApp no está conectado. Reanuda la conexión antes de revisar.");
            ReviewFlow.changed(this);return;
        }
        db.scanState(key,"history".equals(action)
                ?"Solicitando historial sincronizado…"
                :"Solicitando "+count+" mensajes anteriores…");
        ReviewFlow.changed(this);
        try{
            consents();
            JSONObject req=request(action).put("jid",jid);
            if("more".equals(action))req.put("count",count);
            WhatsAppNative.call(req);
            // Native request accepted does not guarantee that WhatsApp delivered data.
            worker.schedule(()->{
                Store.Chat current=db.getChat(key);
                if(current!=null&&current.selected
                        &&(current.scanState.startsWith("Solicitando")
                            ||current.scanState.startsWith("Revisando"))){
                    db.scanState(key,"WhatsApp todavía no confirmó la entrega de mensajes. "
                        +"Comprueba la conexión o importa el chat .txt.");
                    ReviewFlow.changed(this);
                }
            },45,TimeUnit.SECONDS);
        }catch(Exception failure){
            db.scanState(key,"Error al recuperar mensajes. Comprueba el acceso y vuelve a intentarlo.");
            ReviewFlow.changed(this);
            throw failure;
        }
    }
    private void error(String message){''',
        "history errors visible per selected chat")
    src["WhatsAppSessionService.java"]=service

    flow=src["ReviewFlow.java"]
    flow=one(flow,
        '''        for(long id:db.withdrawMissing(chatKey,ids,origins))Reminders.cancelProposal(c,id);''',
        '''        // A bounded or incomplete history is not an authoritative deletion
        // list. Never silently retract previously reviewed messages on pagination.
        // Explicit revocation/deletion remains responsible for removing proposals.''',
        "stop retraction caused by paginated history")
    src["ReviewFlow.java"]=flow

    reminder=src["Reminders.java"]
    reminder=one(reminder,
        'public static final String CHANNEL="task_deadlines",IMPORT_CHANNEL="message_proposals";',
        'public static final String CHANNEL="task_deadlines",IMPORT_CHANNEL="message_proposals",ACTION_CHANNEL="task_actions_v1";',
        "confirmation channel name")
    reminder=one(reminder,
        '        nm.createNotificationChannel(due);',
        '        nm.createNotificationChannel(due);\n        nm.createNotificationChannel(new NotificationChannel(ACTION_CHANNEL,"Confirmaciones de avisos",NotificationManager.IMPORTANCE_LOW));',
        "confirmation low-importance channel")
    reminder=one(reminder,
        '''        return (Build.VERSION.SDK_INT<33||c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)==PackageManager.PERMISSION_GRANTED)&&c.getSystemService(NotificationManager.class).areNotificationsEnabled();''',
        '''        NotificationManager nm=c.getSystemService(NotificationManager.class);
        if(Build.VERSION.SDK_INT>=33&&c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)return false;
        NotificationChannel channel=nm.getNotificationChannel(CHANNEL);
        return nm.areNotificationsEnabled()&&(channel==null||channel.getImportance()!=NotificationManager.IMPORTANCE_NONE);''',
        "respect muted or blocked task channel")
    reminder=one(reminder,
        '''    public static void showProposal(Context c,Store.Inbox p){''',
        '''    public static void acknowledge(Context c,Task t,String status){
        channels(c);if(!canNotify(c))return;
        Intent open=new Intent(c,MainActivity.class).setAction("open")
            .setData(Uri.parse("agenda://task/"+t.id)).putExtra("task_id",t.id)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent click=PendingIntent.getActivity(c,0,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification n=new Notification.Builder(c,ACTION_CHANNEL).setSmallIcon(R.drawable.ic_notify)
            .setContentTitle(status).setContentText(t.title).setContentIntent(click)
            .setOnlyAlertOnce(true).setAutoCancel(true)
            .setCategory(Notification.CATEGORY_STATUS).build();
        c.getSystemService(NotificationManager.class).notify("task_action", (int)t.id,n);
    }
    public static void showProposal(Context c,Store.Inbox p){''',
        "action status feedback")
    src["Reminders.java"]=reminder

    receiver=src["ReminderReceiver.java"]
    receiver=one(receiver,
        '''        if("complete".equals(action)){t.done=true;Store.get(c).save(t);Reminders.cancel(c,id);TaskWidget.refresh(c);return;}''',
        '''        if("complete".equals(action)){
            t.done=true;Store.get(c).save(t);Reminders.cancel(c,id);
            TaskWidget.refresh(c);Reminders.acknowledge(c,t,"Tarea completada");return;
        }''',
        "complete response")
    receiver=one(receiver,
        '''            catch(SecurityException e){a.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p);}return;''',
        '''            catch(SecurityException e){a.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p);}
            c.getSystemService(NotificationManager.class).cancel((int)id);
            Reminders.acknowledge(c,t,"Aviso pospuesto "+minutes+" minutos");
            return;''',
        "snooze response")
    src["ReminderReceiver.java"]=receiver

    schedule=src["ScheduleReminders.java"]
    schedule=one(schedule,
        '''        Notification.Builder n=new Notification.Builder(c,CHANNEL).setSmallIcon(R.drawable.ic_notify).setContentTitle("Clase: "+s.course).setContentText(text)''',
        '''        PendingIntent again=PendingIntent.getBroadcast(c,0,
            new Intent(c,ScheduleAlarmReceiver.class).setAction("pe.agendaclara.SCHEDULE_SNOOZE")
                .setData(Uri.parse("agenda://class-snooze/"+s.id)).putExtra("class_id",s.id),
            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder n=new Notification.Builder(c,CHANNEL).setSmallIcon(R.drawable.ic_notify).setContentTitle("Clase: "+s.course).setContentText(text)''',
        "class notification new action")
    schedule=one(schedule,
        '''            .setCategory(Notification.CATEGORY_REMINDER).setVisibility(Notification.VISIBILITY_PRIVATE).setAutoCancel(true);''',
        '''            .setCategory(Notification.CATEGORY_REMINDER).setVisibility(Notification.VISIBILITY_PRIVATE).setAutoCancel(true)
            .addAction(new Notification.Action.Builder(null,"Ver horario",click).build())
            .addAction(new Notification.Action.Builder(null,"En 10 min",again).build());''',
        "class notification actionable")
    src["ScheduleReminders.java"]=schedule

    classReceiver=src["ScheduleAlarmReceiver.java"]
    classReceiver=one(classReceiver,
        '''        if(!ScheduleReminders.ACTION.equals(i.getAction()))return;''',
        '''        if("pe.agendaclara.SCHEDULE_SNOOZE".equals(i.getAction())){
            long id=i.getLongExtra("class_id",-1);
            if(id<=0)return;
            ScheduleEntry s=ScheduleDatabase.get(c).find(id);
            if(s==null||!s.enabled)return;
            android.app.AlarmManager alarms=c.getSystemService(android.app.AlarmManager.class);
            android.content.Intent remind=new android.content.Intent(c,ScheduleAlarmReceiver.class)
                .setAction("pe.agendaclara.SCHEDULE_SNOOZE_DELIVER")
                .setData(android.net.Uri.parse("agenda://class-snooze-deliver/"+id))
                .putExtra("class_id",id);
            android.app.PendingIntent pending=android.app.PendingIntent.getBroadcast(c,0,remind,
                android.app.PendingIntent.FLAG_UPDATE_CURRENT|android.app.PendingIntent.FLAG_IMMUTABLE);
            alarms.setAndAllowWhileIdle(android.app.AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis()+10*60000L,pending);
            c.getSystemService(android.app.NotificationManager.class).cancel("class",(int)id);
            return;
        }
        if(!ScheduleReminders.ACTION.equals(i.getAction())
                &&!"pe.agendaclara.SCHEDULE_SNOOZE_DELIVER".equals(i.getAction()))return;
        boolean snoozed="pe.agendaclara.SCHEDULE_SNOOZE_DELIVER".equals(i.getAction());''',
        "class snooze receiver routing")
    classReceiver=one(classReceiver,
        '''                ScheduleReminders.schedule(c,s);''',
        '''                if(!snoozed)ScheduleReminders.schedule(c,s);''',
        "snooze does not overwrite next weekly alarm")
    src["ScheduleAlarmReceiver.java"]=classReceiver

    grad=one(grad,"versionCode 40","versionCode 41","version code")
    grad=one(grad,"versionName '3.9.9'","versionName '3.10.0'","version name")

    for name,content in src.items():(SRC/name).write_text(content,encoding="utf-8")
    GRADLE.write_text(grad,encoding="utf-8")
    print("PASS phase40: WhatsApp history states, keyboard dialog restoration, faster clock dial, actionable reminder feedback, 3.10.0")

if __name__=="__main__":run()
