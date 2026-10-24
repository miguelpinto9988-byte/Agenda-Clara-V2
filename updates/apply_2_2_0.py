#!/usr/bin/env python3
"""Agenda Clara 2.2.0: modular filtering, searchable proposal inbox, low-motion UI."""
from pathlib import Path

directory=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
mainfile=directory/"MainActivity.java"
s=mainfile.read_text(encoding="utf-8")

def replace(old,new):
    global s
    occurrences=s.count(old)
    if occurrences!=1:
        raise RuntimeError("Expect 1 occurrence, got %d of %r"%(occurrences,old[:110]))
    s=s.replace(old,new,1)

for name in ("AgendaFilters.java","ReviewFilters.java","UiMotion.java"):
    (directory/name).write_bytes((Path("updates/phase6")/name).read_bytes())

replace('String pendingHistoryChat="";ScrollView contentScroll;',
'''String reviewQuery="";int reviewFilter=0;Runnable reviewSearchTask;LinearLayout reviewList;TextView reviewCount;
    String pendingHistoryChat="";ScrollView contentScroll;''')
replace('filter=state.getInt("filter");categoryFilter=',
'filter=state.getInt("filter");reviewFilter=Math.max(0,Math.min(4,state.getInt("review_filter",0)));reviewQuery=state.getString("review_query","");categoryFilter=')
replace('out.putInt("filter",filter);out.putInt("category_filter",categoryFilter);',
'out.putInt("filter",filter);out.putInt("review_filter",reviewFilter);out.putString("review_query",reviewQuery);out.putInt("category_filter",categoryFilter);')
replace('if(taskSearch!=null)handler.removeCallbacks(taskSearch);if(groupSearch!=null)handler.removeCallbacks(groupSearch);',
'if(taskSearch!=null)handler.removeCallbacks(taskSearch);if(groupSearch!=null)handler.removeCallbacks(groupSearch);if(reviewSearchTask!=null)handler.removeCallbacks(reviewSearchTask);')
replace('body.removeAllViews();if(page==0)tasksPage();else if(page==1)calendarPage();else if(page==2)messagesPage();else settingsPage();',
'body.removeAllViews();if(page==0)tasksPage();else if(page==1)calendarPage();else if(page==2)messagesPage();else settingsPage();if(!samePage)UiMotion.reveal(body);')
replace('        EditText search=input("Buscar en tus tareas",query,android.text.InputType.TYPE_CLASS_TEXT);search.setTag("task_search");',
'        EditText search=input("Buscar en tus tareas",query,android.text.InputType.TYPE_CLASS_TEXT);search.setContentDescription("Buscar tareas por título, notas o fuente, con o sin tilde");search.setTag("task_search");')
replace('            Button b=button(label,()->{categoryFilter=chosen;taskLimit=24;render();});',
'            Button b=button(label,()->{categoryFilter=chosen;taskLimit=24;render();});b.setContentDescription("Categoría "+label+(chosen==categoryFilter?", seleccionada":""));')
replace('            Button b=button(names[j],()->{filter=k;render();});',
'            Button b=button(names[j],()->{filter=k;render();});b.setContentDescription("Filtro "+names[j]+(j==filter?", seleccionado":""));')

start=s.index('    void fillTasks(List<Task> all,LocalDate date){')
end=s.index('    void taskCard(',start)
method=s[start:end]
a=method.index('            String status=TaskLogic.status(t,now);')
b=method.index('            if(count<taskLimit)',a)
method=method[:a]+'''            if(!AgendaFilters.matches(t,filter,categoryFilter,query,date,now))continue;
'''+method[b:]
s=s[:start]+method+s[end:]

start=s.index('    void messagesPage(){')
end=s.index('    void importText(',start)
block=s[start:end]
key='        List<Store.Inbox> inbox=Store.get(this).inbox();subtitle(body,"Propuestas pendientes · "+inbox.size());\n'
if block.count(key)!=1:raise RuntimeError("Inbox extraction anchor not found")
head,tail=block.split(key)
close='    }\n'
if not tail.endswith(close):raise RuntimeError("Unexpected closing brace in review page")
tail=tail[:-len(close)]
if tail.count('card(body)')!=2:raise RuntimeError("Review cards changed unexpectedly")
tail=tail.replace('card(body)','card(reviewList)')
tail=tail.replace('body.addView(button("Ver más propuestas"','reviewList.addView(button("Ver más propuestas"')
tail=tail.replace('"Tu bandeja está al día"','(all.size()==0?"Tu bandeja está al día":"No hay propuestas con este filtro")')
tail=tail.replace('c.setTag("proposal:"+p.id);','c.setTag("proposal:"+p.id);c.setContentDescription("Propuesta pendiente: "+p.title);')
tail=tail.replace('c.addView(text(p.title,18,INK,true));',
'''if(p.dateKnown&&p.due>0&&p.due<System.currentTimeMillis()){
                TextView caution=text("●  PLAZO VENCIDO · CONFIRMA LA FECHA",11,RED,true);
                caution.setPadding(dp(8),dp(6),dp(8),dp(6));caution.setBackground(rounded(0xffffeeee,12));c.addView(caution);gap(c,6);
            }
            c.addView(text(p.title,18,INK,true));''')
