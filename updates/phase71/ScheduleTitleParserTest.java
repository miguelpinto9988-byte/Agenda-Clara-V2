package pe.agendaclara.app;

/** Pure-Java, local tests for conservative schedule OCR header names. */
public final class ScheduleTitleParserTest {
    static void eq(String expected,String got){
        if(!expected.equals(got))throw new AssertionError("Expected "+expected+" got "+got);
    }
    public static void main(String[] args){
        eq("Educación 2026",ScheduleTitleParser.suggest(
            "HORARIO: Educación 2026\nLunes\nTendencias educativas 08:00"));
        eq("Ciclo V",ScheduleTitleParser.suggest("Ciclo - Ciclo V\nMartes"));
        eq("",ScheduleTitleParser.suggest("Lunes\nMartes\nTendencias Educativas"));
        eq("",ScheduleTitleParser.suggest("Horario de clases\nLunes\nMartes"));
        eq("",ScheduleTitleParser.suggest("Horario:\nLunes\nCurso 08:00"));
        System.out.println("PASS: títulos claros detectados, OCR ambiguo rechazado");
    }
}
