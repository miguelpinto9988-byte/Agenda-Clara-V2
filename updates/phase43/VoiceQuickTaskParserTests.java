import pe.agendaclara.app.*;
import java.time.*;
public class VoiceQuickTaskParserTests {
    static void expect(boolean ok){if(!ok)throw new AssertionError("Voice command parser failed");}
    public static void main(String[] args){
        LocalDate today=LocalDate.of(2026,11,1);
        QuickTaskVoiceParser.Result r=QuickTaskVoiceParser.parse("título pagar la luz fecha 10 de octubre hora 4 de la tarde recordatorio cada tres horas",today);
        expect(r.title.equals("pagar la luz"));
        expect(r.date.equals(LocalDate.of(2027,10,10)));
        expect(r.time.equals(LocalTime.of(16,0)));
        expect(r.repeatMinutes==180);
        r=QuickTaskVoiceParser.parse("título reunión fecha mañana hora 9 a. m. recordatorio 2 horas antes",today);
        expect(r.date.equals(LocalDate.of(2026,11,2)) && r.time.equals(LocalTime.of(9,0)) && r.beforeMinutes==120);
        r=QuickTaskVoiceParser.parse("título reunión fecha 31 de febrero hora 25:70 recordatorio cada 0 horas",today);
        expect(!r.validDate && !r.validTime && !r.validReminder);
        expect(GeneralCategoryScope.visibleIn("General","Proyectos"));
        expect(GeneralCategoryScope.visibleIn("General","Notas"));
        expect(GeneralCategoryScope.visibleIn("General","General"));
        expect(GeneralCategoryScope.visibleIn("Notas","Notas"));
        expect(!GeneralCategoryScope.visibleIn("Proyectos","Notas"));
        expect(GeneralCategoryScope.isGeneral(" general "));
        System.out.println("PASS: voice title/date/time/reminder parser and category scope");
    }
}
