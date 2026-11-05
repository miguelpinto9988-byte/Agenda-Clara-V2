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
import java.time.LocalDateTime;
import java.util.List;

/** Home widget: upcoming class + its actual linked tasks + daily academic status. */
public final class AcademicDayWidget extends AppWidgetProvider {
    public static void refresh(Context c){
        AppWidgetManager manager=AppWidgetManager.getInstance(c);
        for(int id:manager.getAppWidgetIds(new ComponentName(c,AcademicDayWidget.class)))
            update(c,manager,id);
    }
    private static PendingIntent open(Context c,int widgetId,int code,Intent intent){
        intent.setData(Uri.parse("agenda://academic/day/"+widgetId+"/"+code));
        return PendingIntent.getActivity(c,widgetId*100+code,intent,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }
    private static void update(Context c,AppWidgetManager manager,int id){
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_academic_day);
        AcademicSchedules.Profile p=AcademicWidgetData.active(c);
        v.setTextViewText(R.id.academic_day_date,LocalDate.now().toString());
        v.setOnClickPendingIntent(R.id.academic_day_header,open(c,id,1,
                new Intent(c,MainActivity.class)));
        if(p==null){
            v.setTextViewText(R.id.academic_day_profile,"Configura un horario en Plan de estudio");
            v.setTextViewText(R.id.academic_day_course,"No hay horarios registrados");
            v.setTextViewText(R.id.academic_day_clock,"Abre Calendario para comenzar");
            v.setTextViewText(R.id.academic_day_room,"");
            v.setTextViewText(R.id.academic_day_label,"Próxima clase");
            v.setTextViewText(R.id.academic_day_exam,"No hay evaluaciones vinculadas");
        }else{
            v.setTextViewText(R.id.academic_day_profile,p.name);
            AcademicWidgetData.NextClass next=AcademicWidgetData.next(c,p,LocalDateTime.now());
            if(next==null){
                v.setTextViewText(R.id.academic_day_label,"Próxima clase");
                v.setTextViewText(R.id.academic_day_course,"No hay clases programadas");
                v.setTextViewText(R.id.academic_day_clock,"Revisa tu horario");
                v.setTextViewText(R.id.academic_day_room,"");
                fill(c,v,id,null);
            }else{
                v.setTextViewText(R.id.academic_day_label,"Próxima clase · "+
                        AcademicWidgetData.relative(next.date));
                v.setTextViewText(R.id.academic_day_course,next.entry.course);
                v.setTextViewText(R.id.academic_day_clock,
                        AcademicWidgetData.clock(next.entry.start)+" – "+
                        AcademicWidgetData.clock(next.entry.end));
                v.setTextViewText(R.id.academic_day_room,
                        next.entry.room.isEmpty()?"Aula sin registrar":"Aula "+next.entry.room);
                fill(c,v,id,AcademicWidgetData.courseTasks(c,p.id,next.entry.course,false));
                v.setOnClickPendingIntent(R.id.academic_day_class,open(c,id,3,
                        new Intent(c,ScheduleActivity.class).putExtra("profile_id",p.id)));
            }
            String first="Sin evaluaciones registradas";
            outer:for(AcademicSchedules.Profile ignored:new AcademicSchedules.Profile[]{p}){
                for(Task t:Store.get(c).all()){
                    if(t.done||!AcademicWidgetData.assessment(t))continue;
                    AcademicTaskLinks.Link link=AcademicTaskLinks.get(c).find(t.id);
                    if(link!=null&&p.id.equals(link.profileId)){
                        first=t.title+" · "+AcademicWidgetData.due(t);break outer;
                    }
                }
            }
            v.setTextViewText(R.id.academic_day_exam,first);
        }
        List<Task> today=AcademicWidgetData.dailyTasks(c,LocalDate.now());
        v.setTextViewText(R.id.academic_day_pending,today.size()+" para hoy · "+
                AcademicWidgetData.pendingCount(c)+" pendientes");
        manager.updateAppWidget(id,v);
    }
    private static void fill(Context c,RemoteViews v,int widgetId,List<Task> tasks){
        int[] rows={R.id.academic_day_task1,R.id.academic_day_task2,R.id.academic_day_task3};
        boolean any=tasks!=null&&!tasks.isEmpty();
        v.setTextViewText(R.id.academic_day_tasks_title,
                any?"Tareas de esta clase":"Tareas del próximo curso");
        for(int i=0;i<rows.length;i++){
            if(tasks!=null&&i<tasks.size()){
                Task t=tasks.get(i);
                String label="☐  "+t.title;
                if(label.length()>70)label=label.substring(0,69)+"…";
                v.setViewVisibility(rows[i],View.VISIBLE);
                v.setTextViewText(rows[i],label);
                v.setOnClickPendingIntent(rows[i],open(c,widgetId,10+i,
                        new Intent(c,MainActivity.class).setAction("academic_widget_task")
                                .putExtra("task_id",t.id)));
            }else{
                v.setViewVisibility(rows[i],i==0?View.VISIBLE:View.GONE);
                if(i==0)v.setTextViewText(rows[i],"Sin tareas pendientes vinculadas");
            }
        }
    }
    @Override public void onUpdate(Context c,AppWidgetManager manager,int[] ids){
        for(int id:ids)update(c,manager,id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c,AppWidgetManager manager,int id,Bundle b){
        update(c,manager,id);
    }
}
