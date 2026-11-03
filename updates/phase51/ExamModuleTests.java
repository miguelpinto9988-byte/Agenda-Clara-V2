import pe.agendaclara.app.SyllabusInterpreter;
import java.util.*;
import java.time.*;
public final class ExamModuleTests {
 static int checks=0;static void yes(boolean b,String s){checks++;if(!b)throw new AssertionError(s);}
 public static void main(String[] args){
  String doc="Curso: Historia\nPrimer examen parcial: 15 de mayo de 2027 a las 14:30\nSegunda evaluación parcial semana 12\nExamen final: 18/07/2027 a las 3 pm";
  var p=SyllabusInterpreter.detect(doc,Arrays.asList("Historia"),LocalDate.of(2027,3,1));
  yes(p.size()==3,"three evaluations");
  yes("Historia".equals(p.get(0).course),"course reuse");
  yes(p.get(0).date.equals(LocalDate.of(2027,5,15)),"first date");
  yes(p.get(0).time.equals(LocalTime.of(14,30)),"first time");
  yes(p.get(1).date==null&&p.get(1).warning.contains("Semana 12"),"do not inherit prior exam date");
  yes(p.get(2).date.equals(LocalDate.of(2027,7,18)),"final date");
  yes(p.get(2).time.equals(LocalTime.of(15,0)),"final time");
  yes(SyllabusInterpreter.detect("El examen final fue cancelado",Arrays.asList("Historia"),LocalDate.now()).isEmpty(),"do not save canceled exam");
  yes(SyllabusInterpreter.detect("Reunión del grupo el jueves",Arrays.asList("Historia"),LocalDate.now()).isEmpty(),"no spurious exam");
  yes(SyllabusInterpreter.detect("Examen el 31/02/2027",Collections.emptyList(),LocalDate.now()).get(0).date==null,"invalid date");
  yes(SyllabusInterpreter.detect("Evaluación 12 de octubre",Collections.emptyList(),LocalDate.now()).get(0).date==null,"missing year stays uncertain");
  System.out.println("PASS academic exams: "+checks+" conservative extraction checks");
 }
}
