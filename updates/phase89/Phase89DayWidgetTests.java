package pe.agendaclara.app;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
public final class Phase89DayWidgetTests{
 private static void check(boolean value,String message){
  if(!value)throw new AssertionError(message);
 }
 private static ScheduleEntry s(String name,int day,int start,boolean enabled){
  ScheduleEntry e=new ScheduleEntry();e.course=name;e.day=day;e.start=start;
  e.end=start+90;e.enabled=enabled;return e;
 }
 public static void main(String[] args){
  LocalDate day=LocalDate.of(2026,11,2);
  List<ScheduleEntry> entries=Arrays.asList(
   s("Curso de mañana",1,720,true),s("Otro día",2,600,true),
   s("Curso temprano",1,480,true),s("Desactivado",1,430,false),
   s("Curso tarde",1,930,true));
  List<ScheduleEntry> out=AcademicDayWidgetData.today(entries,day);
  check(out.size()==3,"Must count three real classes");
  check("Curso temprano".equals(out.get(0).course),"Sort early first");
  check("Curso de mañana".equals(out.get(1).course),"Sort next class second");
  check(AcademicDayWidgetData.today(entries,day.plusDays(2)).isEmpty(),
   "Do not fabricate unrelated-day classes");
  check("1 clase hoy".equals(AcademicDayWidgetData.countLabel(1)),
   "Singular grammar");
  check("0 clases hoy".equals(AcademicDayWidgetData.countLabel(0)),
   "Empty schedule count");
  check("Aula 203".equals(AcademicDayWidgetData.roomLabel("203")),
   "Room prefix");
  check("Aula 203".equals(AcademicDayWidgetData.roomLabel("Aula 203")),
   "No duplicate Aula");
  check("Aula por confirmar".equals(AcademicDayWidgetData.roomLabel("")),
   "Never fabricate room");
  System.out.println("PASS: course order, active profile day, exact class counts, room safety");
 }
}