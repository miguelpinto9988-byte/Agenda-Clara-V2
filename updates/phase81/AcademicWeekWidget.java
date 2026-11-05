package pe.agendaclara.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.RemoteViews;
import java.time.LocalDate;
import java.util.List;

/** Day-switching timetable with course-specific exams and final deliverables. */
public final class AcademicWeekWidget extends AppWidgetProvider {
    public static final String ACTION_DAY="pe.agendaclara.app.ACADEMIC_WIDGET_DAY";
    private static final String PREF="academic_week_widget_v1";
    private static SharedPreferences prefs(Context c){
        return c.getSharedPreferences(PREF,Context.MODE_PRIVATE);
    }
    public static void refresh(Context c){
        AppWidgetManager manager=AppWidgetManager.getInstance(c);
        for(int id:manager.getAppWidgetIds(new ComponentName(c,AcademicWeekWidget.class)))
            update(c,manager,id);
    }
    private static PendingIntent open(Context c,int id,int code,Intent intent){
        intent.setData(Uri.parse("agenda://academic/week/"+id+"/"+code));
        return PendingIntent.getActivity(c,id*110+code,intent,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }
    private static PendingIntent select(Context c,int id,int day){
        Intent intent=new Intent(c,AcademicWeekWidget.class).setAction(ACTION_DAY)
                .setData(Uri.parse("agenda://academic/week/select/"+id+"/"+day))
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id).putExtra("day",day);
        return PendingIntent.getBroadcast(c,id*10+day,intent,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }
    private static void update(Context c,AppWidgetManager manager,int id){
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_academic_week);
        AcademicSchedules.Profile p=AcademicWidgetData.active(c);
        int today=LocalDate.now().getDayOfWeek().getValue();
        int day=prefs(c).getInt("day_"+id,today);
        if(day<1||day>7)day=today;
        int[] tabs={R.id.academic_week_d1,R.id.academic_week_d2,
                R.id.academic_week_d3,R.id.academic_week_d4,R.id.academic_week_d5,
                R.id.academic_week_d6,R.id.academic_week_d7};
        for(int i=0;i<7;i++){
            v.setOnClickPendingIntent(tabs[i],select(c,id,i+1));
            v.setInt(tabs[i],"setBackgroundResource",
                    i+1==day?R.drawable.widget_day_selected:R.drawable.widget_day_idle);
            v.setTextColor(tabs[i],i+1==day?0xffffffff:0xff263c6a);
        }
        v.setOnClickPendingIntent(R.id.academic_week_header,open(c,id,1,
                new Intent(c,MainActivity.class).setAction("academic_widget_calendar")));
        v.setTextViewText(R.id.academic_week_profile,p==null?
                "Primero crea un horario":p.name+" · "+ScheduleEntry.dayName(day));
        int[] groups={R.id.academic_week_group1,R.id.academic_week_group2,
                R.id.academic_week_group3};
        int[] courses={R.id.academic_week_course1,R.id.academic_week_course2,
                R.id.academic_week_course3};
        int[] exams={R.id.academic_week_exam1,R.id.academic_week_exam2,
                R.id.academic_week_exam3};
        List<ScheduleEntry> classes=p==null?
                java.util.Collections.emptyList():AcademicWidgetData.classes(c,p.id,day);
        for(int i=0;i<groups.length;i++){
            if(i>=classes.size()){
                v.setViewVisibility(groups[i],View.GONE);
                continue;
            }
            ScheduleEntry e=classes.get(i);
            v.setViewVisibility(groups[i],View.VISIBLE);
            String course=e.course==null?"Clase":e.course;
            if(course.length()>46)course=course.substring(0,45)+"…";
            v.setTextViewText(courses[i],AcademicWidgetData.clock(e.start)+"  "+course);
            String evaluation=AcademicWidgetData.evaluation(c,p.id,e.course);
            v.setTextViewText(exams[i],evaluation);
            v.setTextColor(exams[i],
                evaluation.startsWith("Sin evaluaciones")?0xff63819b:0xff7046c4);
            v.setOnClickPendingIntent(groups[i],open(c,id,10+i,
                    new Intent(c,ScheduleActivity.class).putExtra("profile_id",p.id)));
        }
        v.setViewVisibility(R.id.academic_week_empty,
                classes.isEmpty()?View.VISIBLE:View.GONE);
        v.setTextViewText(R.id.academic_week_empty,p==null?
                "No hay horarios registrados. Configúralos en Calendario.":
                "Sin clases el "+ScheduleEntry.dayName(day).toLowerCase(java.util.Locale.ROOT));
        v.setTextViewText(R.id.academic_week_footer,
                p==null?"Sin evaluaciones":
                        AcademicWidgetData.countExams(c,p.id)+" evaluaciones pendientes · "+
                        classes.size()+" clases");
        manager.updateAppWidget(id,v);
    }
    @Override public void onReceive(Context c,Intent intent){
        if(ACTION_DAY.equals(intent.getAction())){
            int id=intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,-1);
            int day=intent.getIntExtra("day",-1);
            if(day<1||day>7)return;
            AppWidgetManager manager=AppWidgetManager.getInstance(c);
            boolean owned=false;
            for(int current:manager.getAppWidgetIds(new ComponentName(c,AcademicWeekWidget.class)))
                if(current==id){owned=true;break;}
            if(!owned)return;
            prefs(c).edit().putInt("day_"+id,day).apply();
            update(c,manager,id);
            return;
        }
        super.onReceive(c,intent);
    }
    @Override public void onDeleted(Context c,int[] ids){
        SharedPreferences.Editor editor=prefs(c).edit();
        for(int id:ids)editor.remove("day_"+id);
        editor.apply();
    }
    @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){
        for(int id:ids)update(c,m,id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c,AppWidgetManager m,int id,Bundle opts){
        update(c,m,id);
    }
}
