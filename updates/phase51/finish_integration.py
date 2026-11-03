#!/usr/bin/env python3
"""3.12.0: preserve sticky-note navigation and match Tesseract4Android API."""
from pathlib import Path
BASE=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
def replace(filename,old,new,label):
    f=BASE/filename
    s=f.read_text(encoding='utf-8')
    assert s.count(old)==1,(filename,label,s.count(old))
    f.write_text(s.replace(old,new),encoding='utf-8')
replace('SyllabusPdfReader.java','finally{if(api!=null)api.end();}', 'finally{if(api!=null)api.recycle();}', 'tesseract release')
replace('MainActivity.java','boolean showTaskList=false;', 'boolean showTaskList=false,showNotes=false;', 'notes mode')
replace('MainActivity.java','showTaskList=state.getBoolean("show_tasks",false);','showTaskList=state.getBoolean("show_tasks",false);showNotes=state.getBoolean("show_notes",false);','restore notes mode')
replace('MainActivity.java','out.putBoolean("show_tasks",showTaskList);','out.putBoolean("show_tasks",showTaskList);out.putBoolean("show_notes",showNotes);','persist notes mode')
replace('MainActivity.java',".append(showTaskList).append(':').append(calendarPanel)",".append(showTaskList).append(':').append(showNotes).append(':').append(calendarPanel)",'signature')
replace('MainActivity.java',
    'page=0;selectedCategory="Notas";render();return;',
    'page=0;showTaskList=false;showNotes=true;render();return;',
    'sticky_widget_notes route')
replace('MainActivity.java',
    'body.removeAllViews();if(page==0){if(showTaskList){',
    'body.removeAllViews();if(page==0){if(showNotes){notesPage();}else if(showTaskList){',
    'notes home route')
replace('MainActivity.java',
    'if(index==0)showTaskList=false;',
    'if(index==0){showTaskList=false;showNotes=false;}',
    'navigation reset')
needle='    void tasksPage(){'
insert='''    void notesPage(){
        LinearLayout header=card(body);
        header.addView(button("‹ Volver a Mi guía",()->{showNotes=false;render();}));
        header.addView(text("Mis notas adhesivas",21,INK,true));
        header.addView(button("＋ Nueva nota",()->StickyNotesUi.showEditor(this,null)));
        java.util.LinkedHashSet<String> categories=new java.util.LinkedHashSet<>();
        categories.add("Notas");
        for(StickyNotesStore.Note note:StickyNotesStore.get(this).all())
            if(note.category!=null&&!note.category.isEmpty())categories.add(note.category);
        for(String category:categories)StickyNotesUi.agenda(this,body,category,"");
    }
'''
replace('MainActivity.java',needle,insert+needle,'notes full list')
replace('HomeDashboard.java',
    '()->StickyNotesUi.showEditor(a,null)};',
    '()->{a.page=0;a.showTaskList=false;a.showNotes=true;a.render();}};',
    'notes tile opens full notes')
print('PASS 3.12.0: persisted notes section, widget notes route and supported Tesseract API')
