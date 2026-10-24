import java.util.*;
import pe.agendaclara.app.*;
public final class ScheduleStage14Test {
  static int checks=0;
  static void ok(boolean yes,String note){checks++;if(!yes)throw new AssertionError(note);}
  static ScheduleEntry s(String name,int day,int color){
    ScheduleEntry item=new ScheduleEntry();item.course=name;item.day=day;
    item.start=480;item.end=540;item.color=color;return item;
  }
  static ScheduleGridInterpreter.Line line(String text,int x,int y){
    return new ScheduleGridInterpreter.Line(text,x,y,x+100,y+20);
  }
  public static void main(String[] args){
    int[] shades=ScheduleColorSpectrum.palette();
    ok(shades.length==360,"360 colores");
    ok(new HashSet<Integer>(){{for(int shade:shades)add(shade);}}.size()==360,"360 colores distintos");
    ok(ScheduleColorSpectrum.parseHex("#A1B2C3")==0xffa1b2c3,"HEX con #");
    ok(ScheduleColorSpectrum.parseHex("0000FF")==0xff0000ff,"HEX sin #");
    boolean invalid=false;try{ScheduleColorSpectrum.parseHex("#GGZZYY");}catch(IllegalArgumentException ex){invalid=true;}
    ok(invalid,"hex invalido rechazado");
    ok(ScheduleCourseColors.same("Textos Líricos","Texto Lírico"),"variacion de singular/plural");
    ok(ScheduleCourseColors.same("CURSOS DIGITALES","Curso Digital"),"singular y plural en 2 tokens");
    ok(!ScheduleCourseColors.same("Historia I","Historia II"),"no mezclar ordinales");
    List<ScheduleEntry> classes=new ArrayList<>();
    classes.add(s("Texto Lírico",1,0xff4186a1));
    classes.add(s("Textos Líricos",4,ScheduleCourseColors.deterministic("Textos Líricos")));
    ScheduleCourseColors.align(classes,Collections.emptyList());
    ok(classes.get(1).color==0xff4186a1,"preferencia manual arrastrada a otra sesion");
    ok(ScheduleCourseColors.groups(classes).size()==1,"un curso con dos dias");
    ScheduleEntry saved=s("texto lirico",5,0xffce79fa);
    ScheduleCourseColors.align(classes,Arrays.asList(saved));
    ok(classes.get(0).color==0xffce79fa&&classes.get(1).color==0xffce79fa,
       "color previamente guardado prevalece");
    List<ScheduleGridInterpreter.Line> lines=Arrays.asList(
      line("Lunes 22/10",220,65),line("Martes 23/10",370,65),line("Miércoles 24/10",530,65),
      line("08:00 AM - 09:00 AM",14,158),line("09:00 AM - 10:00 AM",14,250),
      line("Textos Líricos",220,158),line("Texto Lírico",370,158),
      line("Didáctica",530,250)
    );
    ScheduleParser.Result r=ScheduleVirtualGrid.parse(lines,900,650);
    ok(r.candidates.size()==3,"titulos fechas 12 horas y multiples columnas: "+r.candidates.size());
    ok(r.candidates.get(0).start==480&&r.candidates.get(0).end==540,"horas AM interpretadas");
    ok(r.candidates.get(0).color==r.candidates.get(1).color,"OCR asigna color correlacionado");
    ok(!r.uncertain.isEmpty(),"revision explicita OCR");
    ok(ScheduleVirtualGrid.parse(lines.subList(0,3),900,650).candidates.isEmpty(),
       "sin horas verificadas no fabricar bloques");
    System.out.println("PASS: "+checks+" pruebas etapas 1+2, 360 colores, identidad y OCR");
  }
}
