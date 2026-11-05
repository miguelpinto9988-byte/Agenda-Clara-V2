package pe.agendaclara.app;
import java.util.*;
public final class Phase80Tests {
    private static void ok(boolean b,String message){if(!b)throw new AssertionError(message);}
    public static void main(String[] args){
        String table="Semana | Actividad | Fecha | Peso\n"+
            "12 | Examen oral | 18/11/2026 | 30%\n"+
            "13 | Foro de lectura | 19/11/2026 | 5%\n"+
            "14 | Producto final | Por confirmar | 40%\n";
        List<SyllabusEventParser.Page> pages=Arrays.asList(
            new SyllabusEventParser.Page(7,table));
        List<SyllabusEventParser.Event> rows=SyllabusTableInterpreter.extract(pages);
        ok(rows.size()==2,"only exam and final product");
        ok(rows.get(0).date!=null&&rows.get(0).date.toString().equals("2026-11-18"),
                "row-local date");
        ok(rows.get(1).date==null,"week-only no invented date");
        ok(rows.get(0).page==7,"provenance page");
        ok(SyllabusReviewIntelligence.week(rows.get(0).sourceText)==12,"table week preserved");
        List<SyllabusEventParser.Event> all=SyllabusImportPipeline.extract(pages);
        ok(all.size()==2,"no duplicate events between table and text readers");
        Map<String,String> previous=new HashMap<>();
        previous.put("examen final","2026-11-20");
        previous.put("producto final","2026-11-25");
        Map<String,String> current=new HashMap<>();
        current.put("examen final","2026-11-27");
        current.put("sustentacion final","2026-11-30");
        List<SyllabusRevisionComparator.Change> changes=
            SyllabusRevisionComparator.compare(previous,current);
        ok(changes.size()==3,"changed, new and removed items detected");
        ok(SyllabusRevisionComparator.parse(
                SyllabusRevisionComparator.serialize(current)).equals(current),
                "revision roundtrip");
        System.out.println("PASS: tables, dates, source page, exclusions, version diff");
    }
}
