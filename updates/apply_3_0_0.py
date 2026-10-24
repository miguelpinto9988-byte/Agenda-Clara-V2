#!/usr/bin/env python3
"""Agenda Clara 3.0.0 | Etapa 2: correlación de materias + fotos tabulares variables."""
from pathlib import Path
import textwrap
root=Path("AgendaClara")
src=root/"app/src/main/java/pe/agendaclara/app"
def java(file,value):
    (src/file).write_text(textwrap.dedent(value).lstrip(),encoding="utf-8")
def change(file,old,new):
    p=src/file;s=p.read_text(encoding="utf-8")
    if s.count(old)!=1:raise RuntimeError(f"ETAPA 2: ancla no única {file} ({s.count(old)}): {old[:85]}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

java("ScheduleCourseColors.java",r'''
package pe.agendaclara.app;
import java.text.Normalizer;
import java.util.*;
/** Identidad estable para asignaturas: curso -> múltiples sesiones en días distintos. */
public final class ScheduleCourseColors {
    private ScheduleCourseColors(){}
    public static String key(String title){
        if(title==null)return "";
        String n=Normalizer.normalize(title,Normalizer.Form.NFD)
            .replaceAll("\\p{M}+","").toLowerCase(Locale.ROOT);
        return n.replaceAll("[^\\p{L}\\p{N}]+"," ").trim().replaceAll("\\s+"," ");
    }
    /**
     * Permite únicamente pluralizaciones frecuentes sin alterar números ni sufijos
     * de romanos: 'Textos Líricos' equivale a 'Texto Lírico'; 'Historia I' != 'II'.
     * No se hace matching difuso automático cuando la materia es ambigua.
     */
    public static String identity(String title){
        String clean=key(title);if(clean.isEmpty())return clean;
        String[] words=clean.split(" ");
        for(int i=0;i<words.length;i++){
            String w=words[i];if(w.length()<5)continue;
            if((w.endsWith("os")||w.endsWith("as"))&&w.length()>4){
                words[i]=w.substring(0,w.length()-1);
            }else if(w.length()>6&&(w.endsWith("ales")||w.endsWith("iles"))){
                words[i]=w.substring(0,w.length()-2);
            }
        }
        return String.join(" ",words);
    }
    public static boolean same(String a,String b){
        String x=identity(a);return !x.isEmpty()&&x.equals(identity(b));
    }
    public static int hsv(float hue,float saturation,float brightness){
        float h=((hue%360)+360)%360,s=Math.max(0,Math.min(1,saturation)),v=Math.max(0,Math.min(1,brightness));
        float c=v*s,x=c*(1-Math.abs((h/60)%2-1)),m=v-c;float r=0,g=0,b=0;
        if(h<60){r=c;g=x;}else if(h<120){r=x;g=c;}else if(h<180){g=c;b=x;}
        else if(h<240){g=x;b=c;}else if(h<300){r=x;b=c;}else{r=c;b=x;}
        return 0xff000000|(Math.round((r+m)*255)<<16)|(Math.round((g+m)*255)<<8)|Math.round((b+m)*255);
    }
    /** 72 opciones rápidas conservadas de la versión 2.8. */
    public static int[] palette(){
        int[] shades=new int[72];int p=0;
        float[][] variants={{.64f,.96f},{.46f,.98f},{.79f,.82f},{.52f,.78f},{.35f,.93f},{.73f,.64f}};
        for(float[] variant:variants)for(int h=0;h<360;h+=30)shades[p++]=hsv(h,variant[0],variant[1]);
        return shades;
    }
    public static int accessibleText(int color){
        double r=((color>>>16)&255)/255.0,g=((color>>>8)&255)/255.0,b=(color&255)/255.0;
        r=r<=.04045?r/12.92:Math.pow((r+.055)/1.055,2.4);
        g=g<=.04045?g/12.92:Math.pow((g+.055)/1.055,2.4);
        b=b<=.04045?b/12.92:Math.pow((b+.055)/1.055,2.4);
        return .2126*r+.7152*g+.0722*b>.19?0xff101d43:0xffffffff;
    }
    public static int deterministic(String title){
        String k=identity(title);if(k.isEmpty())return 0xff4989f7;
        int hash=k.hashCode()&0x7fffffff;
        return hsv((hash%360),.53f,.92f);
    }
    public static Integer existingColor(String name,Collection<ScheduleEntry> saved){
        if(saved==null)return null;
        for(ScheduleEntry s:saved)if(same(name,s.course))return s.color;
        return null;
    }
    /**
     * Prioridad: color de materia ya guardada -> selección manual en el lote
     * -> propuesta determinista. La revisión del OCR no pierde la selección manual.
     */
    public static void align(List<ScheduleEntry> detected,Collection<ScheduleEntry> saved){
        if(detected==null)return;
        LinkedHashMap<String,Integer> colors=new LinkedHashMap<>();
        if(saved!=null)for(ScheduleEntry s:saved){
            String id=identity(s.course);if(!id.isEmpty())colors.putIfAbsent(id,s.color);
        }
        for(ScheduleEntry s:detected){
            String id=identity(s.course);
            if(id.isEmpty()||colors.containsKey(id))continue;
            if((s.color>>>24)==255&&s.color!=deterministic(s.course))
                colors.put(id,s.color);
        }
        for(ScheduleEntry s:detected){
            String id=identity(s.course);if(id.isEmpty())continue;
            Integer chosen=colors.get(id);
            if(chosen==null){chosen=deterministic(s.course);colors.put(id,chosen);}
            s.color=chosen;
        }
    }
    /** Conserva los bloques individuales; solo los presenta unidos por curso. */
    public static Map<String,List<ScheduleEntry>> groups(Collection<ScheduleEntry> sessions){
        LinkedHashMap<String,List<ScheduleEntry>> out=new LinkedHashMap<>();
        if(sessions!=null)for(ScheduleEntry s:sessions)
            out.computeIfAbsent(identity(s.course),k->new ArrayList<>()).add(s);
        return out;
    }
}
''')
# Ajustar contador de sesiones repetidas en la pantalla de revisión a la misma identidad
change("ScheduleActivity.java",
    'related.get(ScheduleCourseColors.key(s.course)).size()',
    'related.get(ScheduleCourseColors.identity(s.course)).size()')

# Mejorar lectura por geometría sin bordes: encabezados con fecha, formatos 12/24h y multilinea.
java("ScheduleVirtualGrid.java",r'''
package pe.agendaclara.app;
import java.util.*;
import java.util.regex.*;
/** Lectura conservadora de columnas sin recuadros: usuario confirma horarios OCR. */
public final class ScheduleVirtualGrid {
    private ScheduleVirtualGrid(){}
    static final class Header {
        final int day,x,y;
        Header(int day,int x,int y){this.day=day;this.x=x;this.y=y;}
    }
    static final class Period {
        final int y,start,end;
        Period(int y,int start,int end){this.y=y;this.start=start;this.end=end;}
    }
    static final class Candidate {
        int day,start,end,x,y;String text;
        Candidate(int day,int start,int end,int x,int y,String text){
            this.day=day;this.start=start;this.end=end;this.x=x;this.y=y;this.text=text;
        }
    }
    private static final Pattern DAYS=Pattern.compile(
       "^(lunes|martes|miercoles|jueves|viernes|sabado|domingo|lun|mar|mie|jue|vie|sab|dom)(?=$|\\W|\\d)");
    private static final Pattern TIMES=Pattern.compile(
       "(?i)(?<!\\d)(\\d{1,2})\\s*[:h.]\\s*([0-5]\\d)\\s*(am|pm)?\\s*(?:-|–|—|\\ba\\b|\\bhasta\\b)\\s*(\\d{1,2})\\s*[:h.]\\s*([0-5]\\d)\\s*(am|pm)?");
    private static final Pattern ROOM=Pattern.compile(
       "(?i)\\s+(aula|salon|salón|laboratorio|lab\\.?|ambiente)\\s*[#: -]*([\\p{L}\\p{N}][\\p{L}\\p{N} -]{0,30})$");
    private static int day(String raw){
        String n=ScheduleParser.fold(raw==null?"":raw).toLowerCase(Locale.ROOT).trim();
        Matcher m=DAYS.matcher(n);if(!m.find())return 0;
        String head=m.group(1);
        if(head.startsWith("lun"))return 1;
        if(head.startsWith("mar"))return 2;
        if(head.startsWith("mie"))return 3;
        if(head.startsWith("jue"))return 4;
        if(head.startsWith("vie"))return 5;
        if(head.startsWith("sab"))return 6;
        return 7;
    }
    private static int minutes(String h,String m,String meridian){
        int hour=Integer.parseInt(h),minute=Integer.parseInt(m);
        if(meridian!=null&&!meridian.isEmpty()){
            if(hour<1||hour>12)return -1;
            hour=(hour%12)+("pm".equalsIgnoreCase(meridian)?12:0);
        }
        if(hour<0||hour>23)return -1;
        return hour*60+minute;
    }
    private static Period period(ScheduleGridInterpreter.Line line,int width){
        if(line.x()>width*.33)return null;
        Matcher m=TIMES.matcher(line.text);
        if(!m.find())return null;
        int start=minutes(m.group(1),m.group(2),m.group(3));
        int end=minutes(m.group(4),m.group(5),m.group(6));
        if(start<0||end<0||end<=start||end-start>240)return null;
        return new Period(line.y(),start,end);
    }
    public static ScheduleParser.Result parse(List<ScheduleGridInterpreter.Line> lines,int width,int height){
        ScheduleParser.Result out=new ScheduleParser.Result();
        if(lines==null||width<150||height<150)return out;
        List<Header> headers=new ArrayList<>();List<Period> periods=new ArrayList<>();
        for(ScheduleGridInterpreter.Line l:lines){
            int d=day(l.text);
            if(d>0&&l.y()<height*.40)headers.add(new Header(d,l.x(),l.y()));
            Period p=period(l,width);if(p!=null)periods.add(p);
        }
        headers.sort(Comparator.comparingInt(h->h.x));
        List<Header> distinctHeaders=new ArrayList<>();Set<Integer> seenDays=new HashSet<>();
        for(Header h:headers)if(seenDays.add(h.day))distinctHeaders.add(h);
        headers=distinctHeaders;
        periods.sort(Comparator.comparingInt(p->p.y));
        List<Period> distinctPeriods=new ArrayList<>();Set<String> timeKeys=new HashSet<>();
        for(Period p:periods)if(timeKeys.add(p.start+":"+p.end))distinctPeriods.add(p);
        periods=distinctPeriods;
        if(headers.size()<2||periods.size()<2)return out;
        int maxHeaderY=0;for(Header h:headers)maxHeaderY=Math.max(maxHeaderY,h.y);
        int sum=0;for(int i=1;i<periods.size();i++)sum+=periods.get(i).y-periods.get(i-1).y;
        int rowHeight=Math.max(18,sum/Math.max(1,periods.size()-1));
        List<Candidate> parts=new ArrayList<>();
        for(ScheduleGridInterpreter.Line line:lines){
            String caption=line.text==null?"":line.text.trim();
            if(caption.length()<3||caption.length()>110||line.y()<maxHeaderY+6)continue;
            if(day(caption)>0&&caption.length()<25)continue;
            if(TIMES.matcher(caption).find())continue;
            if(line.x()<width*.14)continue; // descarta horas y leyenda lateral
            Header nearest=null;int dx=Integer.MAX_VALUE;
            for(Header h:headers){int distance=Math.abs(line.x()-h.x);
                if(distance<dx){dx=distance;nearest=h;}}
            if(nearest==null||dx>Math.max(width/10,rowHeight*2))continue;
            Period slot=null;int dy=Integer.MAX_VALUE;
            for(Period p:periods){int distance=Math.abs(line.y()-p.y);
                if(distance<dy){dy=distance;slot=p;}}
            if(slot==null||dy>rowHeight*.68f)continue;
            parts.add(new Candidate(nearest.day,slot.start,slot.end,line.x(),line.y(),caption));
        }
        parts.sort(Comparator.comparingInt((Candidate c)->c.day)
             .thenComparingInt(c->c.start).thenComparingInt(c->c.y).thenComparingInt(c->c.x));
        LinkedHashMap<String,List<Candidate>> buckets=new LinkedHashMap<>();
        for(Candidate c:parts)buckets.computeIfAbsent(c.day+"/"+c.start+"/"+c.end,
                k->new ArrayList<>()).add(c);
        Set<String> unique=new HashSet<>();
        for(List<Candidate> bucket:buckets.values()){
            if(bucket.isEmpty())continue;
            Candidate first=bucket.get(0);
            StringBuilder title=new StringBuilder();
            int previousY=Integer.MIN_VALUE;
            for(Candidate part:bucket){
                // OCR puede emitir la misma palabra dos veces; conserva su posición única.
                if(previousY==part.y&&title.toString().endsWith(part.text))continue;
                if(title.length()>0)title.append(' ');
                title.append(part.text);previousY=part.y;
            }
            String name=title.toString().replaceAll("\\s+"," ").trim();
            if(name.isEmpty())continue;
            ScheduleEntry session=new ScheduleEntry();
            session.day=first.day;session.start=first.start;session.end=first.end;
            Matcher location=ROOM.matcher(name);
            if(location.find()&&location.start()>2){
                session.course=name.substring(0,location.start()).trim();
                session.room=location.group().trim();
            }else session.course=name;
            session.color=ScheduleCourseColors.deterministic(session.course);
            String uniqueKey=session.day+"/"+session.start+"/"+
                ScheduleCourseColors.identity(session.course);
            if(unique.add(uniqueKey))out.candidates.add(session);
        }
        if(!out.candidates.isEmpty()){
            out.uncertain.add("Foto sin cuadrícula clara: los bloques se estimaron por posición. Revisa el día, aula y duración antes de importar.");
            out.uncertain.add("Los títulos partidos en varias líneas se han unido por franja horaria. Confirma si pertenecen a la misma asignatura.");
        }
        return out;
    }
}
''')
# En la interfaz de edición, la preferencia manual seleccionada se mantiene al importar
# y las materias normalizadas se vinculan aunque tengan singular/plural.
change("ScheduleActivity.java",
    'if(detected!=null){for(ScheduleEntry linked:detected.candidates)if(ScheduleCourseColors.same(current.course,linked.course))linked.color=current.color;}',
    'if(detected!=null){for(ScheduleEntry linked:detected.candidates)if(ScheduleCourseColors.same(current.course,linked.course))linked.color=current.color;}')

gradle=root/"app/build.gradle"
s=gradle.read_text(encoding="utf-8")
if s.count("versionCode 19")!=1 or s.count("versionName '2.9.0'")!=1:
    raise RuntimeError("ETAPA 2: requiere 2.9.0")
gradle.write_text(s.replace("versionCode 19","versionCode 20").replace("versionName '2.9.0'","versionName '3.0.0'"),encoding="utf-8")
print("ETAPA_2_COMPLETADA: mismo curso y color por sesión, fotos sin cuadrícula, fechas junto a días y formatos AM/PM.")
