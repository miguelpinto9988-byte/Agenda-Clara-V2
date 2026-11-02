import pe.agendaclara.app.CalendarDaySummary;
import pe.agendaclara.app.Task;
import java.time.*;
import java.util.*;
public class CalendarDaySummaryTest {
    private static int checks=0;
    static void ok(boolean condition,String title){checks++;if(!condition)throw new AssertionError(title);}
    public static void main(String[] args){
        ZoneId zone=ZoneId.of("America/Lima");
        LocalDate d=LocalDate.of(2026,10,12),different=LocalDate.of(2026,11,1);
        Task first=new Task();first.due=d.atTime(9,0).atZone(zone).toInstant().toEpochMilli();
        Task second=new Task();second.due=d.atTime(15,0).atZone(zone).toInstant().toEpochMilli();
        Task unscheduled=new Task();unscheduled.due=0;
        Task next=new Task();next.due=different.atStartOfDay(zone).toInstant().toEpochMilli();
        Map<LocalDate,Integer> counted=CalendarDaySummary.tasksForMonth(Arrays.asList(first,second,unscheduled,next),YearMonth.from(d),zone);
        ok(counted.getOrDefault(d,0)==2,"two tasks on same date");
        ok(counted.size()==1,"ignore next month and undated tasks");
        ok(CalendarDaySummary.type(2,false)==CalendarDaySummary.TASK,"task only");
        ok(CalendarDaySummary.type(0,true)==CalendarDaySummary.NOTE,"note only");
        ok(CalendarDaySummary.type(2,true)==CalendarDaySummary.BOTH,"both independent icons");
        ok(CalendarDaySummary.type(0,false)==CalendarDaySummary.NONE,"empty day");
        ok(CalendarDaySummary.accessibility(d,2,1).contains("2 tareas y 1 nota"),"correct pluralization");
        first.due=-1;ok(CalendarDaySummary.tasksForMonth(Arrays.asList(first),YearMonth.from(d),zone).isEmpty(),"negative due ignored");
        System.out.println("PASS CalendarDaySummary: "+checks+" checks");
    }
}