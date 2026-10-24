#!/usr/bin/env python3
"""Agenda Clara 3.6: hierarchical expanders + explicit group/individual discovery."""
from pathlib import Path
root=Path('AgendaClara')
src=root/'app/src/main/java/pe/agendaclara/app'
p=src/'MainActivity.java'
s=p.read_text(encoding='utf-8')
def sub(old,new):
 global s
 count=s.count(old)
 if count!=1:raise RuntimeError(f'MainActivity anchor {count}: {old[:100]!r}')
 s=s.replace(old,new,1)
sub('final Set<AlertDialog> dialogs=new HashSet<>();final Set<Long> expandedProposals=new HashSet<>();',
    'final Set<AlertDialog> dialogs=new HashSet<>();final Set<Long> expandedProposals=new HashSet<>();final Set<String> expandedChatCards=new HashSet<>();')
sub('groupFilter=Math.max(0,Math.min(4,state.getInt("group_filter",0)));',
    'groupFilter=Math.max(0,Math.min(6,state.getInt("group_filter",0)));expandedChatCards.addAll(state.getStringArrayList("expanded_chat_cards")!=null?state.getStringArrayList("expanded_chat_cards"):new ArrayList<>());')
sub('out.putInt("group_filter",groupFilter);',
    'out.putInt("group_filter",groupFilter);out.putStringArrayList("expanded_chat_cards",new ArrayList<>(expandedChatCards));')
sub('''        if(chat.community){chatQuery=chat.title;chatLimit=40;render();toast("Elige los grupos de esta comunidad que quieres leer.");return;}''',
'''        if(chat.community){toast("Despliega la comunidad y selecciona uno de sus grupos.");return;}
        final boolean notificationChat=chat.jid.isEmpty();
        final String kind=chat.group?"grupo":"chat individual";''')
sub('''        if(chat.selected){consentDialog=dialogBuilder().setTitle("Dejar de leer este grupo").setMessage("Se quitarán los mensajes y propuestas de "+chat.title+" guardados por esta conexión. Tus tareas se conservarán.").setNegativeButton("Volver",null).setPositiveButton("Revocar lectura",(d,w)->{for(long id:Store.get(this).revokeReading(chat.key))Reminders.cancelProposal(this,id);session("consent",null);render();}).show();return;}''',
'''        if(chat.selected){consentDialog=dialogBuilder().setTitle("Revocar lectura de "+kind).setMessage("Se quitarán los mensajes y propuestas locales asociados a "+chat.title+". Tus tareas se conservarán.").setNegativeButton("Volver",null).setPositiveButton("Revocar lectura",(d,w)->{for(long id:Store.get(this).revokeReading(chat.key))Reminders.cancelProposal(this,id);if(!notificationChat)session("consent",null);render();}).show();return;}''')
sub('''        if(!chat.joined){toast("WhatsApp muestra este subgrupo en la comunidad, pero no figura entre tus grupos con acceso. Únete desde WhatsApp y actualiza.");return;}''',
'''        if(!notificationChat&&!chat.joined){toast("WhatsApp muestra este subgrupo, pero no confirma acceso. Únete desde WhatsApp y actualiza.");return;}
        if(notificationChat){
            consentDialog=dialogBuilder().setTitle("Autorizar "+kind+": "+chat.title)
                .setMessage("Se interpretarán solamente los mensajes NUEVOS que Android entregue mediante notificaciones de este chat y únicamente después de autorizarlo. No se obtiene el historial ni la lista completa de WhatsApp. El permiso del sistema para notificaciones es amplio; solo se guarda el contenido de chats seleccionados. Puedes revocarlo.")
                .setNegativeButton("Cancelar",null).setPositiveButton("Autorizar",(d,w)->{
                    Store.get(this).selectChat(chat.key,true);
                    Prefs.get(this).edit().putBoolean("discover",true).putBoolean("capture",true).putLong("capture_since",System.currentTimeMillis()).apply();
                    if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                    sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));render();
                }).show();return;
        }''')
