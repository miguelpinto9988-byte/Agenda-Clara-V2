package pe.agendaclara.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.RemoteViews;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Mi día académico: original Canva PNG layers + real schedule/task data. */
public final class AcademicDayWidget extends AppWidgetProvider {
    private static final DateTimeFormatter DATE =
        DateTimeFormatter.ofPattern("EEE d MMM",new Locale("es","PE"));

    public static void refresh(Context c){
        AppWidgetManager m=AppWidgetManager.getInstance(c);
        for(int id:m.getAppWidgetIds(new ComponentName(c,AcademicDayWidget.class)))
            update(c,m,id);
    }
    private static void showCard(RemoteViews v,int index,ScheduleEntry entry,
                                 String label,boolean privateTitles){
        int card=index==0?R.id.academic_day_card_1:R.id.academic_day_card_2;
        int course=index==0?R.id.academic_day_course:R.id.academic_day_course_2;
        int time=index==0?R.id.academic_day_time:R.id.academic_day_time_2;
        int room=index==0?R.id.academic_day_room:R.id.academic_day_room_2;
        v.setViewVisibility(card,View.VISIBLE);
        v.setTextViewText(course,privateTitles?"Clase programada":entry.course);
        v.setTextViewText(time,label+" · "+
            AcademicWidgetRepository.timeLabel(entry.start)+"–"+
            AcademicWidgetRepository.timeLabel(entry.end));
        v.setTextViewText(room,privateTitles?"Ubicación privada":
            AcademicDayWidgetData.roomLabel(entry.room));
    }
    private static void blankCard(RemoteViews v,String title,String info){
        v.setViewVisibility(R.id.academic_day_card_1,View.VISIBLE);
        v.setViewVisibility(R.id.academic_day_card_2,View.GONE);
        v.setTextViewText(R.id.academic_day_course,title);
        v.setTextViewText(R.id.academic_day_time,info);
        v.setTextViewText(R.id.academic_day_room,"");
    }
    private static int pendingTasks(Context c,String profile,List<ScheduleEntry> shown){
        Set<Long> ids=new HashSet<>();
        for(ScheduleEntry e:shown)
            for(Task t:AcademicWidgetRepository.tasksForClass(c,profile,e.course))
                ids.add(t.id);
        return ids.size();
    }
    public static void update(Context c,AppWidgetManager m,int id){
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_academic_day);
        WidgetAppearance.Settings pref=WidgetAppearance.read(c,id);
        LocalDate date=LocalDate.now();
        v.setTextViewText(R.id.academic_day_heading,"Mi día académico");
        v.setTextViewText(R.id.academic_day_date,"Hoy · "+DATE.format(date));
        v.setTextViewText(R.id.academic_day_cta,"Ver horario");
        v.setViewVisibility(R.id.academic_day_card_2,View.GONE);
        v.setTextViewText(R.id.academic_day_tasks_label,"0 clases hoy");
        v.setTextViewText(R.id.academic_day_tasks,"0 tareas");
        Bundle options=m.getAppWidgetOptions(id);
        int height=options==null?250:options.getInt(
            AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,250);
        boolean compact=height<210;
        AcademicSchedules.Profile profile=null;
        try{profile=AcademicWidgetRepository.profile(c,id);}catch(RuntimeException ignored){}
        if(profile==null){
            v.setTextViewText(R.id.academic_day_profile,"Sin horario seleccionado");
            blankCard(v,"Selecciona tu horario","Toca aquí para configurarlo");
            v.setTextViewText(R.id.academic_day_cta,"Configurar");
            Intent config=new Intent(c,AcademicWidgetSettingsActivity.class)
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id)
                .setData(Uri.parse("agenda://academic/day/config/"+id));
            PendingIntent action=PendingIntent.getActivity(c,15000+id,config,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
            for(int target:new int[]{R.id.academic_day_heading,R.id.academic_day_cta,
                R.id.academic_day_arrow,R.id.academic_day_card_1})
                v.setOnClickPendingIntent(target,action);
        }else{
            v.setTextViewText(R.id.academic_day_profile,profile.name);
            try{
                List<ScheduleEntry> all=AcademicWidgetRepository.classes(c,profile.id);
                List<ScheduleEntry> today=AcademicDayWidgetData.today(all,date);
                ArrayList<ScheduleEntry> shown=new ArrayList<>();
                v.setTextViewText(R.id.academic_day_tasks_label,
                    AcademicDayWidgetData.countLabel(today.size()));
                if(!today.isEmpty()){
                    int count=Math.min(compact?1:2,today.size());
                    for(int i=0;i<count;i++){
                        shown.add(today.get(i));
                        showCard(v,i,today.get(i),"Hoy",pref.hidePrivateTitles);
                    }
                }else{
                    AcademicWidgetRepository.NextClass next=
                        AcademicWidgetRepository.nextClass(all,date,LocalTime.now());
                    if(next==null)blankCard(v,"Sin clases programadas",
                        "Agrega clases a tu horario");
                    else{
                        shown.add(next.entry);
                        showCard(v,0,next.entry,DATE.format(next.date),
                            pref.hidePrivateTitles);
                    }
                }
                int tasks=pendingTasks(c,profile.id,shown);
                v.setTextViewText(R.id.academic_day_tasks,
                    tasks==1?"1 tarea":tasks+" tareas");
            }catch(RuntimeException error){
                blankCard(v,"No se pudo consultar el horario",
                    "Abre Agenda Clara para revisar tus clases");
                v.setTextViewText(R.id.academic_day_tasks,"Ver tareas");
            }
            Intent schedule=new Intent(c,ScheduleActivity.class)
                .putExtra("profile_id",profile.id)
                .setData(Uri.parse("agenda://academic/day/schedule/"+id));
            PendingIntent openSchedule=PendingIntent.getActivity(c,15000+id,schedule,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
            for(int target:new int[]{R.id.academic_day_heading,R.id.academic_day_cta,
                R.id.academic_day_arrow,R.id.academic_day_card_1,
                R.id.academic_day_card_2})
                v.setOnClickPendingIntent(target,openSchedule);
            Intent tasks=new Intent(c,MainActivity.class).setAction("tasks")
                .setData(Uri.parse("agenda://academic/day/tasks/"+id));
            v.setOnClickPendingIntent(R.id.academic_day_tasks,
                PendingIntent.getActivity(c,16000+id,tasks,
                    PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        }
        if(compact)v.setViewVisibility(R.id.academic_day_card_2,View.GONE);
        AcademicWidgetTheme.applyDay(c,v,pref.theme);
        m.updateAppWidget(id,v);
    }
    @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){
        for(int id:ids)update(c,m,id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c,
            AppWidgetManager m,int id,Bundle options){update(c,m,id);}
    @Override public void onDeleted(Context c,int[] ids){
        for(int id:ids)WidgetAppearance.remove(c,id);
    }
}