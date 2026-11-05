package pe.agendaclara.app;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

/** Pure JVM regression tests. Does not require Android SDK, Gradle or APK build. */
public final class PhaseBParserTests {
    private static void check(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    public static void main(String[] ignored){
        List<AcademicCourseMatcher.Course> courses=Arrays.asList(
            new AcademicCourseMatcher.Course("horario-a","Educación 2026","Tendencias educativas"),
            new AcademicCourseMatcher.Course("horario-a","Educación 2026","Didáctica"),
            new AcademicCourseMatcher.Course("horario-b","Nocturno","Tendencias educativas")
        );
        List<AcademicCourseMatcher.Match> match=AcademicCourseMatcher.matches(
            "Presentación de infografía de tendencias la próxima semana",courses);
        check(match.size()==2,"Debe ofrecer ambos perfiles con Tendencias");
        check(match.get(0).course.name.equals("Tendencias educativas"),"Curso parcial");
        check(AcademicCourseMatcher.matches("Trabajo del curso",courses).isEmpty(),
                "Palabras genéricas no deben asignar un curso");
        check(AcademicCourseMatcher.matches("Historia",courses).isEmpty(),
                "Materia inexistente");

        check(LocalDate.of(2026,11,25).equals(
                SyllabusEventParser.explicitDate("Parcial 1: 25/11/2026")),"Fecha numérica");
        check(LocalDate.of(2026,12,14).equals(
                SyllabusEventParser.explicitDate("Examen final, 14 de diciembre de 2026")),
                "Mes español");
        check(SyllabusEventParser.explicitDate("Semana 8")==null,"No inventar fecha por semana");
        check(SyllabusEventParser.explicitDate("35/11/2026")==null,"No aceptar día inválido");
        List<SyllabusEventParser.Event> events=SyllabusEventParser.extract(Arrays.asList(
            new SyllabusEventParser.Page(3,
                    "I Parcial - 25/11/2026\nExamen final: 14 de diciembre de 2026"),
            new SyllabusEventParser.Page(5,"Segundo parcial — Semana 8")
        ));
        check(events.size()==3,"Debe encontrar tres eventos");
        check(events.get(0).page==3,"Debe preservar la página de origen");
        check(events.get(2).needsDate(),"Semana 8 requiere confirmación manual");
        System.out.println("PASS B: coincidencias parciales, perfiles ambiguos y fechas verificables");
        System.out.println("PASS B: eventos con página fuente y semanas sin fecha no inventadas");
    }
}