sub('''        List<Store.Chat> all=Store.get(this).chats(),chats=new ArrayList<>();int selected=0;for(Store.Chat c:all)if(!c.jid.isEmpty()){chats.add(c);if(c.selected)selected++;}''',
'''        List<Store.Chat> all=Store.get(this).chats(),chats=new ArrayList<>(all);int selected=0;for(Store.Chat c:chats)if(c.selected)selected++;''')
sub('''        subtitle(body,"Mis grupos · "+selected+" autorizados");
        EditText search=input("Buscar comunidad o grupo",chatQuery,android.text.InputType.TYPE_CLASS_TEXT);''',
'''        subtitle(body,"Comunidades, grupos y chats · "+selected+" autorizados");
        body.addView(text("Abre una comunidad para ver sus grupos. Los chats individuales se identifican cuando Android notifica una conversación y autorizas su detección. La lista no representa todo tu WhatsApp.",12,MUTED,false));gap(body,9);
        EditText search=input("Buscar comunidad, grupo o chat",chatQuery,android.text.InputType.TYPE_CLASS_TEXT);''')
sub('''        LinearLayout filters=row();filters.addView(button(communitiesOnly?"Ver todos":"Solo comunidades",()->{communitiesOnly=!communitiesOnly;chatLimit=40;render();}),new LinearLayout.LayoutParams(0,-2,1));filters.addView(button("Revisar propuestas",()->{page=2;render();}),new LinearLayout.LayoutParams(0,-2,1));body.addView(filters);gap(body,10);''',
'''        LinearLayout filters=row();filters.addView(button("Actualizar",()->{if(Prefs.get(this).getBoolean("wa_linked",false))session("groups",null);if(notificationAccess())sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));render();}),new LinearLayout.LayoutParams(0,-2,1));filters.addView(button("Revisar propuestas",()->{page=2;render();}),new LinearLayout.LayoutParams(0,-2,1));body.addView(filters);gap(body,10);''')
sub('''        String[] groupLabels={"Todos","Autorizados","Sin autorizar","Comunidades","Con historial"};''',
'''        String[] groupLabels={"Todos","Comunidades","Grupos","Individuales","Autorizados","Pendientes","Con historial"};''')
sub('''        List<Store.Chat> detected=new ArrayList<>();for(Store.Chat c:all)if(c.jid.isEmpty())detected.add(c);
        if(!detected.isEmpty()){Switch capture=new Switch(this);capture.setText("Leer notificaciones de chats marcados");capture.setMinHeight(dp(52));capture.setChecked(prefs.getBoolean("capture",false));capture.setOnCheckedChangeListener((v,on)->prefs.edit().putBoolean("capture",on).putLong("capture_since",System.currentTimeMillis()).apply());legacy.addView(capture);for(Store.Chat c:detected){CheckBox check=new CheckBox(this);check.setText(c.title);check.setChecked(c.selected);check.setOnCheckedChangeListener((v,on)->Store.get(this).selectChat(c.key,on));legacy.addView(check);}}''',
'''        Switch capture=new Switch(this);capture.setText("Reconocer grupos y chats individuales desde notificaciones");capture.setTextColor(INK);capture.setMinHeight(dp(52));capture.setChecked(prefs.getBoolean("discover",false));
        capture.setOnCheckedChangeListener((v,on)->{
            prefs.edit().putBoolean("discover",on).putBoolean("capture",on).putLong("capture_since",System.currentTimeMillis()).apply();
            if(on){if(!notificationAccess())safeStart(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));else sendBroadcast(new Intent(WhatsAppListener.REFRESH).setPackage(getPackageName()));}
        });legacy.addView(capture);
        legacy.addView(text("La detección por notificaciones solo ofrece conversaciones visibles para Android, no un inventario de chats. Toca cada tarjeta para autorizar su lectura.",12,MUTED,false));''')
