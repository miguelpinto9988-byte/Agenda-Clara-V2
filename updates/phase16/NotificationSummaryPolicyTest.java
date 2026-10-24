package pe.agendaclara.app;
public final class NotificationSummaryPolicyTest {
    private static void expect(boolean v,String message){if(!v)throw new AssertionError(message);}
    public static void main(String[] args){
        expect(NotificationSummaryPolicy.isSummary("3 mensajes nuevos"),"Spanish summary excluded");
        expect(NotificationSummaryPolicy.isSummary("2 new messages"),"English summary excluded");
        expect(NotificationSummaryPolicy.isSummary(""),"Empty preview excluded");
        expect(!NotificationSummaryPolicy.isSummary("Mañana entregar el informe de investigación"),"Actionable notification retained");
        expect(!NotificationSummaryPolicy.isSummary("2 documentos y una presentación para el lunes"),"Academic details retained");
        System.out.println("PASS: notification preview filters");
    }
}
