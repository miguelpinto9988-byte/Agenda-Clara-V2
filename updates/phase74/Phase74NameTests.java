package pe.agendaclara.app;

/** Pure JVM regressions for OCR timetable names, no Android SDK required. */
public final class Phase74NameTests {
    private static void expect(String source,String expected) {
        String got=ScheduleTitleParser.suggest(source);
        if(!expected.equals(got))
            throw new AssertionError("OCR suggestion: '"+source+"' => '"+got+"' expected '"+expected+"'");
    }
    public static void main(String[] args) {
        expect("HORARIO: Educación 2026\nLunes\nMatemática","Educación 2026");
        expect("Horario de clases — Semana 4\nMartes 08:00","Semana 4");
        expect("Semana: 7\nJueves 10:00","7");
        expect("Semana 12\nLunes 09:00\nDidáctica","Semana 12");
        expect("Lunes\nMartes\nTendencias educativas\n08:00",""); // no header: manual prompt
        expect("Horario de clases\nMiércoles\n16:30",""); // generic heading is not a name
        expect("HORARIO: Matemática Lunes 10:00",""); // reject day/hour as title
        expect("Semestre: VI Ciclo\nLunes","VI Ciclo");
        System.out.println("PASS: explicit OCR title, weekly title, no-title and bad titles");
    }
}
