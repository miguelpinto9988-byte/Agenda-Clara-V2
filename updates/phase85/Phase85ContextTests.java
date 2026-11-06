package pe.agendaclara.app;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

/** Realistic regression fixtures for contextual syllabus inference, not just keyword hits. */
public final class Phase85ContextTests {
    private static void check(boolean condition, String why) {
        if (!condition) throw new AssertionError(why);
    }
    private static SyllabusEventParser.Page p(int number,String text){
        return new SyllabusEventParser.Page(number,text);
    }
    private static List<SyllabusEventParser.Event> from(SyllabusEventParser.Page... pages) {
        return SyllabusImportPipeline.extract(Arrays.asList(pages));
    }
    private static void date(SyllabusEventParser.Event event, String expected) {
        check(event.date != null && event.date.equals(LocalDate.parse(expected)),
            "Expected date " + expected + " for " + event.title + ", got " + event.date);
    }
    private static void contains(String value,String what) {
        check(value.toLowerCase().contains(what.toLowerCase()),
            "Expected text " + what + " in " + value);
    }
    public static void main(String[] args) {
        List<SyllabusEventParser.Event> merged = from(
            p(1,"Temario de examen: tema 14\nPrimer examen parcial\n" +
                "Primer examen es el tema 5\nLos exámenes se evaluarán con rúbricas"),
            p(3,"Segundo examen parcial | 18/06/2026\n" +
                "Primer examen parcial | Fecha: 11/05/2026\n" +
                "Examen tema 12 | 01/06/2026"),
            p(4,"Tercer examen parcial\nSegundo examen: tema 14"));
        check(merged.size() == 3, "Expected exactly three correlated partials; got "+merged.size());
        contains(merged.get(0).title,"Primer examen parcial");
        contains(merged.get(0).title,"Tema 5");
        date(merged.get(0),"2026-05-11");
        date(merged.get(1),"2026-06-18");
        contains(merged.get(1).title,"Tema 14");
        check(merged.get(2).needsDate(),"Undated third partial must remain pending");
        check(merged.get(0).sourceText.contains("Pág. 1") &&
              merged.get(0).sourceText.contains("Pág. 3"),
              "Must preserve provenance of correlated evidence");
        check(from(p(1,"Primer examen es el tema 5\nExamen tema 14")).isEmpty(),
              "A topical reference without a numbered partial must not become an event");
        List<SyllabusEventParser.Event> ambiguous = from(p(1,
            "Primer examen parcial | 10/05/2026\n" +
            "Primer examen parcial | 12/05/2026"));
        check(ambiguous.size()==1,"Repeated partial must collapse");
        check(ambiguous.get(0).date==null,"Conflicting dates must not be guessed");
        contains(ambiguous.get(0).title,"Verificar fecha");
        List<SyllabusEventParser.Event> twoDatesOneRow=from(p(1,
            "Segundo examen parcial | del 10/06/2026 al 12/06/2026"));
        check(twoDatesOneRow.size()==1 && twoDatesOneRow.get(0).date==null,
            "Two possible dates in one row cannot be treated as an exact day");
        List<SyllabusEventParser.Event> adjacent=from(p(2,
            "Primer examen parcial\nFecha: 06/06/2026\n" +
            "Segundo examen parcial\n07/07/2026"));
        check(adjacent.size()==2,"Adjacent date-only rows should not create extra exams");
        date(adjacent.get(0),"2026-06-06");
        date(adjacent.get(1),"2026-07-07");
        List<SyllabusEventParser.Event> weekOnly=from(p(2,
            "Inicio de clases: 01/03/2026\nSemana 5\nPrimer examen parcial"));
        check(weekOnly.size()==1 && weekOnly.get(0).date==null,
            "Week proximity must not manufacture an exact exam date");
        List<SyllabusEventParser.Event> otherKinds=from(p(7,
            "Semana | Actividad | Fecha | Peso\n" +
            "12 | Examen oral | 18/11/2026 | 30%\n" +
            "14 | Producto final | Por confirmar | 40%\n" +
            "Examen tema 14\nExamen parcial sin número\n" +
            "Examen final 20/11/2026"));
        check(otherKinds.size()==3,"Keep explicit oral/final exam and product, not topical noise");
        check(otherKinds.stream().noneMatch(e -> e.title.contains("tema 14")),
            "Topic-only lines must be filtered");
        List<SyllabusEventParser.Event> unknownYear=from(p(8,
            "Primer examen parcial: 14 de mayo\nSegundo parcial"));
        check(unknownYear.size()==2 && unknownYear.get(0).date==null &&
              unknownYear.get(1).date==null,
              "Year must not be invented without a reliable calendar anchor");
        List<SyllabusEventParser.Event> otherOrders=from(p(2,
            "3er examen parcial - 01/08/2026\n1er examen parcial - 30/09/2026\n" +
            "2do examen parcial - 05/09/2026"));
        check(otherOrders.size()==3,"Digit ordinals must be recognized");
        contains(otherOrders.get(0).title,"Primer");
        contains(otherOrders.get(1).title,"Segundo");
        contains(otherOrders.get(2).title,"Tercer");
        date(otherOrders.get(0),"2026-09-30");
        date(otherOrders.get(1),"2026-09-05");
        System.out.println("PASS: contextual partials linked across pages and grouped by ordinal");
        System.out.println("PASS: topic-only mentions excluded; distinct final/oral exams preserved");
        System.out.println("PASS: same-row and adjacent dates, conflict review, no invented year/week");
        System.out.println("PASS: first, second and third partials ordered logically, not by date guess");
    }
}