start=s.index('    void fillChats(LinearLayout list,List<Store.Chat> chats,String query){')
end=s.index('    void importHistory(Store.Chat chat){',start)
new=r'''    boolean isChatGroup(Store.Chat chat){return chat.group||(!chat.community&&!chat.jid.isEmpty());}
    boolean matchesConnectionFilter(Store.Chat chat){
        switch(groupFilter){
            case 1:return chat.community;
            case 2:return !chat.community&&isChatGroup(chat);
            case 3:return !chat.community&&!isChatGroup(chat);
            case 4:return !chat.community&&chat.selected;
            case 5:return !chat.community&&!chat.selected;
            case 6:return !chat.community&&Store.get(this).messageCount(chat.key)>0;
            default:return true;
        }
    }
    boolean matchesConnectionSearch(Store.Chat chat,String q,Map<String,Store.Chat> parents){
        if(q.isEmpty())return true;
        String name=chat.title==null?"":chat.title.toLowerCase(Locale.ROOT);
        Store.Chat parent=parents.get(chat.parent);
        return name.contains(q)||(parent!=null&&parent.title.toLowerCase(Locale.ROOT).contains(q));
    }
    void fillChats(LinearLayout list,List<Store.Chat> chats,String query){
        list.removeAllViews();
        String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);
        Map<String,Store.Chat> parents=new LinkedHashMap<>();
        for(Store.Chat chat:chats)if(chat.community&&!chat.jid.isEmpty())parents.put(chat.jid,chat);
        Map<String,List<Store.Chat>> children=new HashMap<>();
        for(Store.Chat chat:chats)if(!chat.community&&parents.containsKey(chat.parent))
            children.computeIfAbsent(chat.parent,k->new ArrayList<>()).add(chat);
        List<Store.Chat> sorted=new ArrayList<>(chats);
        sorted.sort((a,b)->{if(a.community!=b.community)return a.community?-1:1;
            if(a.selected!=b.selected)return a.selected?-1:1;
            return a.title.compareToIgnoreCase(b.title);});
        int visible=0,remaining=0;
        boolean tree=groupFilter==0||groupFilter==1;
        for(Store.Chat chat:sorted){
            boolean isNested=!chat.community&&parents.containsKey(chat.parent);
            if(tree&&isNested)continue;
            if(!matchesConnectionFilter(chat))continue;
            
            if(!matchesConnectionSearch(chat,q,parents)){
                if(!chat.community||!tree)continue;
                boolean childMatch=false;
                for(Store.Chat child:children.getOrDefault(chat.jid,Collections.emptyList()))
                    if(matchesConnectionSearch(child,q,Collections.emptyMap())){childMatch=true;break;}
                if(!childMatch)continue;
            }
            if(visible++>=chatLimit){remaining++;continue;}
            if(chat.community&&tree){
                List<Store.Chat> groupChildren=children.getOrDefault(chat.jid,Collections.emptyList());
                LinearLayout parent=card(list);parent.setTag("community:"+chat.key);
                parent.setPadding(dp(15),dp(13),dp(15),dp(13));
                LinearLayout heading=row();TextView arrow=text("⌄",24,GREEN,true);
                heading.addView(arrow,new LinearLayout.LayoutParams(dp(38),dp(44)));
                LinearLayout labels=column();labels.addView(text(chat.title,17,INK,true));
                labels.addView(text("COMUNIDAD · "+groupChildren.size()+" grupos",11,GREEN,true));
                heading.addView(labels,new LinearLayout.LayoutParams(0,-2,1));parent.addView(heading);
                LinearLayout inner=column();inner.setPadding(dp(9),dp(8),0,0);
                List<Store.Chat> groupSorted=new ArrayList<>(groupChildren);
                groupSorted.sort((a,b)->a.title.compareToIgnoreCase(b.title));
                int shown=0;
                for(Store.Chat child:groupSorted)if(q.isEmpty()||matchesConnectionSearch(child,q,parents)){
                    addConnectionCard(inner,child,chat.title);shown++;
                }
                if(shown==0)inner.addView(text("No hay subgrupos disponibles con ese filtro. Actualiza desde WhatsApp.",12,MUTED,false));
                parent.addView(inner);
                boolean open=expandedChatCards.contains(chat.key)||!q.isEmpty();
                inner.setVisibility(open?View.VISIBLE:View.GONE);arrow.setText(open?"⌃":"›");
                heading.setOnClickListener(v->{boolean expanded=inner.getVisibility()!=View.VISIBLE;
                    inner.setVisibility(expanded?View.VISIBLE:View.GONE);arrow.setText(expanded?"⌃":"›");
                    if(expanded)expandedChatCards.add(chat.key);else expandedChatCards.remove(chat.key);});
                parent.setOnClickListener(v->heading.performClick());
                heading.setContentDescription("Desplegar comunidad "+chat.title);
            }else addConnectionCard(list,chat,parents.containsKey(chat.parent)?parents.get(chat.parent).title:null);
        }
        if(remaining>0)list.addView(button("Ver "+Math.min(40,remaining)+" conversaciones más",()->{
            chatLimit+=40;fillChats(list,chats,query);
        }));
        if(visible==0){LinearLayout empty=card(list);
            empty.addView(text(chats.isEmpty()?"Aún no hay conversaciones detectadas":"Sin coincidencias",18,INK,true));
            empty.addView(text(chats.isEmpty()?"Vincula WhatsApp para obtener grupos compatibles o activa la detección por notificaciones para descubrir conversaciones nuevas.":"Modifica el filtro o escribe otro nombre.",13,MUTED,false));
        }
    }
    void addConnectionCard(LinearLayout container,Store.Chat chat,String parent){
        boolean nativeChat=!chat.jid.isEmpty();boolean group=isChatGroup(chat);
        LinearLayout card=card(container);card.setTag("chat:"+chat.key);
        card.setBackground(outlined(chat.selected?0xfff0f5ff:0xffffffff,18,chat.selected?0xffbed2ff:STROKE));
        card.setPadding(dp(14),dp(12),dp(14),dp(12));
        LinearLayout heading=row();TextView arrow=text("›",22,GREEN,true);
        heading.addView(arrow,new LinearLayout.LayoutParams(dp(34),dp(42)));
        LinearLayout labels=column();labels.addView(text(chat.title,16,INK,true));
        String type=group?"GRUPO":"CHAT INDIVIDUAL";
        String origin=nativeChat?" · VINCULADO":" · NOTIFICACIONES";
        labels.addView(text(type+origin,10,GREEN,true));
        if(parent!=null)labels.addView(text("Comunidad: "+parent,11,MUTED,false));
        heading.addView(labels,new LinearLayout.LayoutParams(0,-2,1));card.addView(heading);
        LinearLayout details=column();details.setPadding(dp(6),dp(7),dp(6),dp(6));
        details.addView(text(chat.selected?"✓ Lectura autorizada":nativeChat&&!chat.joined?"Acceso al subgrupo sin confirmar":"Lectura pendiente de autorización",12,MUTED,false));
        if(!chat.scanState.isEmpty())details.addView(text(chat.scanState,12,MUTED,false));
        int saved=Store.get(this).messageCount(chat.key);
        if(saved>0)details.addView(text("Mensajes almacenados: "+saved,12,MUTED,false));
        details.addView(button(chat.selected?"Revocar lectura":"Autorizar lectura",()->chooseGroup(chat)));
        if(chat.selected){
            if(nativeChat){
                details.addView(button("Revisar historial sincronizado",()->session("history",chat.jid)));
                details.addView(button("Mensajes anteriores · "+HistoryPageOptions.saved(Prefs.get(this).getInt("wa_history_count",50)),()->chooseHistoryCount(chat)));
            }
            details.addView(button("Importar conversación .txt",()->importHistory(chat)));
        }
        if(!nativeChat)details.addView(text("Solo notificaciones observadas; no incluye chats que aún no hayan notificado.",11,MUTED,false));
        card.addView(details);
        boolean open=expandedChatCards.contains(chat.key);
        details.setVisibility(open?View.VISIBLE:View.GONE);arrow.setText(open?"⌃":"›");
        heading.setOnClickListener(v->{boolean expanding=details.getVisibility()!=View.VISIBLE;
            details.setVisibility(expanding?View.VISIBLE:View.GONE);arrow.setText(expanding?"⌃":"›");
            if(expanding)expandedChatCards.add(chat.key);else expandedChatCards.remove(chat.key);
        });
        card.setOnClickListener(v->heading.performClick());
        heading.setContentDescription((open?"Contraer ":"Desplegar ")+chat.title);
    }
'''
s=s[:start]+new+s[end:]
# History import for authorized conversations irrespective of native pairing. Imported text requires selected consent.
sub('''        if(!Prefs.get(this).getBoolean("wa_reading",false)){toast("Activa la lectura antes de interpretar un archivo de este grupo.");return;}''',
'''        if(!chat.selected){toast("Autoriza primero la lectura de esta conversación.");return;}''')
sub('''if(chat==null||!chat.selected||!Prefs.get(this).getBoolean("wa_reading",false)){toast("El grupo ya no tiene permiso de lectura.");return;}''',
'''if(chat==null||!chat.selected){toast("La conversación ya no tiene permiso de lectura.");return;}''')
p.write_text(s,encoding='utf-8')
# Support explicitly imported .txt from a selected individual notification-based chat.
p=src/'MainActivity.java';s=p.read_text(encoding='utf-8')
needle='for(ConversationAnalyzer.Message m:messages)if(m.time>=cutoff&&m.time<=System.currentTimeMillis()+60000L&&Store.get(this).recordMessage(key,m))stored++;'
assert s.count(needle)==1
s=s.replace(needle,'for(ConversationAnalyzer.Message m:messages)if(m.time>=cutoff&&m.time<=System.currentTimeMillis()+60000L&&(chat.jid.isEmpty()?Store.get(this).recordImportedMessage(key,m):Store.get(this).recordMessage(key,m)))stored++;',1)
needle='int count=ReviewFlow.analyzeLinked(this,key,true,"");'
assert s.count(needle)==1
s=s.replace(needle,'int count=chat.jid.isEmpty()?ReviewFlow.analyzeImported(this,key):ReviewFlow.analyzeLinked(this,key,true,"");',1)
p.write_text(s,encoding='utf-8')
p=src/'Store.java';s=p.read_text(encoding='utf-8')
needle='    public synchronized boolean recordMessage(String key,ConversationAnalyzer.Message m){'
assert s.count(needle)==1
s=s.replace(needle,'''    public synchronized boolean recordMessage(String key,ConversationAnalyzer.Message m){return saveMessageWithScope(key,m,false);}
    /** Manual import of a selected conversation; never used by passive notification scanning. */
    public synchronized boolean recordImportedMessage(String key,ConversationAnalyzer.Message m){return saveMessageWithScope(key,m,true);}
    private synchronized boolean saveMessageWithScope(String key,ConversationAnalyzer.Message m,boolean explicitImport){''',1)
