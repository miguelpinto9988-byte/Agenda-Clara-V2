package pe.agendaclara.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.RemoteViews;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

/** Mi día + próxima clase; shows only linked tasks from that schedule and course. */
public final class AcademicDayWidget extends AppWidgetProvider {
    public static void refresh(Context c){
        AppWidgetManager m=AppWidgetManager.getInstance(c);
        for(int id:m.getAppWidgetIds(new ComponentName(c,AcademicDayWidget.class)))
            update(c,m,id);
    }
    public static void update(Context c,AppWidgetManager m,int id){
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_academic_day);
        AcademicSchedules.Profile p=null;
        try{p=AcademicWidgetRepository.profile(c,id);}catch(RuntimeException ignored){}
        String profileName=p==null?"Selecciona un horario":p.name;
        v.setTextViewText(R.id.academic_day_profile,profileName);
        if(p==null){
            v.setTextViewText(R.id.academic_day_course,"Aún no tienes un horario elegido");
            v.setTextViewText(R.id.academic_day_time,"Toca el widget para configurarlo.");
            v.setTextViewText(R.id.academic_day_tasks,"Crea o selecciona un horario desde Plan de estudio.");
            Intent config=new Intent(c,AcademicWidgetSettingsActivity.class)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id)
                    .setData(Uri.parse("agenda://academic/day/config/"+id));
            v.setOnClickPendingIntent(R.id.academic_day_heading,
                    PendingIntent.getActivity(c,15000+id,config,
                            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        }else try{
            List<ScheduleEntry> classes=AcademicWidgetRepository.classes(c,p.id);
            AcademicWidgetRepository.NextClass next=AcademicWidgetRepository.nextClass(
                    classes,LocalDate.now(),LocalTime.now());
            if(next==null){
                v.setTextViewText(R.id.academic_day_course,"Sin próximas clases registradas");
                v.setTextViewText(R.id.academic_day_time,"Abre tu horario para agregar clases.");
                v.setTextViewText(R.id.academic_day_tasks,"No hay tareas asociadas a una próxima clase.");
            }else{
                ScheduleEntry classEntry=next.entry;
                WidgetAppearance.Settings pref=WidgetAppearance.read(c,id);
                v.setTextViewText(R.id.academic_day_course,
                        pref.hidePrivateTitles?"Próxima clase":classEntry.course);
                String day=next.date.equals(LocalDate.now())?"Hoy":
                        AcademicWidgetRepository.dateLabel(next.date);
                v.setTextViewText(R.id.academic_day_time,
                        day+" · "+AcademicWidgetRepository.timeLabel(classEntry.start)
                        +"–"+AcademicWidgetRepository.timeLabel(classEntry.end)
                        +(classEntry.room.isEmpty()?"":" · Aula "+classEntry.room));
                List<Task> tasks=AcademicWidgetRepository.tasksForClass(c,p.id,classEntry.course);
                StringBuilder label=new StringBuilder();
                int limit=Math.min(3,tasks.size());
                for(int i=0;i<limit;i++){
                    if(i>0)label.append("\n");
                    label.append("☐ ").append(pref.hidePrivateTitles?"Tarea pendiente":
                            AcademicWidgetRepository.shortText(tasks.get(i).title,48));
                }
                if(tasks.size()>limit)label.append("\n+").append(tasks.size()-limit)+" más";
                v.setTextViewText(R.id.academic_day_tasks,
                        tasks.isEmpty()?"No hay tareas pendientes de este curso.":label.toString());
            }
            Intent schedule=new Intent(c,ScheduleActivity.class)
                    .putExtra("profile_id",p.id)
                    .setData(Uri.parse("agenda://academic/day/schedule/"+id));
            v.setOnClickPendingIntent(R.id.academic_day_heading,
                    PendingIntent.getActivity(c,15000+id,schedule,
                            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
            Intent tasks=new Intent(c,MainActivity.class).setAction("tasks")
                    .setData(Uri.parse("agenda://academic/day/tasks/"+id));
            v.setOnClickPendingIntent(R.id.academic_day_tasks,
                    PendingIntent.getActivity(c,16000+id,tasks,
                            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        }catch(RuntimeException e){
            v.setTextViewText(R.id.academic_day_course,"No se pudo consultar tu horario");
            v.setTextViewText(R.id.academic_day_tasks,"Abre Agenda Clara para revisar tus datos.");
        }
        m.updateAppWidget(id,v);
    }
    @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){
        for(int id:ids)update(c,m,id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c,AppWidgetManager m,int id,Bundle opts){
        update(c,m,id);
    }
    @Override public void onDeleted(Context c,int[] ids){
        for(int id:ids)WidgetAppearance.remove(c,id);
    }
}