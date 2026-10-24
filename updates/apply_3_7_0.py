#!/usr/bin/env python3
"""Agenda Clara 3.7: Google Calendar organizado por cuentas, calendarios desplegables,
y previsualización/importación seleccionada de eventos como sesiones de Mi horario."""
from pathlib import Path
root=Path('AgendaClara')
p=root/'app/src/main/java/pe/agendaclara/app'
f=p/'MainActivity.java';s=f.read_text(encoding='utf8')
def rep(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old))
 s=s.replace(old,new,1)
rep('final Set<AlertDialog> dialogs=new HashSet<>();final Set<Long> expandedProposals=new HashSet<>();final Set<String> expandedChatCards=new HashSet<>();',
    'final Set<AlertDialog> dialogs=new HashSet<>();final Set<Long> expandedProposals=new HashSet<>();final Set<String> expandedChatCards=new HashSet<>();final Set<String> expandedCalendarAccounts=new HashSet<>();final Set<Long> expandedCalendarIds=new HashSet<>();')
rep('expandedChatCards.addAll(state.getStringArrayList("expanded_chat_cards")!=null?state.getStringArrayList("expanded_chat_cards"):new ArrayList<>());',
    'expandedChatCards.addAll(state.getStringArrayList("expanded_chat_cards")!=null?state.getStringArrayList("expanded_chat_cards"):new ArrayList<>());expandedCalendarAccounts.addAll(state.getStringArrayList("expanded_calendar_accounts")!=null?state.getStringArrayList("expanded_calendar_accounts"):new ArrayList<>());for(long id:state.getLongArray("expanded_calendar_ids")!=null?state.getLongArray("expanded_calendar_ids"):new long[0])expandedCalendarIds.add(id);')
rep('out.putStringArrayList("expanded_chat_cards",new ArrayList<>(expandedChatCards));',
    'out.putStringArrayList("expanded_chat_cards",new ArrayList<>(expandedChatCards));out.putStringArrayList("expanded_calendar_accounts",new ArrayList<>(expandedCalendarAccounts));long[] expanded=new long[expandedCalendarIds.size()];int cx=0;for(Long id:expandedCalendarIds)expanded[cx++]=id;out.putLongArray("expanded_calendar_ids",expanded);')
