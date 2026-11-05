package pe.agendaclara.app;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

/** JVM-only factual regression cases. No Android SDK, Gradle or APK required. */
public final class Phase79SyllabusTests {
    private static void ok(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    private static SyllabusAssessmentExtractor.Finding find(
            List<SyllabusAssessmentExtractor.Finding> list,String title){
        for(SyllabusAssessmentExtractor.Finding f:list)
            if(f.event.title.toLowerCase(java.util.Locale.ROOT)
                    .contains(title.toLowerCase(java.util.Locale.ROOT)))return f;
        throw new AssertionError("No se encontró "+title);
    }
    public static void main(String[] args) {
        List<SyllabusEventParser.Page> pages=Arrays.asList(
            new SyllabusEventParser.Page(1,
                "PERIODO ACADEMICO: 2026-II\nInicio de clases: 17/08/2026\n"+
                "ASIGNATURA: Tendencias educativas\nCalendario de evaluaciones"),
            new SyllabusEventParser.Page(3,
                "SEMANA XII\nParcial 2\n25 %\n"+
                "Semana 13\nExamen final\n"+
                "del 28 de noviembre al 3 de diciembre de 2026\n30 %\n"+
                "Examen sustitutorio | martes semana 12 | 15%\n"+
                "Producto final | 18/12/2026 | 30 %\n"+
                "Actividad regular | 12/12/2026\n"+
                "Rúbrica de evaluación | 15%\n")
        );
        List<SyllabusAssessmentExtractor.Finding> events=
            SyllabusAssessmentExtractor.extract(pages);
        ok(events.size()==4,"Solo 4 exámenes/finales, encontrados "+events.size());
        SyllabusAssessmentExtractor.Finding partial=find(events,"Parcial 2");
        ok(partial.event.week==12,"Parcial II hereda semana XII de tabla");
        ok(partial.event.date==null,"Semana sola NO debe inventar día");
        ok(partial.weight==25,"Parcial II extrae ponderación de otra celda");
        SyllabusAssessmentExtractor.Finding finalExam=find(events,"Examen final");
        ok(finalExam.event.date==null,"Rango no es una fecha exacta");
        ok(finalExam.event.windowStart.equals(LocalDate.of(2026,11,28)),
                "Inicio de rango entre meses");
        ok(finalExam.event.windowEnd.equals(LocalDate.of(2026,12,3)),
                "Fin de rango entre meses");
        ok(finalExam.weight==30,"Ponderación del examen final");
        SyllabusAssessmentExtractor.Finding substitute=find(events,"Examen sustitutorio");
        ok(substitute.suggestedDay!=null,"Martes de semana 12 sugiere día");
        ok(substitute.event.date==null,"Fecha calculada requiere confirmación");
        SyllabusAssessmentExtractor.Finding project=find(events,"Producto final");
        ok(project.event.date.equals(LocalDate.of(2026,12,18)),
                "Fecha completa explícita");
        ok(project.weight==30,"Producto final extrae 30%");
        ok(SyllabusEventParser.extract(pages).size()==4,
                "La API heredada debe usar el analizador mejorado");
        ok(SyllabusDateInterpreter.calendar(pages).anchored(),
                "Inicio semestral encontrado");
        List<SyllabusReimportPlanner.Existing> known=Arrays.asList(
            new SyllabusReimportPlanner.Existing(10,"Examen final 30%",
                "Examen",0,"Silabo de Tendencias 2026.pdf"));
        ok(SyllabusReimportPlanner.identity("Examen final 25%").equals(
            SyllabusReimportPlanner.identity("Examen final 30%")),
            "Cambio de porcentaje no debe crear duplicado");
        SyllabusReimportPlanner.Plan changed=SyllabusReimportPlanner.compare(
            "Examen final 25%","Examen",1764000000000L,"Silabo de Tendencias 2026.pdf",known);
        ok(changed.status==SyllabusReimportPlanner.Status.CHANGED&&
                changed.previous.id==10,"Debe proponer ACTUALIZAR evento sin fecha");
        SyllabusReimportPlanner.Plan unchanged=SyllabusReimportPlanner.compare(
            "Examen final 30%","Examen",0,"Silabo de Tendencias 2026.pdf",known);
        ok(unchanged.status==SyllabusReimportPlanner.Status.UNCHANGED,
            "Debe omitir reimportación idéntica");
        List<SyllabusReimportPlanner.Existing> duplicates=Arrays.asList(
            new SyllabusReimportPlanner.Existing(11,"Parcial 1","Examen",0,"doc-a.pdf"),
            new SyllabusReimportPlanner.Existing(12,"Parcial 1","Examen",0,"doc-b.pdf"));
        ok(SyllabusReimportPlanner.compare("Parcial 1","Examen",0,"doc-c.pdf",duplicates)
                .status==SyllabusReimportPlanner.Status.AMBIGUOUS,
            "Dos registros idénticos no se deben modificar solos");
        ok(SyllabusReimportPlanner.compare("Parcial 2","Examen",0,"doc-a.pdf",duplicates)
                .status==SyllabusReimportPlanner.Status.NEW,
            "Parcial 1 y 2 no deben colisionar");
        System.out.println("PASS 79: tablas PDF y DOCX, rangos, semanas, porcentajes, día sugerido");
        System.out.println("PASS 79: solo exámenes y finales, sin asignar fechas inventadas");
        System.out.println("PASS 79: nueva/idéntica/actualización/ambigua, reimportación segura");
    }
}
