package pe.agendaclara.app;

import android.content.Context;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/** Read-only native widget data adapter; all course matching is profile-scoped. */
public final class AcademicWidgetRepository {
    private AcademicWidgetRepository(){}
    private static final Locale ES=new Locale("es","PE");
    private static final DateTimeFormatter DATE=DateTimeFormatter.ofPattern("d MMM",ES);
    public static final class NextClass {
        public final ScheduleEntry entry;
        public final LocalDate date;
        NextClass(ScheduleEntry entry,LocalDate date){this.entry=entry;this.date=date;}
    }
    public static AcademicSchedules.Profile profile(Context c,int widgetId){
        String id=WidgetAppearance.read(c,widgetId).profileId;
        if(id==null||id.isEmpty())id=AcademicSchedules.activeId(c);
        return AcademicSchedules.find(c,id);
    }
    public static List<ScheduleEntry> classes(Context c,String profileId){
        List<ScheduleEntry> out=new ArrayList<>();
        for(ScheduleEntry entry:ScheduleDatabase.get(c).all(profileId))
            if(entry.enabled)out.add(entry);
        out.sort(Comparator.comparingInt((ScheduleEntry s)->s.day)
                .thenComparingInt(s->s.start).thenComparing(s->s.course));
        return out;
    }
    public static NextClass nextClass(List<ScheduleEntry> entries,LocalDate today,LocalTime now){
        NextClass best=null;
        long bestDistance=Long.MAX_VALUE;
        for(ScheduleEntry entry:entries){
            for(int days=0;days<7;days++){
                LocalDate date=today.plusDays(days);
                if(date.getDayOfWeek().getValue()!=entry.day)continue;
                if(days==0 && entry.end<=now.toSecondOfDay()/60)continue;
                long distance=days*1440L+Math.max(0,entry.start-now.toSecondOfDay()/60);
                if(distance<bestDistance){
                    best=new NextClass(entry,date);bestDistance=distance;
                }
                break;
            }
        }
        return best;
    }
    public static List<Task> linkedTasks(Context c,String profileId,String course,boolean evaluations){
        List<Task> out=new ArrayList<>();
        String courseKey=AcademicSchedules.key(course);
        for(Task task:Store.get(c).all()){
            if(task.done)continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(c).find(task.id);
            if(link==null||!profileId.equals(link.profileId)
                ||!courseKey.equals(AcademicSchedules.key(link.course)))continue;
            boolean exam=task.source!=null&&task.source.startsWith("Sílabo");
            if(exam!=evaluations)continue;
            out.add(task);
        }
        out.sort(Comparator.comparingLong((Task t)->t.due<=0?Long.MAX_VALUE:t.due)
                .thenComparingLong(t->t.id));
        return out;
    }
    public static List<Task> tasksForClass(Context c,String profileId,String course){
        // Include syllabus evaluations only in the assessment widget, not twice.
        return linkedTasks(c,profileId,course,false);
    }
    public static String evaluationLabel(Task task){
        if(task.due>0)return DATE.format(Instant.ofEpochMilli(task.due)
            .atZone(ZoneId.systemDefault()).toLocalDate());
        int week=SyllabusReviewIntelligence.week(task.notes);
        return week>0?"Semana "+week+" · fecha por confirmar":"Fecha por confirmar";
    }
    public static String shortText(String text,int limit){
        if(text==null)return "";
        String s=text.trim().replaceAll("\\s+"," ");
        return s.length()<=limit?s:s.substring(0,Math.max(1,limit-1))+"…";
    }
    public static String dateLabel(LocalDate date){
        return DATE.format(date);
    }
    public static String timeLabel(int minutes){
        return String.format(ES,"%02d:%02d",minutes/60,minutes%60);
    }
}