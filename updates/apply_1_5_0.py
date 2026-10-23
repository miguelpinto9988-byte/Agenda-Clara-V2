#!/usr/bin/env python3
"""Agenda Clara 1.5.0: filtros de grupos, análisis de cambios y diagnóstico de calendario.
Se aplica después de apply_1_3_1.py y apply_1_4_0.py. No maneja firmas privadas.
"""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def patch(file,old,new):
    path=p/file
    s=path.read_text(encoding="utf-8")
    if s.count(old)!=1:raise RuntimeError(f"{file}: patrón {repr(old[:120])} aparece {s.count(old)} veces")
    path.write_text(s.replace(old,new,1),encoding="utf-8")

patch("ActivityClassifier.java",
'|no (?:entregar|presentar|enviar|hacer)|no se entrega|cancelad',
'|no (?:entregar|presentar|enviar|hacer)|no se entrega|no habra|no se realizara|no hace falta|ya no hay|cancelad')
patch("ActivityClassifier.java",
'|sustentacion|exposicion|evaluacion|entrega|actividad|trabajo|tarea)\\\\b',
'|sustentacion|exposicion|evaluacion|entrega|actividad|trabajo|tarea|simulacro|parcial|prueba|control de lectura)\\\\b')
patch("ActivityClassifier.java",
'|evaluacion)\\\\b|\\\\b(?:vamos a reunirnos|nos reuniremos)',
'|evaluacion|simulacro|parcial|prueba)\\\\b|\\\\b(?:vamos a reunirnos|nos reuniremos)')
patch("ConversationAnalyzer.java",
'    private static final Pattern UPDATE=Pattern.compile("\\\\b(?:para|hasta|fecha|entrega|plazo|sera|queda|es el|a las)\\\\b");',
'    private static final Pattern UPDATE=Pattern.compile("\\\\b(?:para|hasta|fecha|entrega|plazo|sera|queda|es el|a las|se reprograma|se adelanta|se cambia|se posterga|nueva fecha)\\\\b");')
patch("ConversationAnalyzer.java",
'        for(Message m:ordered){\n            if(updates.containsKey(m.id))continue;\n            Message closure=replies.get(m.id);',
'''        for(Message m:ordered){
            if(updates.containsKey(m.id))continue;
            // Edición de fecha vinculada mediante respuesta citada: conservar la clave de
            // la actividad original y pedir confirmación del usuario. No crear dos propuestas.
            if(!m.reply.isEmpty()&&updates.get(m.reply)==m){
                MessageParser.Proposal activity=MessageParser.parseOne(m.quoted,m.time,zone,false);
                MessageParser.Proposal schedule=MessageParser.parseOne(m.body,m.time,zone,true);
                if(activity.action&&schedule.dateKnown&&!schedule.ambiguous){
                    activity.original=m.body+"\\\\n\\\\nRespuesta a: "+m.quoted;
                    activity.due=schedule.due;activity.dateKnown=true;activity.timeKnown=schedule.timeKnown;
                    activity.ambiguous=true;
                    activity.reason="La respuesta cambia la fecha de una actividad. Comprueba el mensaje original y confirma el nuevo plazo.";
                    if(activity.due>0&&activity.due<now)activity.reason="Fecha pasada. "+activity.reason;
                    Finding f=new Finding();f.message=m;f.proposal=activity;f.key=m.reply+":0";
                    out.add(f);continue;
                }
            }
            Message closure=replies.get(m.id);''')
patch("MainActivity.java",
'String chatQuery="";boolean communitiesOnly=false;',
'String chatQuery="";int groupFilter=0;boolean communitiesOnly=false;')
patch("MainActivity.java",
'chatQuery=state.getString("chat_query","");communitiesOnly=state.getBoolean("communities_only",false);',
'chatQuery=state.getString("chat_query","");communitiesOnly=state.getBoolean("communities_only",false);groupFilter=Math.max(0,Math.min(4,state.getInt("group_filter",0)));')
patch("MainActivity.java",
'out.putString("chat_query",chatQuery);out.putBoolean("communities_only",communitiesOnly);',
'out.putString("chat_query",chatQuery);out.putBoolean("communities_only",communitiesOnly);out.putInt("group_filter",groupFilter);')
patch("MainActivity.java",
'        LinearLayout list=column();body.addView(list);fillChats(list,chats,chatQuery);',
'''        HorizontalScrollView filterScroll=new HorizontalScrollView(this);filterScroll.setHorizontalScrollBarEnabled(false);LinearLayout filterChips=row();
        String[] groupLabels={"Todos","Autorizados","Sin autorizar","Comunidades","Con historial"};
        for(int j=0;j<groupLabels.length;j++){
            final int selectedFilter=j;Button chip=button(groupLabels[j],()->{groupFilter=selectedFilter;chatLimit=40;render();});
            chip.setTextColor(j==groupFilter?0xffffffff:MUTED);
            chip.setBackground(rounded(j==groupFilter?GREEN:0xfff0f4fd,18));filterChips.addView(chip);
        }
        filterScroll.addView(filterChips);body.addView(filterScroll);gap(body,8);
        LinearLayout list=column();body.addView(list);fillChats(list,chats,chatQuery);''')
