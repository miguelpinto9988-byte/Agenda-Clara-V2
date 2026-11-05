#!/usr/bin/env python3
"""Entrega B: add explicit course routing to both task editors (no APK)."""
from pathlib import Path

def once(source,old,new,label):
    if old==new:return source
    n=source.count(old)
    if n==1:return source.replace(old,new,1)
    if n==0 and new in source:return source
    raise RuntimeError(f"{label}: anclaje inesperado ({n}); se detuvo sin modificar")

def main_editor(source):
    # Give manual task creation a direct course chooser, independent of matching.
    anchor='''        box.addView(categoryDisplay,new LinearLayout.LayoutParams(-1,dp(60)));gap(box,9);'''
    insert='''        box.addView(categoryDisplay,new LinearLayout.LayoutParams(-1,dp(60)));gap(box,9);
        final AcademicCourseMatcher.Course[] chosenAcademicCourse={null};
        Button academicCourseButton=button("Curso del horario (opcional) · Elegir",()->{});
        academicCourseButton.setOnClickListener(v->AcademicCourseRouting.chooseAny(this,chosen->{
            chosenAcademicCourse[0]=chosen;
            academicCourseButton.setText("Curso: "+chosen.name+" · "+chosen.category+"  ›");
        }));
        box.addView(academicCourseButton);gap(box,9);'''
    source=once(source,anchor,insert,"selector de curso manual")
    before='''                if(t.calendarEnabled&&t.calendarId<0)t.calendarId=Prefs.calendar(this);
                try{if(inboxId>0){if(!Store.get(this).acceptProposal(t,inboxId)){toast("Esta propuesta ya fue atendida.");return;}}else Store.get(this).save(t);}catch(android.database.sqlite.SQLiteConstraintException e){toast("Esta propuesta ya fue convertida en tarea.");return;}
                if(inboxId>0)Reminders.cancelProposal(this,inboxId);if(t.done)Reminders.cancel(this,t.id);else Reminders.schedule(this,t);TaskWidget.refresh(this);editor.dismiss();render();
                if(t.calendarEnabled)background(()->{String result=CalendarBridge.upsert(this,t);return result.isEmpty()?"Tarea guardada y evento escrito en el calendario del teléfono.":result;});
                else toast(t.due>0&&t.due<System.currentTimeMillis()?"Tarea guardada con fecha vencida.":"Tarea guardada.");'''
    after='''                if(t.calendarEnabled&&t.calendarId<0)t.calendarId=Prefs.calendar(this);
                AcademicCourseRouting.Decision finishSave=match->{
                    if(match!=null)t.category=match.category;
                    try{
                        if(inboxId>0){
                            if(!Store.get(this).acceptProposal(t,inboxId)){
                                toast("Esta propuesta ya fue atendida.");return;
                            }
                        }else Store.get(this).save(t);
                        if(match!=null){
                            AcademicTaskLinks.get(this).assign(t.id,match.profileId,match.name);
                        }else if(existing!=null&&!AcademicSchedules.ownsCategory(this,t.category)){
                            AcademicTaskLinks.get(this).clear(t.id);
                        }
                    }catch(android.database.sqlite.SQLiteConstraintException e){
                        toast("Esta propuesta ya fue convertida en tarea.");return;
                    }catch(RuntimeException e){
                        toast("Revisa la tarea: no se pudo guardar correctamente.");return;
                    }
                    if(inboxId>0)Reminders.cancelProposal(this,inboxId);
                    if(t.done)Reminders.cancel(this,t.id);else Reminders.schedule(this,t);
                    TaskWidget.refresh(this);editor.dismiss();render();
                    if(t.calendarEnabled)background(()->{
                        String result=CalendarBridge.upsert(this,t);
                        return result.isEmpty()?"Tarea guardada y evento escrito en el calendario del teléfono.":result;
                    });
                    else toast(t.due>0&&t.due<System.currentTimeMillis()
                        ?"Tarea guardada con fecha vencida.":"Tarea guardada.");
                };
                if(chosenAcademicCourse[0]!=null)finishSave.decided(chosenAcademicCourse[0]);
                else AcademicCourseRouting.review(this,t.title+" "+t.notes,t.category,finishSave);'''
    source=once(source,before,after,"guardar tarea manual con confirmación")
    return source

def voice_editor(source):
    before='''                try{Store.get(activity).save(task);Reminders.schedule(activity,task);TaskWidget.refresh(activity);}catch(Exception e){
                    new AlertDialog.Builder(activity,R.style.DialogTheme).setMessage("No se pudo guardar la tarea. Vuelve a intentarlo.").setPositiveButton("Entendido",null).show();return;}
                showSuccess(task,reminderValue);review.dismiss();review=null;'''
    after='''                AcademicCourseRouting.review(activity,spoken+" "+courseValue,task.category,matched->{
                    if(matched!=null)task.category=matched.category;
                    try{
                        Store.get(activity).save(task);
                        if(matched!=null)AcademicTaskLinks.get(activity).assign(
                                task.id,matched.profileId,matched.name);
                        Reminders.schedule(activity,task);TaskWidget.refresh(activity);
                    }catch(Exception e){
                        new AlertDialog.Builder(activity,R.style.DialogTheme)
                            .setMessage("No se pudo guardar correctamente la tarea. Revisa tu agenda.")
                            .setPositiveButton("Entendido",null).show();return;
                    }
                    showSuccess(task,reminderValue);review.dismiss();review=null;
                });'''
    return once(source,before,after,"guardar tarea dictada con confirmación")

def run():
    root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
    main=root/"MainActivity.java"
    voice=root/"VoiceQuickTask.java"
    original=main.read_text(encoding="utf-8")
    v=voice.read_text(encoding="utf-8")
    changed=main_editor(original)
    changed_voice=voice_editor(v)
    main.write_text(changed,encoding="utf-8")
    voice.write_text(changed_voice,encoding="utf-8")
    print("PASS B: confirmación de cursos para tareas manuales y por voz; sin APK")

if __name__=="__main__":run()
