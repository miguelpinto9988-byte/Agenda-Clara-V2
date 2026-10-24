import pe.agendaclara.app.*;
import java.time.*;
import java.util.*;
public final class Phase7Tests {
 static int checks;
 static void test(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
 static Task task(LocalDate day,boolean done,ZoneId z){
  Task t=new Task();t.due=day.atTime(9,0).atZone(z).toInstant().toEpochMilli();t.done=done;return t;
 }
 public static void main(String[] args){
  ZoneId zone=ZoneId.of("America/Lima");
  LocalDate wed=LocalDate.of(2026,10,21);
  LocalDate monday=WeeklyPlanner.monday(wed);
  test(monday.equals(LocalDate.of(2026,10,19)),"Monday boundary");
  List<Task> tasks=Arrays.asList(task(monday,false,zone),task(monday.plusDays(6),false,zone),task(monday.plusDays(2),true,zone),task(monday.minusDays(1),false,zone),task(monday.plusDays(7),false,zone));
  int[] totals=WeeklyPlanner.pendingByDay(tasks,monday,zone);
  test(totals.length==7,"Seven days");
  test(totals[0]==1,"Monday");
  test(totals[6]==1,"Sunday");
  test(totals[2]==0,"Done not scheduled");
  test(WeeklyPlanner.count(totals)==2,"Only week pending");
  test(WeeklyPlanner.count(WeeklyPlanner.pendingByDay(Collections.emptyList(),monday,zone))==0,"Empty week");
  test(WeeklyPlanner.monday(monday.plusDays(6)).equals(monday),"Sunday same week");
  System.out.println("PASS: "+checks+" weekly planner JVM checks");
 }
}