start=s.index('    void calendarSettings(){');end=s.index('    void notificationsPermission(){',start)
replacement='''    /** Cada cuenta es un acordeón independiente: sin confundir calendarios de cuentas distintas. */
    void calendarSettings(){
        LinearLayout info=card(body);info.addView(text("Google Calendar · Por cuentas",20,INK,true));gap(info,8);
        info.addView(text("Los calendarios proceden de las cuentas sincronizadas en este Android. Pulsa una cuenta y después su calendario para desplegarlo.",13,MUTED,false));
        boolean allowed=CalendarBridge.allowed(this);
        info.addView(text(allowed?"● Calendario autorizado":"○ Requiere permiso de calendario",13,allowed?SUCCESS:RED,true));
        info.addView(button(allowed?"Actualizar cuentas y calendarios":"Conectar Google Calendar",this::chooseCalendar));
        if(!allowed){info.addView(text("Para ver calendarios de cada cuenta, concede permisos de lectura y escritura. Agenda Clara no solicita contraseñas de Google.",12,MUTED,false));return;}
        List<CalendarBridge.CalendarInfo> calendars;
        try{calendars=CalendarBridge.calendars(this);}catch(Exception error){info.addView(text("No se pudieron leer calendarios. Comprueba la sincronización de Android.",13,RED,false));return;}
        Map<String,List<CalendarBridge.CalendarInfo>> accounts=new LinkedHashMap<>();
        for(CalendarBridge.CalendarInfo k:calendars){String key=(k.google?"Google: ":"Android: ")+(k.account==null?"Cuenta sin nombre":k.account);
            accounts.computeIfAbsent(key,unused->new ArrayList<>()).add(k);}
        if(accounts.isEmpty()){
            LinearLayout missing=card(body);missing.addView(text("No se encontraron calendarios",17,INK,true));
            missing.addView(text("Añade una cuenta en Android y activa la sincronización del Calendario.",13,MUTED,false));
            missing.addView(button("Abrir cuentas de Android",()->safeStart(new Intent(Settings.ACTION_SYNC_SETTINGS))));
        }
        for(Map.Entry<String,List<CalendarBridge.CalendarInfo>> account:accounts.entrySet()){
            String key=account.getKey();List<CalendarBridge.CalendarInfo> members=account.getValue();
            LinearLayout card=card(body);card.setTag("calendar_account:"+key);
            LinearLayout heading=row();TextView arrow=text("›",22,GREEN,true);heading.addView(arrow,new LinearLayout.LayoutParams(dp(35),dp(42)));
            LinearLayout labels=column();labels.addView(text(key,16,INK,true));
            labels.addView(text(members.size()+(members.size()==1?" calendario":" calendarios"),12,MUTED,false));
            heading.addView(labels,new LinearLayout.LayoutParams(0,-2,1));card.addView(heading);
            LinearLayout inside=column();inside.setPadding(dp(6),dp(9),0,0);
            for(CalendarBridge.CalendarInfo cal:members)calendarAccountChild(inside,cal,key);
            card.addView(inside);boolean open=expandedCalendarAccounts.contains(key);inside.setVisibility(open?View.VISIBLE:View.GONE);arrow.setText(open?"⌃":"›");
            heading.setContentDescription("Desplegar cuenta "+key);
            heading.setOnClickListener(v->{boolean show=inside.getVisibility()!=View.VISIBLE;inside.setVisibility(show?View.VISIBLE:View.GONE);arrow.setText(show?"⌃":"›");
                if(show)expandedCalendarAccounts.add(key);else expandedCalendarAccounts.remove(key);});
        }
        LinearLayout actions=card(body);actions.addView(text("Importar y exportar",18,INK,true));
        actions.addView(text("Elige un calendario dentro de su cuenta para importar sus eventos como clases semanales de Mi horario. Antes de guardarlos se muestra una revisión.",12,MUTED,false));
        actions.addView(button("Revisar eventos como tareas",this::pickEvents));
        actions.addView(button("Exportar tareas vinculadas a Google Calendar",()->background(()->CalendarBridge.sendAll(this))));
        actions.addView(button("Comprobar enlaces con Google Calendar",()->background(()->CalendarBridge.diagnostics(this))));
        actions.addView(text("La importación de clases no modifica ni borra eventos de Google Calendar. Los cambios remotos dependen de la sincronización de Android.",12,MUTED,false));
        info.addView(text("Destino actual para tareas: "+Prefs.get(this).getString("calendar_name","Sin elegir"),12,GREEN,true));
    }
    void calendarAccountChild(LinearLayout container,CalendarBridge.CalendarInfo calendar,String account){
        LinearLayout item=card(container);item.setTag("calendar:"+calendar.id);
        LinearLayout head=row();TextView arrow=text("›",19,GREEN,true);head.addView(arrow,new LinearLayout.LayoutParams(dp(30),dp(40)));
        LinearLayout summary=column();summary.addView(text(calendar.name,15,INK,true));summary.addView(text(calendar.writable?"Puede recibir tareas":"Solo lectura",11,MUTED,false));
        head.addView(summary,new LinearLayout.LayoutParams(0,-2,1));item.addView(head);
        LinearLayout details=column();details.setPadding(dp(4),dp(6),dp(4),dp(6));
        CheckBox selected=new CheckBox(this);selected.setText("Incluir en revisión de eventos");selected.setTextColor(INK);
        selected.setChecked(Prefs.calendars(this).contains(""+calendar.id));
        selected.setOnCheckedChangeListener((v,on)->Prefs.selectCalendar(this,calendar.id,on));details.addView(selected);
        details.addView(button("Ver eventos y exportar a Mi horario",()->previewCalendarSchedule(calendar)));
        if(calendar.writable)details.addView(button(Prefs.calendar(this)==calendar.id?"✓ Destino actual de tareas":"Usar como destino de tareas",()->{
            Prefs.get(this).edit().putLong("calendar",calendar.id).putString("calendar_name",calendar.name+" · "+calendar.account).apply();
            Prefs.selectCalendar(this,calendar.id,true);toast("Destino actualizado: "+calendar.name);render();}));
        item.addView(details);boolean open=expandedCalendarIds.contains(calendar.id);details.setVisibility(open?View.VISIBLE:View.GONE);arrow.setText(open?"⌃":"›");
        head.setContentDescription("Desplegar calendario "+calendar.name+" de "+account);
        head.setOnClickListener(v->{boolean show=details.getVisibility()!=View.VISIBLE;details.setVisibility(show?View.VISIBLE:View.GONE);arrow.setText(show?"⌃":"›");
            if(show)expandedCalendarIds.add(calendar.id);else expandedCalendarIds.remove(calendar.id);});
    }
    void previewCalendarSchedule(CalendarBridge.CalendarInfo calendar){
        if(!CalendarBridge.allowed(this)){chooseCalendar();return;}
        toast("Leyendo eventos del calendario…");
        new Thread(()->{
            try{
                // Solo consulta al proveedor del calendario Android. No se transfieren contraseñas.
                List<CalendarBridge.Event> events=CalendarBridge.events(this,calendar.id);
                List<CalendarScheduleImport.Group> groups=CalendarScheduleImport.groups(events,java.time.ZoneId.systemDefault());
                runOnUiThread(()->{if(isFinishing()||isDestroyed())return;showCalendarSchedulePreview(calendar,groups);});
            }catch(Exception error){runOnUiThread(()->toast("No se pudieron leer eventos de esta cuenta."));}
        },"read-calendar-schedule").start();
    }
    void showCalendarSchedulePreview(CalendarBridge.CalendarInfo calendar,List<CalendarScheduleImport.Group> groups){
        if(groups.isEmpty()){
            dialogBuilder().setTitle("Sin clases importables").setMessage("No hay eventos con horas compatibles con clases semanales entre los eventos disponibles. Los eventos de día completo o demasiado largos se omiten. Revisa la sincronización de la cuenta.").setPositiveButton("Entendido",null).show();return;
        }
        boolean[] marked=new boolean[groups.size()];
        String[] labels=new String[groups.size()];
        for(int i=0;i<groups.size();i++){CalendarScheduleImport.Group group=groups.get(i);
            StringBuilder days=new StringBuilder();for(ScheduleEntry entry:group.sessions){if(days.length()>0)days.append(", ");days.append(ScheduleEntry.dayName(entry.day)).append(" ").append(ScheduleEntry.clock(entry.start));}
            labels[i]=group.name+" · "+group.sessions.size()+" día(s)\n"+days;
        }
        dialogBuilder().setTitle("Importar horario de "+calendar.name)
            .setMultiChoiceItems(labels,marked,(d,i,on)->marked[i]=on)
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("Revisar importación",(d,w)->{
                ArrayList<ScheduleEntry> picked=new ArrayList<>();
                for(int i=0;i<marked.length;i++)if(marked[i])for(ScheduleEntry entry:groups.get(i).sessions)picked.add(entry.copy());
                if(picked.isEmpty()){toast("Selecciona al menos un curso.");return;}
                int existing=0;List<ScheduleEntry> saved=ScheduleDatabase.get(this).all();
                for(ScheduleEntry candidate:picked)for(ScheduleEntry old:saved){
                    if(old.day==candidate.day&&old.start==candidate.start&&old.end==candidate.end&&ScheduleCourseColors.same(old.course,candidate.course)){existing++;break;}}
                final int duplicates=existing;final int total=picked.size();
                dialogBuilder().setTitle("Confirmar horario importado")
                    .setMessage("Cuenta: "+calendar.account+"\nCalendario: "+calendar.name+"\nBloques propuestos: "+total+"\nPosibles duplicados: "+duplicates+".\n\nSe importarán como clases SEMANALES en Mi horario. Revisa los días, horas, y fecha de fin del semestre después de importarlos. No se editarán los eventos de Google Calendar.")
                    .setNegativeButton("Volver",null).setPositiveButton("Importar clases",(agree,which)->{
                        new Thread(()->{
                            ScheduleDatabase db=ScheduleDatabase.get(this);int count=db.importReviewed(picked);ScheduleReminders.rebuild(this);
                            runOnUiThread(()->toast(count+" clase(s) importadas a Mi horario. Revisa tu calendario."));
                        },"import-calendar-classes").start();
                    }).show();
            }).show();
    }
'''
s=s[:start]+replacement+s[end:]
f.write_text(s,encoding='utf8')
# New helper: deterministic grouping of occurrences and no unrequested all-day conversions.
(p/'CalendarScheduleImport.java').write_text('''package pe.agendaclara.app;
import java.time.*;
import java.util.*;
/** Converts selected timed CalendarContract event instances into weekly sessions.
 * A group is a course title, containing one independent block for each day and time.
 * Duplicate weekly occurrences stay one session; different times remain distinct.
 */
public final class CalendarScheduleImport {
  private CalendarScheduleImport(){}
  public static final class Group {
    public String name;
    public final List<ScheduleEntry> sessions=new ArrayList<>();
    Group(String title){name=title;}
  }
  public static List<Group> groups(Collection<CalendarBridge.Event> events,ZoneId zone){
    Map<String,Group> grouped=new LinkedHashMap<>();
    Map<String,Set<String>> sessionKeys=new HashMap<>();
    if(events==null)return new ArrayList<>();
    for(CalendarBridge.Event e:events){
      if(e==null||e.allDay||e.title==null||e.title.trim().isEmpty()||e.end<=e.start)continue;
      ZonedDateTime begin=Instant.ofEpochMilli(e.start).atZone(zone);
      ZonedDateTime finish=Instant.ofEpochMilli(e.end).atZone(zone);
      if(!begin.toLocalDate().equals(finish.toLocalDate()))continue;
      int start=begin.getHour()*60+begin.getMinute(),end=finish.getHour()*60+finish.getMinute();
      if(end<=start||end-start>720)continue;
      String key=ScheduleCourseColors.identity(e.title);
      if(key.isEmpty())continue;
      int day=begin.getDayOfWeek().getValue();
      String signature=day+":"+start+":"+end;
      Set<String> seen=sessionKeys.computeIfAbsent(key,unused->new HashSet<>());
      if(!seen.add(signature))continue;
      Group group=grouped.computeIfAbsent(key,unused->new Group(e.title.trim()));
      ScheduleEntry item=new ScheduleEntry();item.id=0;item.course=group.name;item.day=day;item.start=start;item.end=end;
      item.room=e.location==null?"":e.location.trim();
      if(item.room.length()>140)item.room=item.room.substring(0,140);
      item.notes="Importado de Google Calendar";item.color=ScheduleCourseColors.deterministic(item.course);
      item.reminder=10;
      if(ScheduleEntry.valid(item))group.sessions.add(item);
    }
    ArrayList<Group> out=new ArrayList<>(grouped.values());
    for(Group group:out)group.sessions.sort(Comparator.comparingInt((ScheduleEntry it)->it.day).thenComparingInt(it->it.start));
    return out;
  }
}
''',encoding='utf8')
# Preserve provider location when importing.
f=p/'CalendarBridge.java';b=f.read_text(encoding='utf8')
old='public long id,start,end,calendarId;public String title,notes,calendarName="";public boolean allDay;'
assert b.count(old)==1
b=b.replace(old,'public long id,start,end,calendarId;public String title,notes,calendarName="",location="";public boolean allDay;')
old='new String[]{"event_id","title","begin","end","description","allDay"}'
assert b.count(old)==1
b=b.replace(old,'new String[]{"event_id","title","begin","end","description","allDay","eventLocation"}')
old='e.allDay=cur.getInt(5)!=0;out.add(e);'
assert b.count(old)==1
b=b.replace(old,'e.allDay=cur.getInt(5)!=0;e.location=cur.getString(6)==null?"":cur.getString(6);out.add(e);')
f.write_text(b,encoding='utf8')
f=root/'app/build.gradle';g=f.read_text(encoding='utf8');assert 'versionCode 26' in g and "versionName '3.6.0'" in g;f.write_text(g.replace('versionCode 26','versionCode 27').replace("versionName '3.6.0'","versionName '3.7.0'"),encoding='utf8')
print('PASS: Agenda 3.7 cuentas desplegables, calendarios desplegables, vistas previas y conversión a clases. ')