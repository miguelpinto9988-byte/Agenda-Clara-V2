import pe.agendaclara.app.*;
import java.time.*;
import java.util.*;

/** Synthetic academic phrases, deliberately reordered; nothing is imported or stored. */
public final class AcademicContextInterpreterTests {
    static int checks=0;
    static void ok(boolean value,String description){checks++;if(!value)throw new AssertionError(description);}
    static final LocalDate TODAY=LocalDate.of(2026,11,2);
    static void checkVoice(String phrase,String title,LocalDate date,LocalTime time,String course){
        QuickTaskVoiceParser.Result p=QuickTaskVoiceParser.parse(phrase,TODAY);
        ok(title.equals(p.title),"wrong title: '"+p.title+"' in "+phrase);
        ok(Objects.equals(date,p.date),"wrong date: "+p.date+" in "+phrase);
        ok(Objects.equals(time,p.time),"wrong time: "+p.time+" in "+phrase);
        ok(course.equals(p.course),"wrong course: "+p.course+" in "+phrase);
    }
    public static void main(String[]args){
        LocalTime end=LocalTime.of(23,59);
        checkVoice("Tengo tarea de Historia dentro de tres días a las dos de la tarde",
            "tarea de Historia",TODAY.plusDays(3),LocalTime.of(14,0),"Historia");
        checkVoice("Dentro de tres días, a las dos de la tarde, tengo tarea de Historia",
            "tarea de Historia",TODAY.plusDays(3),LocalTime.of(14,0),"Historia");
        checkVoice("A las dos de la tarde tengo tarea de Historia dentro de tres días",
            "tarea de Historia",TODAY.plusDays(3),LocalTime.of(14,0),"Historia");
        checkVoice("Historia: tarea dentro de tres días a las dos de la tarde",
            "Historia: tarea",TODAY.plusDays(3),LocalTime.of(14,0),"Historia");
        checkVoice("Para el martes de la próxima semana preparar presentación de Social Studies",
            "preparar presentación de Social Studies",LocalDate.of(2026,11,10),end,"Social Studies");
        checkVoice("Mañana a las 4 p. m. entregar Historia", "entregar Historia",TODAY.plusDays(1),LocalTime.of(16,0),"Historia");
        checkVoice("Tengo trabajo de Historia próximo viernes 2 pm","trabajo de Historia",LocalDate.of(2026,11,6),LocalTime.of(14,0),"Historia");
        checkVoice("En tres días a las 5 de la tarde tengo exposición de Social Studies en 4to de secundaria",
            "exposición de Social Studies en 4to de secundaria",TODAY.plusDays(3),LocalTime.of(17,0),"Social Studies");
        QuickTaskVoiceParser.Result r=QuickTaskVoiceParser.parse("en la próxima semana tengo tarea de historia a las dos de la tarde",TODAY);
        ok(r.hadDate&&!r.validDate&&r.date==null,"broad week should not invent a day");
        ok(r.validTime&&r.time.equals(LocalTime.of(14,0)),"afternoon hour should resolve");
        r=QuickTaskVoiceParser.parse("a las dos de la próxima semana tengo la tarea de historia",TODAY);
        ok(r.hadDate&&!r.validDate&&r.date==null,"ambiguous next week should request day");
        ok(r.hadTime&&!r.validTime&&r.time==null,"two o'clock must ask AM/PM");
        ok(!r.contextHint.isEmpty(),"question shown in review");
        r=QuickTaskVoiceParser.parse("Examen de social studies el próximo jueves",TODAY);
        ok(LocalTime.of(23,59).equals(r.time),"Voice tasks default to 23:59");
        r=QuickTaskVoiceParser.parse("título pagar la luz fecha 10 de octubre hora 4 de la tarde recordatorio cada tres horas",TODAY);
        ok(r.date.equals(LocalDate.of(2027,10,10))&&r.time.equals(LocalTime.of(16,0))&&r.repeatMinutes==180,"legacy command compatibility");
        r=QuickTaskVoiceParser.parse("Necesito entregar el informe de Historia dentro de tres días y recuérdame cada dos horas",TODAY);
        ok(r.repeatMinutes==120&&r.title.equals("entregar el informe de Historia"),"reminder cannot leak into title");
        AcademicContextInterpreter.Result c=AcademicContextInterpreter.parse("El miércoles examen de Social Studies para 4to de secundaria y vale 5 puntos",TODAY);
        ok(c.kind.equals("EVALUACION")&&c.grade.contains("4to de secundaria"),"grade and evaluation");
        ok(c.notes.contains("puntuación"),"grades must not become time");
        c=AcademicContextInterpreter.parse("Apunte de Historia: mapa del capítulo tres",TODAY);
        ok(c.course.equals("Historia")&&c.kind.equals("NOTA")&& !c.action,"note must not become task");
        c=AcademicContextInterpreter.parse("Tarea de Diseño Universal para el viernes",TODAY,Arrays.asList("Diseño Universal"));
        ok(c.course.equals("Diseño Universal"),"registered course lexicon");
        c=AcademicContextInterpreter.parse("Examen de matemáticas para 4.º B",TODAY);
        ok(c.grade.contains("4.º B"),"grade section recognized");
        c=AcademicContextInterpreter.parse("Entrega de química 31 de febrero",TODAY);
        ok(c.hadDate&&c.dateUncertain&&c.date==null,"invalid date must remain unconfirmed");
        c=AcademicContextInterpreter.parse("Tarea de literatura a las 12",TODAY);
        ok(c.hadTime&&c.timeUncertain,"12 without AM/PM is ambiguous");
        c=AcademicContextInterpreter.parse("Tarea de literatura a las 14:30",TODAY);
        ok(c.time.equals(LocalTime.of(14,30))&&!c.timeUncertain,"24-hour clock");
        ZoneId zone=ZoneId.of("America/Lima");long now=TODAY.atTime(8,0).atZone(zone).toInstant().toEpochMilli();
        MessageParser.Proposal p=MessageParser.parseOne("Dentro de tres días a las 2 de la tarde tengo tarea de Historia",now,zone,false);
        ok(p.action&&p.dateKnown&&p.timeKnown&&p.due==TODAY.plusDays(3).atTime(14,0).atZone(zone).toInstant().toEpochMilli(),"WhatsApp date-first academic assignment");
        ok(p.course.equals("Historia"),"WhatsApp course metadata");
        p=MessageParser.parseOne("A las dos la próxima semana tengo tarea de Social Studies",now,zone,false);
        ok(p.action&&!p.dateKnown&&!p.timeKnown&&p.ambiguous,"ambiguous WhatsApp date and time must not schedule");
        ok(p.course.equals("Social Studies"),"English course in Spanish message");
        ok(MessageParser.parse("Gracias por enviar el informe mañana",now,zone,false).isEmpty(),"no spurious task on gratitude");
        ok(MessageParser.parse("¿Tendremos examen de historia el viernes?",now,zone,false).isEmpty(),"no task on question");
        ok(MessageParser.parse("No hay tarea de Historia mañana",now,zone,false).isEmpty(),"no task on cancellation");
        List<MultiActivityInterpreter.Candidate> many=MultiActivityInterpreter.extract(
            "Mañana a las 2 pm tenemos tarea de Matemática; además el viernes tenemos examen de Historia",TODAY);
        ok(many.size()==2,"two separate activities");
        ok(many.get(0).course.equals("Matemática")&&many.get(1).course.equals("Historia"),"courses scoped to each activity");
        System.out.println("PASS: "+checks+" academic-context and flexible-order checks");
    }
}
