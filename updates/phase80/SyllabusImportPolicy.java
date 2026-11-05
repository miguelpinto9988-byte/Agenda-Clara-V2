package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.Locale;

/** Stable event signatures for syllabus reimports. Excludes mutable dates and weights. */
public final class SyllabusImportPolicy {
    private SyllabusImportPolicy() {}
    public static String normalized(String source) {
        if(source==null)return "";
        String s=Normalizer.normalize(source.toLowerCase(Locale.ROOT),Normalizer.Form.NFD)
                .replaceAll("\\p{M}+","");
        s=s.replaceAll("\\b(?:del?|desde|hasta)\\s+\\d{1,2}\\s+de\\s+"+
                "(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|"+
                "setiembre|septiembre|octubre|noviembre|diciembre)(?:\\s+de\\s+\\d{4})?"," ");
        s=s.replaceAll("\\b\\d{4}-\\d{1,2}-\\d{1,2}\\b"," ");
        s=s.replaceAll("\\b\\d{1,2}[./-]\\d{1,2}[./-]\\d{2,4}\\b"," ");
        s=s.replaceAll("\\b(?:semana|semanas|sem)\\.?\\s*(?:nro|n|no)?\\.?\\s*"+
                "(?:[0-9]{1,2}|[ivxlcdm]{1,8})(?:\\s*(?:-|al|a|y)\\s*"+
                "(?:[0-9]{1,2}|[ivxlcdm]{1,8}))?\\b"," ");
        s=s.replaceAll("\\b\\d{1,3}(?:[.,]\\d{1,2})?\\s*%"," ");
        s=s.replaceAll("[|:;,–—()\\[\\]{}]+"," ");
        s=s.replaceAll("\\s+"," ").trim();
        return s;
    }
    /** Multiplicity is deterministic per same-label occurrence in a single PDF. */
    public static String signature(String course,String kind,String eventLabel,int occurrence) {
        if(occurrence<1)throw new IllegalArgumentException("Occurrence must be positive");
        return normalized(course)+"|"+normalized(kind)+"|"+normalized(eventLabel)+
                "|#"+occurrence;
    }
    public static boolean sameContent(String oldTitle,long oldDue,String newTitle,long newDue) {
        return normalized(oldTitle).equals(normalized(newTitle))&&oldDue==newDue;
    }
}
