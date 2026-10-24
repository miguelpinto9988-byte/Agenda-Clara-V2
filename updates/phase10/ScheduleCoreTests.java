import pe.agendaclara.app.*;
public final class ScheduleCoreTests {
 static int count=0;static void check(boolean ok,String msg){count++;if(!ok)throw new AssertionError(msg);}
 public static void main(String[] args){
  check(ScheduleEntry.minutes("08:30")==510,"hour");check(ScheduleEntry.minutes("24:00")==-1,"hour invalid");check(ScheduleEntry.minutes("8.45")==525,"dot hour");
  ScheduleParser.Result result=ScheduleParser.parse("Lunes 08:00-09:00 Matemáticas Aula 101\nMartes Biología 10:00-11:30 Laboratorio");
  check(result.candidates.size()==2,"recognize two classes");
  check(result.candidates.get(0).day==1,"Monday");
  check(result.candidates.get(0).course.toLowerCase().contains("matem"),"subject retained");
  check(result.candidates.get(0).room.toLowerCase().contains("aula"),"location retained");
  check(result.candidates.get(1).end==690,"end time");
  ScheduleParser.Result dup=ScheduleParser.parse("Lunes 08:00-09:00 Matemáticas Aula 101\nLunes 08:00-09:00 Matemáticas Aula 101");
  check(dup.candidates.size()==1,"deduplication");
  ScheduleParser.Result missing=ScheduleParser.parse("08:00-09:00 Matemáticas");
  check(missing.candidates.isEmpty()&&!missing.uncertain.isEmpty(),"uncertain day not invented");
  ScheduleParser.Result bad=ScheduleParser.parse("Viernes Biología 11:00-09:00");
  check(bad.candidates.isEmpty(),"negative duration");
  ScheduleParser.Result separate=ScheduleParser.parse("Miércoles\n08:00-09:30 Literatura Aula 3");
  check(separate.candidates.size()==1&&separate.candidates.get(0).day==3,"day headings");
  ScheduleEntry s=new ScheduleEntry();s.course="Literatura";s.day=3;s.start=480;s.end=540;
  check(ScheduleEntry.valid(s),"valid session");
  s.start=600;check(!ScheduleEntry.valid(s),"reverse session");
  System.out.println("PASS: "+count+" class timetable JVM regression checks");
 }
}