import pe.agendaclara.app.*;
import java.util.*;
public class Phase13CoreTest {
  static int cases=0;
  static void ok(boolean b,String name){cases++;if(!b)throw new AssertionError(name);}
  static ScheduleEntry entry(String name,int day,int start,int end){ScheduleEntry e=new ScheduleEntry();e.course=name;e.day=day;e.start=start;e.end=end;return e;}
  public static void main(String[] args){
    ok(ScheduleCourseColors.palette().length==72,"72 swatches");
    Set<Integer> shades=new HashSet<>();for(int v:ScheduleCourseColors.palette())shades.add(v);
    ok(shades.size()==72,"all swatches distinct");
    ok(ScheduleCourseColors.hsv(0,1,1)==0xffff0000,"HSV red");
    ok(ScheduleCourseColors.hsv(120,1,1)==0xff00ff00,"HSV green");
    ok(ScheduleCourseColors.hsv(240,1,1)==0xff0000ff,"HSV blue");
    ok(ScheduleCourseColors.hsv(360,1,1)==0xffff0000,"HSV wrap");
    ok(ScheduleCourseColors.accessibleText(0xff000000)==0xffffffff,"white on black");
    ok(ScheduleCourseColors.accessibleText(0xffffffff)==0xff101d43,"dark on white");
    ok(ScheduleCourseColors.same("Textos Líricos"," TEXTOS  LIRICOS "),"accent,case,spaces");
    ok(ScheduleCourseColors.same("Tendencias Educativas (E)","TENDENCIAS educativas E"),"punctuation");
    ok(!ScheduleCourseColors.same("Didáctica de la Lengua y Literatura II","Didáctica de la Lengua y Literatura I"),"preserve roman numerals");
    ok(!ScheduleCourseColors.same("Historia", "Historias"),"do not join similar courses");
    List<ScheduleEntry> e=new ArrayList<>();e.add(entry("Textos Líricos",2,420,520));e.add(entry("textos liricos",4,600,700));e.add(entry("Recursos Digitales",1,420,520));
    ScheduleCourseColors.align(e,Collections.emptyList());
    ok(e.get(0).color==e.get(1).color,"same course matching colors");
    ok(ScheduleCourseColors.groups(e).size()==2,"2 courses 3 sessions");
    List<ScheduleEntry> saved=Arrays.asList(entry("TEXTOS LIRICOS",5,680,730));saved.get(0).color=0xff123456;
    ScheduleCourseColors.align(e,saved);
    ok(e.get(0).color==0xff123456&&e.get(1).color==0xff123456,"preserve user color");
    ok(e.get(2).color!=0xff123456,"other course retains independent color");
    // No detected cell boundaries; derive candidate rows from weekday X and ruler Y.
    List<ScheduleGridInterpreter.Line> lines=Arrays.asList(
      new ScheduleGridInterpreter.Line("LUNES",250,60,315,85),
      new ScheduleGridInterpreter.Line("MARTES",360,60,440,85),
      new ScheduleGridInterpreter.Line("MIÉRCOLES",490,60,620,85),
      new ScheduleGridInterpreter.Line("08:00 - 08:50",20,180,170,205),
      new ScheduleGridInterpreter.Line("09:00 - 09:50",20,255,170,280),
      new ScheduleGridInterpreter.Line("10:00 - 10:50",20,335,170,360),
      new ScheduleGridInterpreter.Line("Textos Líricos",360,180,450,205),
      new ScheduleGridInterpreter.Line("Tutoría Educativa",250,260,315,280),
      new ScheduleGridInterpreter.Line("Recursos Digitales",500,335,620,360)
    );
    ScheduleParser.Result v=ScheduleVirtualGrid.parse(lines,900,650);
    ok(v.candidates.size()==3,"fallback recognize 3 single-row cells: "+v.candidates.size());
    ok(!v.uncertain.isEmpty(),"fallback warns duration uncertainty");
    ok(v.candidates.stream().anyMatch(s->s.day==2&&s.start==480&&s.end==530),"Tuesday date/time");
    ok(v.candidates.stream().noneMatch(s->s.end-s.start>50),"no invented multi row");
    ok(ScheduleVirtualGrid.parse(lines.subList(0,3),900,650).candidates.isEmpty(),"no time ruler => no guesses");
    System.out.println("PASS: "+cases+" phase13 schedule palette, identity, virtual-grid safety tests");
  }
}