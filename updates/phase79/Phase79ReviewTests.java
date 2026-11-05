package pe.agendaclara.app;
import java.util.*;

public final class Phase79ReviewTests {
    static void ok(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    static SyllabusEventParser.Event e(String title,String type,String source){
        return new SyllabusEventParser.Event(title,type,null,8,source);
    }
    public static void main(String[] args){
        ok(SyllabusReviewIntelligence.week("Semana XII") == 12,"roman week");
        ok(SyllabusReviewIntelligence.week("Semanas 13-14") == 13,"week range");
        ok(SyllabusReviewIntelligence.week("Sem. 8") == 8,"abbreviated week");
        ok(SyllabusReviewIntelligence.week("Semana 60") == 0,"invalid week");
        ok(SyllabusReviewIntelligence.weight("Examen final (30 %)")==30,"weight");
        ok(SyllabusReviewIntelligence.weight("Producto final 125 %")==-1,"invalid weight");
        for(String label:Arrays.asList("Examen oral","Examen práctico","Examen sustitutorio",
                "Examen de recuperación","Segundo parcial","Evaluación final",
                "Práctica calificada","Control de lectura")){
            ok("Examen".equals(SyllabusReviewIntelligence.classify(label)),label);
        }
        for(String label:Arrays.asList("Trabajo final","Producto final","Proyecto integrador",
                "Portafolio final","Sustentación final","Entrega del proyecto final")){
            ok("Producto final".equals(SyllabusReviewIntelligence.classify(label)),label);
        }
        for(String label:Arrays.asList("Tarea semanal","Foro de discusión",
                "Informe de lectura","Bibliografía del curso",
                "Sistema de evaluación","Metodología de enseñanza")){
            ok(SyllabusReviewIntelligence.classify(label).isEmpty(),label);
        }
        List<SyllabusEventParser.Event> input=Arrays.asList(
            e("Examen final semana 15","examen","Semana XV | Examen final 30%"),
            e("Trabajo final semana 16","trabajo","Semana 16 | Trabajo final"),
            e("Foro semanal","actividad","Foro semanal"),
            e("Examen final semana 15","examen","Semana XV | Examen final 30%"));
        List<SyllabusReviewIntelligence.Review> result=SyllabusReviewIntelligence.filter(input);
        ok(result.size()==2,"only exam and final product, deduplicated");
        ok(result.get(0).week==15&&result.get(0).weight==30,"week/weight preserved");
        ok(!result.get(0).dateConfirmed&&result.get(0).event.date==null,
                "never invent date for academic week");
        ok(result.get(0).dateEvidence.contains("sin confirmar"),
                "pending exact day explained");
        System.out.println("PASS: exam types, final deliverables, exclusions, week and weights");
        System.out.println("PASS: duplicates suppressed, no fabricated dates");
    }
}
