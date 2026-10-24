#!/usr/bin/env python3
"""Agenda Clara 3.1: selector multi-día (1-7) para creación manual y revisión de OCR."""
from pathlib import Path
root=Path("AgendaClara")
src=root/"app/src/main/java/pe/agendaclara/app"
file=src/"ScheduleActivity.java"
s=file.read_text(encoding="utf-8")
def edit(old,new):
    global s
    n=s.count(old)
    if n!=1:raise RuntimeError(f"Ancla inesperada (n={n}): {old[:110]!r}")
    s=s.replace(old,new,1)

# Reemplaza el control de día único por chips seleccionables, sin romper la edición OCR.
# La clase original permanece en la selección y cada día adicional se convierte en
# una instancia independiente, con el mismo color, sala, horario y alarma.
anchor='''    private void colorMixer(int[] color,boolean[] manuallyColored,View preview){'''
helpers='''    // 3.1: helper para elegir hasta los siete días en creación manual y revisión OCR.
    private void chooseScheduleDays(ScheduleEntry entry, Runnable afterSelection){
        final String[] names={"Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"};
        final boolean[] days=new boolean[7];
        if(entry.day>=1&&entry.day<=7)days[entry.day-1]=true;
        else days[0]=true;
        LinearLayout panel=col();panel.setPadding(dp(18),dp(9),dp(18),dp(12));
        panel.addView(txt("Selecciona de 1 a 7 días para este curso",14,INK,true));
        space(panel,9);
        final ArrayList<android.widget.CheckBox> choices=new ArrayList<>();
        for(int i=0;i<7;i++){
            final int index=i;
            android.widget.CheckBox check=new android.widget.CheckBox(this);
            check.setText(names[i]);check.setTextSize(15);check.setChecked(days[i]);
            check.setButtonTintList(android.content.res.ColorStateList.valueOf(entry.color));
            check.setOnCheckedChangeListener((view,checked)->days[index]=checked);
            panel.addView(check);choices.add(check);
        }
        AlertDialog dialog=new AlertDialog.Builder(this)
            .setTitle("Días del curso")
            .setView(panel)
            .setNegativeButton("Cancelar",null).setPositiveButton("Aplicar",null).create();
        dialog.setOnShowListener(v->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(btn->{
            int count=0;for(boolean selected:days)if(selected)count++;
            if(count==0){toast("Selecciona al menos un día");return;}
            ArrayList<ScheduleEntry> batch=new ArrayList<>();
            for(int day=1;day<=7;day++)if(days[day-1]){
                ScheduleEntry copy=ScheduleMultiDays.copy(entry,day);
                if(day!=entry.day)copy.id=0;
                batch.add(copy);
            }
            if(batch.isEmpty())return;
            dialog.dismiss();
            final boolean isOCR=detected!=null&&detected.candidates.contains(entry);
            if(isOCR){
                int initial=detected.candidates.indexOf(entry);
                if(initial>=0){
                    boolean keep=initial<chosen.size()&&chosen.get(initial);
                    detected.candidates.remove(initial);
                    if(initial<chosen.size())chosen.remove(initial);
                    for(int k=0;k<batch.size();k++){
                        ScheduleEntry item=batch.get(k);
                        // No incluir duplicados idénticos dentro de la foto
                        boolean dup=false;
                        for(ScheduleEntry old:detected.candidates)
                            if(old.day==item.day&&old.start==item.start&&old.end==item.end&&
                               ScheduleCourseColors.same(old.course,item.course)){dup=true;break;}
                        if(!dup){detected.candidates.add(initial,item);chosen.add(initial,keep);initial++;}
                    }
                    ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all());
                    show(5);
                }
            }else{
                confirmConflicts(batch,()->{
                    ScheduleDatabase db=ScheduleDatabase.get(this);
                    for(ScheduleEntry item:batch)
                        if(db.save(item)){db.recolorSameCourse(item.course,item.color);ScheduleReminders.schedule(this,item);}
                    show(1);
                });
            }
            if(afterSelection!=null)afterSelection.run();
        }));
        dialog.show();
    }
'''
edit(anchor,helpers+anchor)

# Desde editor existente: ofrecer selección múltiple al agregar una materia.
# Abrir control tras guardar sesión inicial para reutilizar campos ya validados.
# Desde OCR: mantener visible opción para cualquier bloque en la revisión.
target='''            View accent=new View(this);accent.setBackground(bg(s.color,8));c.addView(accent,new LinearLayout.LayoutParams(-1,dp(7)));space(c,6);'''
edit(target,target+'''
            c.addView(btn("Seleccionar días · Lunes a domingo",()->chooseScheduleDays(s,null),false));
            space(c,6);''')

# Desde creación manual: selector de días accesible tras configurar cada sesión.
target2='''        form.addView(txt("Color del curso · 72 tonos rápidos + 360 tonos en catálogo",13,INK,true));'''
edit(target2,'''        if(current.id==0){
            form.addView(btn("Repetir este curso · Seleccionar días (1–7)",()->{
                ScheduleEntry draft=new ScheduleEntry();
                draft.course=course.getText().toString().trim();
                draft.room=current.room;
                draft.start=current.start;
                draft.end=current.end;
                draft.day=current.day;
                draft.color=current.color;
                if(!ScheduleEntry.valid(draft)){toast("Completa el curso y las horas válidas antes de elegir días");return;}
                chooseScheduleDays(draft,()->{});
            },false));
            space(form,9);
        }
'''+target2)
file.write_text(s,encoding="utf-8")

(src/"ScheduleMultiDays.java").write_text("""package pe.agendaclara.app;
import java.util.*;
/** Genera sesiones independientes para una misma materia en cualquier conjunto de 1 a 7 días. */
public final class ScheduleMultiDays {
    private ScheduleMultiDays(){}
    public static ScheduleEntry copy(ScheduleEntry source,int day){
        if(source==null||day<1||day>7)throw new IllegalArgumentException("Día inválido");
        ScheduleEntry e=new ScheduleEntry();
        e.day=day;e.course=source.course;e.room=source.room;
        e.start=source.start;e.end=source.end;e.color=source.color;
        e.reminder=source.reminder;e.enabled=source.enabled;
        return e;
    }
    public static List<ScheduleEntry> expand(ScheduleEntry source,Collection<Integer> days){
        if(days==null||days.isEmpty())throw new IllegalArgumentException("Elige días");
        TreeSet<Integer> selected=new TreeSet<>(days);
        List<ScheduleEntry> out=new ArrayList<>();
        for(int day:selected)out.add(copy(source,day));
        return out;
    }
}
""",encoding="utf-8")

p=root/"app/build.gradle";gradle=p.read_text(encoding="utf-8")
if gradle.count("versionCode 20")!=1 or gradle.count("versionName '3.0.0'")!=1:
    raise RuntimeError("Requiere Agenda 3.0.0")
p.write_text(gradle.replace("versionCode 20","versionCode 21").replace("versionName '3.0.0'","versionName '3.1.0'"),encoding="utf-8")
print("AGENDA_3_1_DAYS_PATCH_APPLIED")