needle='if(chat==null||!chat.selected||chat.jid.isEmpty()||!Prefs.get(context).getBoolean("wa_reading",false))return false;'
assert s.count(needle)==1
s=s.replace(needle,'if(chat==null||!chat.selected||(!explicitImport&&(chat.jid.isEmpty()||!Prefs.get(context).getBoolean("wa_reading",false))))return false;',1)
p.write_text(s,encoding='utf-8')
p=src/'ReviewFlow.java';s=p.read_text(encoding='utf-8')
needle='    /** Linked history is explicitly authorized by chat selection; live notification guards remain separate. */'
assert s.count(needle)==1
method='''    /** User-chosen .txt import for a selected notification-based individual or group chat. */
    public static int analyzeImported(Context context,String chatKey){
        Store db=Store.get(context);Store.Chat chat=db.getChat(chatKey);
        if(chat==null||!chat.selected)return 0;
        db.trimMessages(chatKey,Prefs.get(context).getInt("wa_history_days",30));
        List<ConversationAnalyzer.Message> messages=db.messages(chatKey,4000);
        List<ConversationAnalyzer.Finding> findings=ConversationAnalyzer.analyze(messages,ZoneId.systemDefault(),System.currentTimeMillis());
        int created=0;
        for(ConversationAnalyzer.Finding finding:findings){
            Store.Chat current=db.getChat(chatKey);if(current==null||!current.selected)break;
            if(db.offerLinked(finding,current,true)>0)created++;
        }
        changed(context);return created;
    }
'''
s=s.replace(needle,method+needle,1)
p.write_text(s,encoding='utf-8')
listener=src/'WhatsAppListener.java'
x=listener.read_text(encoding='utf-8')
old='return !Prefs.get(this).getBoolean("wa_reading",false)&&Prefs.get(this).getBoolean("discover",Prefs.get(this).getBoolean("capture",false));'
assert x.count(old)==1
x=x.replace(old,'return Prefs.get(this).getBoolean("discover",Prefs.get(this).getBoolean("capture",false));')
listener.write_text(x,encoding='utf-8')
# Version bump; original source 3.5.0.
gradle=root/'app/build.gradle';g=gradle.read_text(encoding='utf-8')
assert g.count('versionCode 25')==1 and g.count("versionName '3.5.0'")==1
gradle.write_text(g.replace('versionCode 25','versionCode 26').replace("versionName '3.5.0'","versionName '3.6.0'"),encoding='utf-8')
print('PASS 3.6: comunidades desplegables, grupos, chats individuales de notificaciones, permisos individuales')