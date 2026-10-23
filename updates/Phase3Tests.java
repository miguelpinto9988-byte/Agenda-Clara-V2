import pe.agendaclara.app.*;
import java.time.*;
import java.util.*;

public final class Phase3Tests {
    static int checks;
    static final ZoneId Z=ZoneId.of("America/Lima");
    static final long NOW=ZonedDateTime.of(2026,10,23,8,0,0,0,Z).toInstant().toEpochMilli();
    static void check(boolean valid,String label){checks++;if(!valid)throw new AssertionError(label);}
    static ConversationAnalyzer.Message msg(String id,String body,long time,String sender){
        ConversationAnalyzer.Message m=new ConversationAnalyzer.Message();
        m.id=id;m.body=body;m.time=time;m.sender=sender;return m;
    }
    public static void main(String[] args){
        for(String text:new String[]{
            "No habrá examen mañana a las 3 pm",
            "Ya no hay reunión mañana a las 3 pm",
            "No hace falta enviar informe mañana a las 3 pm",
            "No se realizará el simulacro mañana a las 3 pm"}){
            check(MessageParser.parse(text,NOW,Z,false).isEmpty(),"No inventar tarea cancelada: "+text);
        }
        for(String text:new String[]{
            "Simulacro de evacuación mañana a las 3 pm",
            "Prueba de ciencias mañana a las 3 pm",
            "Parcial de matemáticas mañana a las 3 pm",
            "Control de lectura mañana a las 3 pm"}){
            check(MessageParser.parse(text,NOW,Z,false).size()==1,"Actividad académica: "+text);
        }
        ConversationAnalyzer.Message original=msg("msg100","Entregar el informe mañana a las 3 pm",NOW,"profesor");
        ConversationAnalyzer.Message newer=msg("msg101","Entregar el informe hasta mañana a las 5 pm",NOW+300_000,"profesor");
        newer.reply="msg100";newer.quoted=original.body;
        List<ConversationAnalyzer.Finding> f=ConversationAnalyzer.analyze(Arrays.asList(original,newer),Z,NOW);
        check(f.size()==1,"Un solo aviso para fecha modificada");
        check(f.get(0).key.equals("msg100:0"),"Clave estable de la tarea original");
        check(f.get(0).proposal.ambiguous,"Nueva fecha requiere confirmación");
        check(Instant.ofEpochMilli(f.get(0).proposal.due).atZone(Z).getHour()==17,"Fecha más reciente");
        check(f.get(0).proposal.reason.contains("Comprueba"),"Explicación visible y revisable");
        ConversationAnalyzer.Message unrelated=msg("msg102","Gracias, profesor",NOW+400_000,"alumna");
        f=ConversationAnalyzer.analyze(Arrays.asList(original,newer,unrelated),Z,NOW);
        check(f.size()==1,"El contexto no genera un segundo aviso");
        System.out.println("{\"checks\":"+checks+",\"passed\":"+checks+",\"failed\":0,\"scope\":\"Spanish cues, quoted changes and explicit review\"}");
    }
}