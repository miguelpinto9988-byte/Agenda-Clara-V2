package pe.agendaclara.app;

import android.content.Context;
import java.time.DayOfWeek;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/**
 * Read-only source of truth for academic home widgets.
 * Uses stored profile UUID + explicit task/course links; no fuzzy course assignment.
 */
public final class AcademicWidgetData {
    private AcademicWidgetData(){}
    private static final Locale ES=new Locale("es","PE");
    private static final DateTimeFormatter CLOCK=DateTimeFormatter.ofPattern("h:mm a",ES);
    private static final DateTimeFormatter DAY=DateTimeFormatter.ofPattern("d MMM",ES);

    public static final class NextClass {
        public final ScheduleEntry entry;
        public final LocalDate date;
        public NextClass(ScheduleEntry e,LocalDate d){entry=e;date=d;}
    }
    public static AcademicSchedules.Profile active(Context c){
        return AcademicSchedules.find(c,AcademicSchedules.activeId(c));
    }
    public static String clock(int minutes){
        return LocalDate.now().atStartOfDay().plusMinutes(minutes).format(CLOCK);
    }
    public static List<ScheduleEntry> classes(Context c,String profileId,int day){
        List<ScheduleEntry> result=new ArrayList<>();
        if(profileId==null||profileId.isEmpty())return result;
        for(ScheduleEntry e:ScheduleDatabase.get(c).all(profileId))
            if(e.enabled&&e.day==day)result.add(e);
        result.sort(Comparator.comparingInt(e->e.start));
        return result;
    }
    public static NextClass next(Context c,AcademicSchedules.Profile p,LocalDateTime now){
        if(p==null)return null;
        NextClass best=null;
        LocalDateTime bestTime=null;
        List<ScheduleEntry> all=ScheduleDatabase.get(c).all(p.id);
        for(int offset=0;offset<=7;offset++){
            LocalDate date=now.toLocalDate().plusDays(offset);
            int day=date.getDayOfWeek().getValue();
            for(ScheduleEntry e:all){
                if(!e.enabled||e.day!=day)continue;
                LocalDateTime end=date.atStartOfDay().plusMinutes(e.end);
                if(!end.isAfter(now))continue;
                LocalDateTime start=date.atStartOfDay().plusMinutes(e.start);
                LocalDateTime candidate=start.isBefore(now)?now:start;
                if(bestTime==null||candidate.isBefore(bestTime)){
                    bestTime=candidate;best=new NextClass(e,date);
                }
            }
        }
        return best;
    }
    public static String relative(LocalDate d){
        if(d.equals(LocalDate.now()))return "Hoy";
        if(d.equals(LocalDate.now().plusDays(1)))return "Mañana";
        return d.format(DateTimeFormatter.ofPattern("EEE d MMM",ES));
    }
    public static String due(Task t){
        if(t.due<=0){
            int w=SyllabusReviewIntelligence.week(t.notes);
            return w>0?"Semana "+w+" · fecha por confirmar":"Fecha por confirmar";
        }
        return Instant.ofEpochMilli(t.due).atZone(ZoneId.systemDefault())
                .toLocalDate().format(DAY);
    }
    public static boolean linked(Context c,Task t,String profileId,String course){
        if(t==null||profileId==null||course==null)return false;
        AcademicTaskLinks.Link link=AcademicTaskLinks.get(c).find(t.id);
        return link!=null&&profileId.equals(link.profileId)
                &&AcademicSchedules.key(link.course).equals(AcademicSchedules.key(course));
    }
    public static boolean assessment(Task t){
        if(t==null)return false;
        String s=SyllabusReviewIntelligence.fold(t.title+" "+t.source);
        return s.contains("silabo")||s.contains("examen")||s.contains("parcial")
                ||s.contains("sustentacion final")||s.contains("proyecto final")
                ||s.contains("producto final")||s.contains("portafolio final")
                ||s.contains("trabajo final");
    }
    public static List<Task> courseTasks(Context c,String profileId,String course,boolean assessments){
        List<Task> out=new ArrayList<>();
        for(Task t:Store.get(c).all()){
            if(t.done||!linked(c,t,profileId,course))continue;
            if(assessment(t)==assessments)out.add(t);
        }
        out.sort((a,b)->{
            long aa=a.due<=0?Long.MAX_VALUE:a.due;
            long bb=b.due<=0?Long.MAX_VALUE:b.due;
            int compare=Long.compare(aa,bb);
            return compare!=0?compare:Long.compare(a.id,b.id);
        });
        return out;
    }
    public static List<Task> dailyTasks(Context c,LocalDate date){
        long end=date.plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli();
        List<Task> out=new ArrayList<>();
        for(Task t:Store.get(c).all())if(!t.done&&t.due>0&&t.due<end)out.add(t);
        out.sort(Comparator.comparingLong(t->t.due));
        return out;
    }
    public static int pendingCount(Context c){
        int count=0;
        for(Task t:Store.get(c).all())if(!t.done)count++;
        return count;
    }
    public static String evaluation(Context c,String profileId,String course){
        for(Task t:courseTasks(c,profileId,course,true)){
            String title=t.title==null?"Evaluación":t.title.trim();
            if(title.length()>32)title=title.substring(0,30)+"…";
            return title+" · "+due(t);
        }
        return "Sin evaluaciones registradas";
    }
    public static int countExams(Context c,String profileId){
        int n=0;
        for(Task t:Store.get(c).all()){
            if(t.done||!assessment(t))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(c).find(t.id);
            if(link!=null&&profileId!=null&&profileId.equals(link.profileId))n++;
        }
        return n;
    }
}
