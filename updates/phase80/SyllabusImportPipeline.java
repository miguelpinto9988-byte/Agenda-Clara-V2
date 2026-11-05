package pe.agendaclara.app;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Joins text and table readers, retaining provenance for review. */
public final class SyllabusImportPipeline {
    private SyllabusImportPipeline(){}
    public static List<SyllabusEventParser.Event> extract(List<SyllabusEventParser.Page> pages){
        List<SyllabusEventParser.Event> ordinary=
            SyllabusReviewIntelligence.onlyEvents(SyllabusEventParser.extract(pages));
        List<SyllabusEventParser.Event> tables=
            SyllabusReviewIntelligence.onlyEvents(SyllabusTableInterpreter.extract(pages));
        ArrayList<SyllabusEventParser.Event> merged=new ArrayList<>();
        Set<String> keys=new HashSet<>();
        // Prefer table cells when they provide an explicit row-local date.
        for(SyllabusEventParser.Event event:tables)append(merged,keys,event);
        for(SyllabusEventParser.Event event:ordinary)append(merged,keys,event);
        return merged;
    }
    private static void append(List<SyllabusEventParser.Event> output,Set<String> keys,
                               SyllabusEventParser.Event e){
        if(e==null)return;
        String kind=SyllabusReviewIntelligence.classify(e.title+" "+e.type);
        int week=SyllabusReviewIntelligence.week(e.sourceText);
        String key=e.page+"|"+kind+"|"+week+"|"+
                SyllabusReviewIntelligence.fold(e.title).replaceAll("[^a-z0-9]","")+
                "|"+(e.date==null?"":e.date);
        if(keys.add(key))output.add(e);
    }
}
