import pe.agendaclara.app.QuickTaskVoiceParser;
import java.time.*;

/** Synthetic examples only: no microphone recordings or personal data. */
public final class NaturalQuickTaskTests {
    private static int checks=0;
    private static void check(boolean result,String description){checks++;if(!result)throw new AssertionError(description);}
    private static void sentence(String spoken,LocalDate today,String title,LocalDate dueDate,LocalTime dueTime,int every,int before){
        QuickTaskVoiceParser.Result r=QuickTaskVoiceParser.parse(spoken,today);
        check(r.validDate&&r.validTime&&r.validReminder,"Unexpected invalid interpretation: "+spoken);
        check(title.equals(r.title),"Wrong title: "+r.title);
        check(dueDate.equals(r.date),"Wrong date for "+spoken+": "+r.date);
        check(dueTime.equals(r.time),"Wrong time for "+spoken+": "+r.time);
        check(every==r.repeatMinutes&&before==r.beforeMinutes,"Wrong reminder: "+spoken);
    }
    public static void main(String[] args){
        LocalDate today=LocalDate.of(2026,11,1);
        LocalTime end=LocalTime.of(23,59);
        sentence("Tengo que entregar el informe de Historia dentro de tres días y recuérdame cada dos horas",today,"entregar el informe de Historia",today.plusDays(3),end,120,-1);
        sentence("Pagar la luz mañana a las cuatro de la tarde",today,"Pagar la luz",today.plusDays(1),LocalTime.of(16,0),0,-1);
        sentence("Necesito presentar el trabajo en una semana",today,"presentar el trabajo",today.plusWeeks(1),end,0,-1);
        sentence("Comprar el regalo el próximo mes",today,"Comprar el regalo",today.plusMonths(1),end,0,-1);
        sentence("Reunión de equipo el 15 de noviembre a las 9:30 de la mañana",today,"Reunión de equipo",LocalDate.of(2026,11,15),LocalTime.of(9,30),0,-1);
        sentence("Entregar reporte el 5 de noviembre recuérdame dos horas antes",today,"Entregar reporte",LocalDate.of(2026,11,5),end,0,120);
        sentence("Hacer el inventario",today,"Hacer el inventario",today,end,0,-1);
        sentence("Terminar el ejercicio dentro de 3 días a las 4 p. m.",today,"Terminar el ejercicio",today.plusDays(3),LocalTime.of(16,0),0,-1);
        sentence("Enviar el contrato dentro de una semana a las cinco y media de la tarde",today,"Enviar el contrato",today.plusWeeks(1),LocalTime.of(17,30),0,-1);
        sentence("Comprar leche pasado mañana",today,"Comprar leche",today.plusDays(2),end,0,-1);
        sentence("Estudiar para el examen el próximo lunes",today,"Estudiar para el examen",LocalDate.of(2026,11,2),end,0,-1);
        sentence("Hacer el informe sin recordatorio",today,"Hacer el informe",today,end,0,0);
        sentence("Completar la tarea en dos semanas",today,"Completar la tarea",today.plusWeeks(2),end,0,-1);
        sentence("Entregar presupuesto 02/12/2026 a las 12 del mediodía",today,"Entregar presupuesto",LocalDate.of(2026,12,2),LocalTime.NOON,0,-1);
        sentence("título pagar la luz fecha 10 de octubre hora 4 de la tarde recordatorio cada tres horas",today,"pagar la luz",LocalDate.of(2027,10,10),LocalTime.of(16,0),180,-1);
        sentence("título reunión fecha mañana hora 9 a. m. recordatorio 2 horas antes",today,"reunión",today.plusDays(1),LocalTime.of(9,0),0,120);
        check(QuickTaskVoiceParser.parse("Preparar informe el próximo mes",LocalDate.of(2026,1,31)).date.equals(LocalDate.of(2026,2,28)),"Month end rollover");
        check(QuickTaskVoiceParser.parse("Entregar informe dentro de una semana",LocalDate.of(2026,10,1)).date.equals(LocalDate.of(2026,10,8)),"One-week offset from recording day");
        QuickTaskVoiceParser.Result invalid=QuickTaskVoiceParser.parse("entregar el documento el 31 de febrero",today);
        check(invalid.hadDate&&!invalid.validDate&&invalid.date==null,"Invalid date must not silently default");
        invalid=QuickTaskVoiceParser.parse("título reunión fecha 31 de febrero hora 25:70 recordatorio cada 0 horas",today);
        check(!invalid.validDate&&!invalid.validTime&&!invalid.validReminder,"Backward compatibility for invalid legacy commands");
        check(QuickTaskVoiceParser.DEFAULT_DEADLINE.equals(LocalTime.of(23,59)),"Default deadline must be 11:59 PM");
        System.out.println("PASS natural Spanish voice task interpretation: "+checks+" checks");
    }
}
