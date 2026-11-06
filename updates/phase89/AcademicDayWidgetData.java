package pe.agendaclara.app;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/** Pure, profile-scoped day grouping; never displays invented placeholder classes. */
public final class AcademicDayWidgetData {
    private AcademicDayWidgetData() {}
    public static List<ScheduleEntry> today(List<ScheduleEntry> sessions, LocalDate date){
        ArrayList<ScheduleEntry> out=new ArrayList<>();
        if(sessions==null||date==null)return out;
        int day=date.getDayOfWeek().getValue();
        for(ScheduleEntry item:sessions)
            if(item!=null&&item.enabled&&item.day==day)out.add(item);
        out.sort(Comparator.comparingInt((ScheduleEntry s)->s.start)
            .thenComparing(s->s.course==null?"":s.course));
        return out;
    }
    public static String countLabel(int count){
        return count==1?"1 clase hoy":count+" clases hoy";
    }
    public static String roomLabel(String raw){
        String s=raw==null?"":raw.trim();
        if(s.isEmpty())return "Aula por confirmar";
        return s.toLowerCase(Locale.ROOT).startsWith("aula")?s:"Aula "+s;
    }
}