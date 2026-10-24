package pe.agendaclara.app;
import java.util.*;
public final class MultiActivityInterpreterTest {
 public static void main(String[] args){
  List<MultiActivityInterpreter.Candidate> a=MultiActivityInterpreter.extract("1. Mañana exposición de Historia a las 9:00. 2. El viernes entregar informe de Psicología a las 18:00; además el lunes examen de Matemática.");
  if(a.size()!=3)throw new AssertionError("Expected three activities, got "+a.size());
  if(!a.get(0).kind.equals("EXPOSICION"))throw new AssertionError("exposition");
  if(!a.get(1).kind.equals("ENTREGA"))throw new AssertionError("delivery");
  if(!a.get(2).kind.equals("EVALUACION"))throw new AssertionError("exam");
  if(!MultiActivityInterpreter.extract("No hay examen mañana. Se canceló la exposición.").isEmpty())throw new AssertionError("negation");
  if(!MultiActivityInterpreter.extract("Hola, qué tal, gracias").isEmpty())throw new AssertionError("chat");
  if(!a.get(0).requiresReview)throw new AssertionError("review mandatory");
  System.out.println("PASS multi activity interpretation");
 }
}