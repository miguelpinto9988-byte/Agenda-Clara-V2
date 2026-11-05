package pe.agendaclara.app;

import java.text.Normalizer;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Conservative syllabus event post-processor. It adds no speculative due dates
 * and never converts ordinary homework into a final assessment.
 */
public final class SyllabusReviewIntelligence {
    private SyllabusReviewIntelligence(){}
    private static final Pattern EXAM=Pattern.compile(
        "\\b(examen(?:es)?|parcial(?:es)?|sustitutorio|recuperacion|"+
        "extraordinario|aplazado|evaluacion\\s+(?:oral|escrita|practica|"+
        "parcial|final)|practica\\s+calificada|control\\s+de\\s+lectura)\\b");
    private static final Pattern FINAL=Pattern.compile(
        "\\b(trabajo|producto|proyecto|informe|entregable|portafolio|"+
        "presentacion|sustentacion|exposicion)\\s+(?:integrador|integrador[ao]s|"+
        "final|finales|de\\s+cierre)\\b|"+
        "\\b(?:entrega|presentacion|sustentacion|exposicion)\\s+(?:del?\\s+)?"+
        "(?:trabajo|producto|proyecto|portafolio)\\s+final\\b");
    private static final Pattern NEGATIVE=Pattern.compile(
        "\\b(bibliografia|referencias|competencias|resultados\\s+de\\s+aprendizaje|"+
        "criterios\\s+de\\s+evaluacion|sistema\\s+de\\s+evaluacion|"+
        "ponderacion|metodologia|requisitos|politicas|descripcion\\s+del\\s+curso)\\b");
    private static final Pattern WEEK=Pattern.compile(
        "\\b(?:semana(?:s)?|sem\\.?|unidad\\s+semanal)\\s*"+
        "(?:academica(?:s)?\\s*)?(?:n[.º°o]*\\s*)?"+
        "([0-9]{1,2}|[ivxlcdm]{1,8})\\b");
    private static final Pattern WEIGHT=Pattern.compile(
        "(?<![0-9])([0-9]{1,3})(?:[.,]([0-9]{1,2}))?\\s*%");
    public static final class Review {
        public final SyllabusEventParser.Event event;
        public final int week,weight;
        public final String dateEvidence;
        public final boolean dateConfirmed;
        public final String kind;
        Review(SyllabusEventParser.Event e,int w,int p,String evidence,String kind){
            event=e;week=w;weight=p;dateEvidence=evidence;
            dateConfirmed=e.date!=null;this.kind=kind;
        }
    }
    public static String fold(String input){
        if(input==null)return "";
        return Normalizer.normalize(input.toLowerCase(Locale.ROOT),Normalizer.Form.NFD)
                .replaceAll("\\p{M}+","").replaceAll("\\s+"," ").trim();
    }
    public static int week(String input){
        Matcher m=WEEK.matcher(fold(input));
        if(!m.find())return 0;
        String n=m.group(1);
        try{
            int w=n.matches("[0-9]+")?Integer.parseInt(n):roman(n);
            return w>=1&&w<=53?w:0;
        }catch(RuntimeException ignored){return 0;}
    }
    private static int roman(String s){
        int value=0,previous=0;
        for(int i=s.length()-1;i>=0;i--){
            int n="ivxlcdm".indexOf(s.charAt(i));
            int v=n==0?1:n==1?5:n==2?10:n==3?50:n==4?100:n==5?500:n==6?1000:0;
            if(v==0)return 0;
            value+=v<previous?-v:v;previous=v;
        }
        return value;
    }
    public static int weight(String text){
        Matcher m=WEIGHT.matcher(text==null?"":text);
        if(!m.find())return -1;
        int p=Integer.parseInt(m.group(1));
        return p<=100?p:-1;
    }
    public static String classify(String input){
        String s=fold(input);
        if(s.isEmpty())return "";
        // A heading that explains the grading system is not an event.
        if(NEGATIVE.matcher(s).find() && !s.matches(".*\\b(?:semana|fecha|dia)\\b.*"))
            return "";
        if(FINAL.matcher(s).find())return "Producto final";
        if(EXAM.matcher(s).find())return "Examen";
        return "";
    }
    public static List<Review> filter(List<SyllabusEventParser.Event> events){
        ArrayList<Review> out=new ArrayList<>();
        Set<String> seen=new HashSet<>();
        if(events==null)return out;
        for(SyllabusEventParser.Event e:events){
            if(e==null)continue;
            String evidence=e.sourceText==null?"":e.sourceText;
            String kind=classify(evidence+" "+e.type);
            if(kind.isEmpty())continue;
            int w=week(evidence);
            int p=weight(evidence);
            String dateEvidence=e.date==null?(w>0?"Semana académica "+w+
                " · día sin confirmar":"Fecha pendiente de confirmar"):
                "Fecha explícita o calculada por el lector: "+e.date;
            String fingerprint=fold(e.title)+"|"+(e.date==null?"?":e.date)+
                    "|"+w+"|"+e.page;
            if(!seen.add(fingerprint))continue;
            out.add(new Review(e,w,p,dateEvidence,kind));
        }
        return out;
    }
}
