package pe.agendaclara.app;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;

/** Offline, deterministic extraction of several independent activities from one WhatsApp message.
 * Produces review-only candidates; never saves tasks or reads WhatsApp directly. */
public final class MultiActivityInterpreter {
 private MultiActivityInterpreter(){}
 public static final class Candidate {
  public final String text,kind,dateHint,timeHint,course;
  public final int confidence;
  public final boolean requiresReview;
  Candidate(String t,String k,String d,String h,String c,int score){
   text=t;kind=k;dateHint=d;timeHint=h;course=c;confidence=Math.max(0,Math.min(100,score));requiresReview=true;
  }
 }
 private static final Pattern START=Pattern.compile("(?i)(?:^|[.!?;\\n]+|(?:\\s+)(?:adem[aá]s|por otro lado|tambi[eé]n|otra actividad|segunda actividad|luego|aparte)[:,]?\\s+|\\s+(?=\\d+[.)]\\s))");
 private static final Pattern INTENT=Pattern.compile("(?i)\\b(tarea|entrega|entregar|presentar|presentaci[oó]n|exposici[oó]n|exponer|examen|evaluaci[oó]n|prueba|control de lectura|reuni[oó]n|clase|taller|pr[aá]ctica|proyecto|trabajo|informe|ensayo|investigaci[oó]n|lectura|actividad|llevar|traer|enviar|subir|hacer|realizar|resolver|estudiar|repasar|completar|asistir|participar|debate|sustentaci[oó]n|cuestionario|foro|laboratorio)\\b");
 private static final Pattern DATE=Pattern.compile("(?i)\\b(hoy|ma[ñn]ana|pasado ma[ñn]ana|lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo|pr[oó]xim[oa]|esta semana|la otra semana|\\d{1,2}[/-]\\d{1,2}(?:[/-]\\d{2,4})?|\\d{1,2} de [a-záéíóú]+)\\b");
 private static final Pattern TIME=Pattern.compile("(?i)\\b(?:a las|desde las|hasta las|a partir de las)?\\s*(?:[01]?\\d|2[0-3])[:.]\\d{2}\\s*(?:am|pm|a\\.?m\\.?|p\\.?m\\.?)?\\b|\\b(?:a las|desde las|hasta las)\\s*\\d{1,2}\\s*(?:am|pm|de la mañana|de la tarde|de la noche)\\b");
 private static final Pattern NEG=Pattern.compile("(?i)\\b(no (?:hay|habr[aá]|tenemos|toca|deben|se debe)|cancelad[oa]|suspendid[oa]|se pospone|ya no|fue anulad[oa]|no es obligatorio|solo era un ejemplo|era broma)\\b");
 private static final Pattern COURSE=Pattern.compile("(?i)\\b(?:curso|materia|asignatura|de|para)\\s+(?:de\\s+)?([\\p{L}][\\p{L} ]{2,35})");
 private static final Pattern CHANGE=Pattern.compile("(?i)\\b(?:cambi[oó]|correcci[oó]n|rectific[oó]|en vez de|mejor dicho|ahora ser[aá]|se reprogram[oó])\\b");
 public static List<Candidate> extract(String message){
  if(message==null||message.trim().isEmpty())return Collections.emptyList();
  String normalized=message.replace("\r\n","\n").replace('\r','\n').replaceAll("[ \\t]+"," ").trim();
  if(normalized.length()>20000)normalized=normalized.substring(0,20000);
  String[] parts=START.split(normalized);
  List<Candidate> result=new ArrayList<>();
  String inheritedDate="",inheritedCourse="";
  for(String raw:parts){
   String part=raw.replaceFirst("^\\s*[-*•]\\s*","").replaceFirst("^\\d+[.)]\\s*","").trim();
   if(part.isEmpty())continue;
   String date=match(DATE,part),time=match(TIME,part),course=matchGroup(COURSE,part);
   if(!date.isEmpty())inheritedDate=date;
   if(!course.isEmpty())inheritedCourse=course;
   if(!INTENT.matcher(part).find())continue;
   if(NEG.matcher(part).find())continue;
   String kind=kind(part);
   int score=48+(date.isEmpty()?0:16)+(time.isEmpty()?0:12)+(course.isEmpty()?0:8)+(part.length()>25?7:0);
   if(CHANGE.matcher(part).find())score-=15;
   result.add(new Candidate(part,kind,date.isEmpty()?inheritedDate:date,time,course.isEmpty()?inheritedCourse:course,score));
  }
  return Collections.unmodifiableList(result);
 }
 private static String match(Pattern p,String s){Matcher m=p.matcher(s);return m.find()?m.group().trim():"";}
 private static String matchGroup(Pattern p,String s){Matcher m=p.matcher(s);return m.find()?m.group(1).trim():"";}
 private static String kind(String s){
  String n=Normalizer.normalize(s.toLowerCase(Locale.ROOT),Normalizer.Form.NFD).replaceAll("\\p{M}","");
  if(n.matches("(?s).*(examen|evaluacion|prueba|control de lectura).*"))return "EVALUACION";
  if(n.matches("(?s).*(exposicion|exponer|presentacion|sustentacion).*"))return "EXPOSICION";
  if(n.matches("(?s).*(reunion|asistir|taller|debate).*"))return "EVENTO";
  if(n.matches("(?s).*(entrega|entregar|enviar|subir|presentar).*"))return "ENTREGA";
  return "TAREA";
 }
}
