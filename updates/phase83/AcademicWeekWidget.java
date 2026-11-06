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
import java.util.List;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.time.LocalDate;
import java.time.ZoneId;

/** Horario semanal + evaluaciones, with dates scoped to each individual course. */
public final class AcademicWeekWidget extends AppWidgetProvider {
    public static void refresh(Context c){
        AppWidgetManager m=AppWidgetManager.getInstance(c);
        for(int id:m.getAppWidgetIds(new ComponentName(c,AcademicWeekWidget.class)))
            update(c,m,id);
    }
    public static void update(Context c,AppWidgetManager m,int id){
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_academic_week);
        AcademicSchedules.Profile p=null;
        try{p=AcademicWidgetRepository.profile(c,id);}catch(RuntimeException ignored){}
        v.setTextViewText(R.id.academic_week_profile,
                p==null?"Configura un horario":p.name);
        if(p==null){
            v.setTextViewText(R.id.academic_week_classes,"Selecciona uno de tus horarios académicos.");
            v.setTextViewText(R.id.academic_week_evaluations,"No hay evaluaciones vinculadas.");
            Intent config=new Intent(c,AcademicWidgetSettingsActivity.class)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id)
                    .setData(Uri.parse("agenda://academic/week/config/"+id));
            v.setOnClickPendingIntent(R.id.academic_week_heading,
                    PendingIntent.getActivity(c,17000+id,config,
                            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        }else try{
            WidgetAppearance.Settings settings=WidgetAppearance.read(c,id);
            List<ScheduleEntry> entries=AcademicWidgetRepository.classes(c,p.id);
            StringBuilder courses=new StringBuilder();
            StringBuilder evaluations=new StringBuilder();
            int shown=0,exams=0,hiddenExams=0;
            LinkedHashMap<String,String> distinctCourses=new LinkedHashMap<>();
            for(ScheduleEntry entry:entries){
                distinctCourses.put(AcademicSchedules.key(entry.course),entry.course);
                if(shown>=5)continue;
                if(shown++>0)courses.append("\n");
                courses.append(ScheduleEntry.dayName(entry.day).substring(0,3))
                        .append(" ").append(AcademicWidgetRepository.timeLabel(entry.start))
                        .append("  ").append(settings.hidePrivateTitles?
                            "Clase programada":AcademicWidgetRepository.shortText(entry.course,34));
            }
            // Collect every scheduled course before limiting the visible evaluations.
            // A later exam from course A must not hide an earlier exam from course B.
            List<AcademicWidgetEvaluationOrder.Entry> orderedEntries=new ArrayList<>();
            for(String course:distinctCourses.values()){
                for(Task task:AcademicWidgetRepository.linkedTasks(c,p.id,course,true)){
                    orderedEntries.add(new AcademicWidgetEvaluationOrder.Entry(course,task));
                }
            }
            long startOfToday=LocalDate.now().atStartOfDay(ZoneId.systemDefault())
                    .toInstant().toEpochMilli();
            for(AcademicWidgetEvaluationOrder.Entry entry:
                    AcademicWidgetEvaluationOrder.ordered(orderedEntries,startOfToday)){
                if(exams>=4){hiddenExams++;continue;}
                if(exams++>0)evaluations.append("\n");
                Task task=entry.task;
                String dateLabel=AcademicWidgetRepository.evaluationLabel(task);
                if(task.due>0&&task.due<startOfToday)dateLabel="Vencida · "+dateLabel;
                evaluations.append(settings.hidePrivateTitles?"Evaluación del curso":
                        AcademicWidgetRepository.shortText(entry.course,22))
                        .append(": ").append(settings.hidePrivateTitles?
                            "Evaluación":AcademicWidgetRepository.shortText(task.title,21))
                        .append(" · ").append(dateLabel);
            }
            if(hiddenExams>0)evaluations.append("\n+").append(hiddenExams).append(" evaluaciones más");
            if(entries.size()>shown)courses.append("\n+").append(entries.size()-shown).append(" clases más");
            v.setTextViewText(R.id.academic_week_classes,
                    courses.length()>0?courses.toString():"Todavía no hay clases en este horario.");
            v.setTextViewText(R.id.academic_week_evaluations,
                    evaluations.length()>0?evaluations.toString():
                        "Sin evaluaciones próximas vinculadas a estos cursos.");
            Intent schedule=new Intent(c,ScheduleActivity.class)
                    .putExtra("profile_id",p.id)
                    .setData(Uri.parse("agenda://academic/week/schedule/"+id));
            v.setOnClickPendingIntent(R.id.academic_week_heading,
                    PendingIntent.getActivity(c,17000+id,schedule,
                            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
        }catch(RuntimeException ignored){
            v.setTextViewText(R.id.academic_week_classes,"No se pudieron leer las clases.");
            v.setTextViewText(R.id.academic_week_evaluations,
                    "Abre Agenda Clara y comprueba el horario seleccionado.");
        }
        AcademicWidgetTheme.apply(c,v,R.id.academic_week_root,
                new int[]{R.id.academic_week_heading},
                new int[]{R.id.academic_week_profile,R.id.academic_week_classes,R.id.academic_week_evaluations},
                WidgetAppearance.read(c,id).theme);
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