tail=tail.replace('c.addView(button("Ver mensaje original",()->{boolean show=original.getVisibility()!=View.VISIBLE;if(show)expandedProposals.add(p.id);else expandedProposals.remove(p.id);original.setVisibility(show?View.VISIBLE:View.GONE);}));',
'''Button expand=button(expandedProposals.contains(p.id)?"Ocultar mensaje original":"Ver mensaje original",()->{boolean show=original.getVisibility()!=View.VISIBLE;if(show)expandedProposals.add(p.id);else expandedProposals.remove(p.id);original.setVisibility(show?View.VISIBLE:View.GONE);});
            expand.setContentDescription("Expandir u ocultar mensaje original de: "+p.title);c.addView(expand);''')
# The proposal cards are rendered without side effects: users still explicitly confirm with Agregar.
newheader='''        List<Store.Inbox> inbox=Store.get(this).inbox();
        reviewCount=text("",15,INK,true);body.addView(reviewCount);gap(body,8);
        EditText search=input("Buscar propuestas o mensajes",reviewQuery,android.text.InputType.TYPE_CLASS_TEXT);
        search.setTag("review_search");search.setSingleLine(true);
        search.setContentDescription("Buscar propuestas por actividad, grupo o contenido del mensaje");
        body.addView(search);gap(body,8);
        HorizontalScrollView scroller=new HorizontalScrollView(this);scroller.setHorizontalScrollBarEnabled(false);
        LinearLayout chips=row();String[] options={"Todas","Sin fecha","Vencidas","Del historial","Próximas"};
        for(int i=0;i<options.length;i++){
            final int chosen=i;Button chip=button(options[i],()->{reviewFilter=chosen;inboxLimit=25;render();});
            chip.setTextColor(chosen==reviewFilter?0xffffffff:MUTED);
            chip.setBackground(rounded(chosen==reviewFilter?GREEN:PALE,18));
            chip.setContentDescription("Mostrar propuestas "+options[i]+(chosen==reviewFilter?", filtro activo":""));
            chips.addView(chip);
        }
        scroller.addView(chips);body.addView(scroller);gap(body,10);
        reviewList=column();body.addView(reviewList);
        fillReviewList(inbox);
        search.addTextChangedListener(new TextWatcher(){
            public void beforeTextChanged(CharSequence t,int start,int count,int after){}
            public void onTextChanged(CharSequence t,int start,int before,int count){
                reviewQuery=t.toString();inboxLimit=25;
                if(reviewSearchTask!=null)handler.removeCallbacks(reviewSearchTask);
                reviewSearchTask=()->{if(page==2&&search.isAttachedToWindow())fillReviewList(inbox);};
                handler.postDelayed(reviewSearchTask,190);
            }
            public void afterTextChanged(Editable e){}
        });
    }
    /** Rebuild only the proposal list while typing; preserve the search field and cursor. */
    void fillReviewList(List<Store.Inbox> all){
        if(reviewList==null)return;
        reviewList.removeAllViews();
        List<Store.Inbox> inbox=new ArrayList<>();
        long now=System.currentTimeMillis();
        for(Store.Inbox proposal:all){
            if(ReviewFilters.matches(proposal.title,proposal.source,proposal.original,
               proposal.dateKnown,proposal.due,proposal.historical,reviewFilter,reviewQuery,now))
                inbox.add(proposal);
        }
        if(reviewCount!=null)reviewCount.setText("Propuestas encontradas · "+inbox.size()+" de "+all.size());
'''
s=s[:start]+head+newheader+tail+close+s[end:]

# Modest visual upgrades that do not change screen dimensions or force redraws.
replace('c.setPadding(dp(15),dp(14),dp(15),dp(14));c.setBackground(outlined(SURFACE,19,STROKE));c.setElevation(dp(3));',
'c.setPadding(dp(16),dp(15),dp(16),dp(15));c.setBackground(outlined(SURFACE,20,STROKE));c.setElevation(dp(2));')
replace('TextView title=text(t.title,17,t.done?MUTED:INK,true);',
'TextView title=text(t.title,17,t.done?MUTED:INK,true);title.setMaxLines(3);title.setEllipsize(android.text.TextUtils.TruncateAt.END);')

mainfile.write_text(s,encoding="utf-8")
gradle=Path("AgendaClara/app/build.gradle")
config=gradle.read_text(encoding="utf-8")
if config.count("versionCode 10")!=1 or config.count("versionName '2.1.0'")!=1:
    raise RuntimeError("This patch needs the previously verified 2.1.0")
gradle.write_text(config.replace("versionCode 10","versionCode 11").replace("versionName '2.1.0'","versionName '2.2.0'"),encoding="utf-8")
print("Agenda Clara 2.2.0: agenda search, review filters, component isolation, subtle transitions.")
