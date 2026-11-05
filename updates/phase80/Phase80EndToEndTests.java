package pe.agendaclara.app;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

public final class Phase80EndToEndTests {
    private static void check(boolean ok,String message){
        if(!ok)throw new AssertionError(message);
    }
    private static List<SyllabusEventParser.Event> parse(String text){
        List<SyllabusEventParser.Page> pages=SyllabusTableNormalizer.normalize(
            Arrays.asList(new SyllabusEventParser.Page(3,text)));
        return SyllabusReviewIntelligence.onlyEvents(SyllabusEventParser.extract(pages));
    }
    public static void main(String[] args){
        List<SyllabusEventParser.Event> split=parse(
            "Asignatura: Historia de la educación\n"+
            "Semana | Evaluación | Fecha\n"+
            "XII\nExamen parcial\n12/11/2026\n"+
            "XV\nTrabajo final\n29/11/2026\n"+
            "Bibliografía y tareas ordinarias\n");
        check(split.size()==2,"vertical table reconstructs exactly 2 evaluations");
        check(split.get(0).page==3&&split.get(1).page==3,"original page preserved");
        check(LocalDate.of(2026,11,12).equals(split.get(0).date),
                "week XII exam linked to its own date");
        check(split.get(0).week==12,"week XII preserved");
        check(LocalDate.of(2026,11,29).equals(split.get(1).date),
                "final project linked to its own date");
        List<SyllabusEventParser.Event> inline=parse(
            "Semana | Evaluación | Fecha\n"+
            "3 | Control de lectura | 19/11/2026\n"+
            "4 | Examen práctico | 26/11/2026\n");
        check(inline.size()==2,"inline table does not duplicate events");
        check(inline.get(1).date.equals(LocalDate.of(2026,11,26)),
                "second inline evaluation has its own date");
        List<SyllabusEventParser.Event> pending=parse(
            "Curso: Investigación educativa\n"+
            "Semana | Evaluación\n"+
            "XV\nExamen final\n"+
            "XVI\nProducto final\n");
        check(pending.size()==2,"week-only events imported");
        check(pending.get(0).date==null&&pending.get(1).date==null,
                "week-only events must not invent a day");
        check(pending.get(0).week==15&&pending.get(1).week==16,
                "week-only numbers belong to correct event");
        List<SyllabusEventParser.Event> unusual=parse(
            "Quiz 2 | Semana 7"+System.lineSeparator()+
            "Prueba oral de unidad | Semana VIII"+System.lineSeparator());
        check(unusual.size()==2,"quiz and oral exam remain recognized by filter");
        String before=SyllabusImportPolicy.signature("Historia de la educación","Examen",
            "Examen final | Semana XV | 25/11/2026 | 30%",1);
        String after=SyllabusImportPolicy.signature("Historia de la educación","Examen",
            "Examen final | Semana XV | 28/11/2026 | 30%",1);
        String other=SyllabusImportPolicy.signature("Historia de la educación","Examen",
            "Examen final | Semana XV | 28/11/2026 | 30%",2);
        check(before.equals(after),"date modifications retain event identity");
        check(!before.equals(other),"repeated labels have distinct occurrences");
        check(!SyllabusImportPolicy.sameContent("Examen final",1,
            "Examen final",2),"date changes detected");
        check(SyllabusImportPolicy.sameContent("Examen final",1,
            "Examen final",1),"unchanged event identified");
        System.out.println("PASS: multiline and inline timetable rows, independent dates");
        System.out.println("PASS: weeks without date remain pending, page provenance");
        System.out.println("PASS: date-independent identities and version change detection");
    }
}
