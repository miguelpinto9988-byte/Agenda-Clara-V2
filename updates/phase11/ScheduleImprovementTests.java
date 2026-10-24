import pe.agendaclara.app.*;
import java.util.*;
import java.time.*;
public final class ScheduleImprovementTests {
 static int n=0;static void ok(boolean value,String note){n++;if(!value)throw new AssertionError(note);}
 static ScheduleEntry session(String course,int day,int start,int end){
    ScheduleEntry e=new ScheduleEntry();e.course=course;e.day=day;e.start=start;e.end=end;return e;
 }
 public static void main(String[] args){
    ScheduleEntry a=session("Álgebra",1,480,540),b=session("Historia",1,520,580),
                  c=session("Comunicación",2,480,540),d=session("Literatura",1,540,600);
    ok(ScheduleConflict.overlaps(a,b),"mismo día y minutos compartidos");
    ok(!ScheduleConflict.overlaps(a,c),"diferente día");
    ok(!ScheduleConflict.overlaps(a,d),"clases consecutivas");
    ok(ScheduleConflict.describe(Arrays.asList(a,b),Collections.emptyList()).size()==1,"aviso entre dos nuevas clases");
    a.id=12;b.id=12;ok(!ScheduleConflict.overlaps(a,b),"edición no colisiona con sí misma");
    ZoneId zone=ZoneId.of("America/Lima");ScheduleEntry monday=session("Taller",1,480,540);monday.reminder=10;
    Instant mondayMorning=ZonedDateTime.of(2026,10,19,7,0,0,0,zone).toInstant();
    ZonedDateTime due=SchedulePeriod.next(monday,mondayMorning,zone,null,null);
    ok(due!=null&&due.getHour()==7&&due.getMinute()==50,"recuerda 10 minutos antes");
    ok(SchedulePeriod.next(monday,mondayMorning,zone,LocalDate.of(2026,10,26),LocalDate.of(2026,11,2)).toLocalDate().equals(LocalDate.of(2026,10,26)),"respeta inicio");
    ok(SchedulePeriod.next(monday,mondayMorning,zone,null,LocalDate.of(2026,10,18))==null,"semestre finalizado");
    ok(SchedulePeriod.next(monday,ZonedDateTime.of(2026,10,19,9,0,0,0,zone).toInstant(),zone,LocalDate.of(2026,10,19),LocalDate.of(2026,10,19))==null,"sin aviso después del cierre");
    System.out.println("PASS: "+n+" horario 2.6.1: cruces y periodo académico");
 }
}