#!/usr/bin/env python3
"""Agenda Clara 3.2: usar SOLO la fila existente Lun...Dom como multiselección."""
from pathlib import Path
root=Path("AgendaClara")
path=root/"app/src/main/java/pe/agendaclara/app/ScheduleActivity.java"
s=path.read_text(encoding="utf-8")
def one(a,b):
 global s
 if s.count(a)!=1:raise RuntimeError(f"Ancla {s.count(a)}: {a[:100]}")
 s=s.replace(a,b,1)

start=s.index("    // 3.1: helper para elegir hasta los siete días")
end=s.index("    private void colorMixer(",start)
s=s[:start]+s[end:]
one('''            c.addView(btn("Seleccionar días · Lunes a domingo",()->chooseScheduleDays(s,null),false));
            space(c,6);''',"")
start=s.index('''        if(current.id==0){
            form.addView(btn("Repetir este curso · Seleccionar días (1–7)",''')
end=s.index('''        form.addView(txt("Color del curso · 72 tonos rápidos + 360 tonos en catálogo",''',start)
s=s[:start]+s[end:]
one('''if(current.id>0){Arrays.fill(selected,false);selected[index]=true;}else selected[index]=!selected[index];''','''selected[index]=!selected[index];''')
# Las sesiones ya guardadas conserven su ID solo en el día original;
# cualquier otro día produce una nueva fila y no sobrescribe la original.
one('''ScheduleEntry e=current.copy();e.day=i+1;e.start=st;''',
    '''ScheduleEntry e=current.copy();if(e.day!=i+1)e.id=0;e.day=i+1;e.start=st;''')
# En modo OCR los siete días elegidos pasan a la lista de revisión,
# sin insertarse aún en BD ni perder la opción de elegir qué importar.
start=s.index("if(importing){ScheduleEntry s=additions.get(0);")
end=s.index("            confirmConflicts(additions",start)
s=s[:start]+'''if(importing){
                 if(detected!=null){
                     int index=detected.candidates.indexOf(previous);
                     if(index<0)index=detected.candidates.indexOf(current);
                     boolean checked=index>=0&&index<chosen.size()?chosen.get(index):true;
                     if(index>=0){detected.candidates.remove(index);if(index<chosen.size())chosen.remove(index);}
                     else index=detected.candidates.size();
                     int insert=index;
                     for(ScheduleEntry e:additions){
                         boolean duplicate=false;
                         for(ScheduleEntry existing:detected.candidates)
                             if(existing.day==e.day&&existing.start==e.start&&existing.end==e.end&&
                                ScheduleCourseColors.same(existing.course,e.course)){duplicate=true;break;}
                         if(!duplicate){
                             detected.candidates.add(insert,e);
                             chosen.add(Math.min(insert,chosen.size()),checked);
                             insert++;
                         }
                     }
                     ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all());
                 }else{
                     ScheduleEntry updated=additions.get(0);
                     current.day=updated.day;current.start=updated.start;current.end=updated.end;
                     current.course=updated.course;current.room=updated.room;
                     current.teacher=updated.teacher;current.notes=updated.notes;
                     current.color=updated.color;current.reminder=updated.reminder;
                 }
                 dialog.dismiss();if(onDone!=null)onDone.run();return;}''' + s[end:]

