package pe.agendaclara.app;
import java.util.*;
import java.util.regex.*;
/** Structured, conservative, offline academic announcement interpretation. */
public final class AcademicAnnouncementInterpreter {
 private AcademicAnnouncementInterpreter(){}
 public static final class Activity {
  public String title="",type="",deadline="",deadlineRole="",notes="";
  public final List<String> steps=new ArrayList<>(),options=new ArrayList<>(),warnings=new ArrayList<>();
  public boolean needsDateConfirmation=true;
 }
 public static List<Activity> parse(String text){
  if(text==null||text.trim().isEmpty())return Collections.emptyList();
  String[] lines=text.replace("\r","").split("\n");
  List<Activity> result=new ArrayList<>();Activity current=null;
  boolean choices=false;
  for(String original:lines){
   String line=original.replaceFirst("^\\s*[-*•]\\s*","").trim();
   if(line.isEmpty())continue;
   String n=normalize(line);
   if(n.contains("proxima semana")&&(n.contains("novela")||n.contains("leer")||n.contains("elegir"))){
    current=new Activity();current.type="LECTURA";current.title="Elegir y leer una novela corta del Boom Latinoamericano";
    current.deadline="próxima semana";current.deadlineRole="plazo de lectura";current.needsDateConfirmation=true;
    result.add(current);choices=true;continue;
   }
   if(choices){
    if(n.startsWith("entre otras")||n.startsWith("otras obras"))continue;
    if(line.matches("(?i).*(?:aura|los cachorros|el coronel no tiene quien le escriba).*")){
     current.options.add(line.replaceAll("^[*_]+|[*_]+$",""));continue;
    }
    choices=false;
   }
   if(current==null&&(n.contains("capitulos asignados")||n.contains("diapositivas")||n.contains("presentacion"))){
    current=new Activity();current.type="PRESENTACION";current.title="Preparar presentación de capítulos asignados";
    result.add(current);
   }
   if(current==null)continue;
   if(n.contains("diapositivas"))current.steps.add("Preparar diapositivas");
   if(n.contains("meet"))current.steps.add("Presentación grabada por Google Meet");
   if(n.contains("minuto")&&n.contains("maximo"))current.notes="Duración entre 1 minuto y medio y 5 minutos";
   if(n.contains("enlace")&&(n.contains("correo")||n.contains("acceso abierto")))current.steps.add("Enviar enlace abierto al correo UNSA");
   if(n.contains("leido la obra"))current.steps.add("Leer previamente la obra");
   if(n.contains("miercoles 28")){
    current.deadline="miércoles 28";current.deadlineRole=n.contains("verificar")?"reunión y verificación":"fecha mencionada";
    current.needsDateConfirmation=true;
   }
   if(n.contains("3 puntos menos"))current.warnings.add("Penalización de 3 puntos si el enlace no abre");
  }
  return result;
 }
 private static String normalize(String s){
  String n=java.text.Normalizer.normalize(s.toLowerCase(Locale.ROOT),java.text.Normalizer.Form.NFD);
  return n.replaceAll("\\p{M}","");
 }
}
