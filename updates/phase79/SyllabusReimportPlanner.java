package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Previews re-imports without writing tasks.
 * Caller supplies only tasks linked to the chosen profile AND course.
 * Never updates or merges an existing task without confirmation.
 */
public final class SyllabusReimportPlanner {
    private SyllabusReimportPlanner(){}
    public enum Status { NEW, UNCHANGED, CHANGED, AMBIGUOUS }
    public static final class Existing {
        public final long id,due;
        public final String title,type,document;
        public Existing(long id,String title,String type,long due,String document){
            this.id=id;this.title=title==null?"":title;
            this.type=type==null?"":type;
            this.due=due;this.document=document==null?"":document;
        }
    }
    public static final class Plan {
        public final Status status;
        public final Existing previous;
        public final List<Existing> alternatives;
        public final String explanation;
        private Plan(Status status,Existing previous,List<Existing> candidates,String explanation){
            this.status=status;this.previous=previous;
            this.alternatives=candidates;this.explanation=explanation;
        }
    }
    private static String fold(String value){
        if(value==null)return "";
        return Normalizer.normalize(value.toLowerCase(Locale.ROOT),Normalizer.Form.NFD)
            .replaceAll("\\p{M}+","").replaceAll("[^a-z0-9]+"," ")
            .replaceAll("\\s+"," ").trim();
    }
    /** Remove DATE and assessment weight, retain ordinal (parcial 1 vs parcial 2). */
    public static String identity(String text){
        // Strip percentages before accent/punctuation normalization drops the % sign.
        String name=fold(text==null?"":text.replaceAll(
            "(?iu)\\b\\d{1,3}(?:[.,]\\d{1,2})?\\s*%"," "));
        name=name.replaceAll("\\b(?:20\\d{2}|\\d{1,2}\\s+de\\s+\\w+\\s+de\\s+20\\d{2})\\b"," ");
        name=name.replaceAll("\\b\\d{1,2}\\s*\\d{1,2}\\s*20\\d{2}\\b"," ");
        name=name.replaceAll("\\b(?:semana|sem)\\s*(?:\\d{1,2}|[ivxlcdm]{1,6})\\b"," ");
        name=name.replaceAll("\\b(?:ponderacion|valor|peso)\\s*\\d{1,3}\\b"," ");
        name=name.replaceAll("\\s+"," ").trim();
        return name;
    }
    private static String cleanType(String type){return fold(type);}
    public static Plan compare(String title,String type,long due,String document,
                               List<Existing> enrolled){
        ArrayList<Existing> matches=new ArrayList<>();
        String sought=identity(title),wanted=cleanType(type);
        if(enrolled!=null)for(Existing earlier:enrolled){
            if(earlier==null||earlier.id<=0||!identity(earlier.title).equals(sought)||
               !cleanType(earlier.type).equals(wanted))continue;
            matches.add(earlier);
        }
        if(matches.isEmpty())return new Plan(Status.NEW,null,matches,
            "No existe una evaluación equivalente en este curso.");
        if(matches.size()>1){
            // Narrow by exact document provenance when one existing event matches.
            ArrayList<Existing> byDocument=new ArrayList<>();
            for(Existing e:matches)if(!document.isEmpty()&&
                    fold(e.document).equals(fold(document)))byDocument.add(e);
            if(byDocument.size()==1)matches=byDocument;
            else return new Plan(Status.AMBIGUOUS,null,matches,
                "Hay varias evaluaciones similares. Elige una antes de actualizar.");
        }
        Existing existing=matches.get(0);
        if(existing.due==due)return new Plan(Status.UNCHANGED,existing,matches,
            "Ya existe esta evaluación con la misma fecha.");
        return new Plan(Status.CHANGED,existing,matches,
            existing.due==0?"La evaluación estaba sin fecha y ahora tiene una fecha confirmada.":
            due==0?"El nuevo sílabo no confirma la fecha anterior.":
            "La fecha del sílabo es distinta de la fecha guardada.");
    }
}