patch("MainActivity.java",
'if(communitiesOnly&&!chat.community&&chat.parent.isEmpty())continue;if(visible++>=chatLimit)continue;',
'''if(communitiesOnly&&!chat.community&&chat.parent.isEmpty())continue;
            if(groupFilter==1&&!chat.selected)continue;
            if(groupFilter==2&&(chat.selected||chat.community))continue;
            if(groupFilter==3&&!chat.community)continue;
            if(groupFilter==4&&(chat.community||Store.get(this).messageCount(chat.key)==0))continue;
            if(visible++>=chatLimit)continue;''')
patch("MainActivity.java",
'                if(!chat.scanState.isEmpty()){gap(c,6);c.addView(text(chat.scanState,12,MUTED,false));}',
'''                if(!chat.scanState.isEmpty()){gap(c,6);c.addView(text(chat.scanState,12,MUTED,false));}
                if(Store.get(this).messageCount(chat.key)>0)c.addView(text("Mensajes conservados: "+Store.get(this).messageCount(chat.key),12,MUTED,false));''')
patch("MainActivity.java",
'        actions.addView(text("Los eventos se añaden primero a Mensajes para revisarlos.',
'''        actions.addView(button("Diagnosticar enlaces del calendario",()->background(()->CalendarBridge.diagnostics(this))));
        actions.addView(text("El diagnóstico es de solo lectura; indica si un evento vinculado dejó de estar disponible y no crea duplicados. Si aparece un evento ausente, revísalo antes de reprogramar.",12,MUTED,false));
        actions.addView(text("Los eventos se añaden primero a Mensajes para revisarlos.''')
patch("CalendarBridge.java",
'    public static String sendAll(Context c){',
'''    /** Diagnóstico conservador, solo lectura: jamás recrea ni elimina eventos. */
    public static String diagnostics(Context c){
        if(!allowed(c))return "Concede permisos de lectura y escritura del calendario para comprobar los enlaces.";
        int linked=0,found=0,missing=0,waiting=0,mismatch=0,errors=0;
        for(Task t:Store.get(c).all()){
            if(t.done||!t.calendarEnabled||t.due<=0)continue;
            if(t.eventId<=0){waiting++;continue;}
            linked++;
            try(Cursor cur=c.getContentResolver().query(ContentUris.withAppendedId(CalendarContract.Events.CONTENT_URI,t.eventId),
                    new String[]{CalendarContract.Events._ID,CalendarContract.Events.CALENDAR_ID},null,null,null)){
                if(cur==null){errors++;continue;}
                if(!cur.moveToFirst()){missing++;continue;}
                found++;
                if(t.calendarId>0&&cur.getLong(1)!=t.calendarId)mismatch++;
            }catch(SecurityException|IllegalArgumentException e){errors++;}
        }
        return "Enlaces revisados: "+linked+" · Activos: "+found+" · Ausentes: "+missing+
                " · Sin enviar: "+waiting+" · Calendario diferente: "+mismatch+
                (errors>0?" · Sin comprobar: "+errors:"")+
                ". No se ha creado, modificado ni borrado ningún evento.";
    }
    public static String sendAll(Context c){''')
gradle=Path("AgendaClara/app/build.gradle");s=gradle.read_text(encoding="utf-8")
if s.count("versionCode 7")!=1 or s.count("versionName '1.4.0'")!=1:raise RuntimeError("Versión 1.4.0 no encontrada")
gradle.write_text(s.replace("versionCode 7","versionCode 8").replace("versionName '1.4.0'","versionName '1.5.0'"),encoding="utf-8")
print("Agenda Clara 1.5.0: filtros, cambios de fechas y diagnóstico no destructivo preparados.")
