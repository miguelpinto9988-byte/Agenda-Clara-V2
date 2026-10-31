import pe.agendaclara.app.*;
import java.time.*;
import java.util.*;

/** Entirely synthetic examples; never use real chat histories as fixtures. */
public final class WhatsAppUnderstandingPrototypeTests {
    static ZoneId zone=ZoneId.of("America/Lima");
    static long now=ZonedDateTime.of(2026,10,31,8,0,0,0,zone).toInstant().toEpochMilli();
    static int checks=0;
    static void check(boolean test,String description){checks++;if(!test)throw new AssertionError(description);}
    static ConversationAnalyzer.Message msg(String id,String body,int minutes,String sender){
        ConversationAnalyzer.Message m=new ConversationAnalyzer.Message();
        m.id=id;m.body=body;m.sender=sender;m.time=now+minutes*60_000L;
        return m;
    }
    public static void main(String[] args){
        String four="Entregar el informe de Historia mañana a las 15:00; Revisar el contrato hoy a las 18:00; " +
            "Hay que comprar repuestos mañana a las 10:00; Tienen que resolver los ejercicios de Álgebra mañana a las 16:00";
        List<MessageParser.Proposal> parts=MessageParser.parse(four,now,zone,false);
        check(parts.size()==4,"Four independent activities in one message: "+parts.size());
        check(WhatsAppUnderstandingEngine.split("Entregar informe de Historia y enviar fotos de Biología").size()==2,"Independent conjunctions split");
        check(WhatsAppUnderstandingEngine.split("Leer y resumir el capítulo de Historia").size()==1,"Single compound task stays together");
        check(!WhatsAppUnderstandingEngine.related("Entregar informe de Historia","Enviar informe de Biología"),"Different subjects must stay separate");
        check(WhatsAppUnderstandingEngine.related("Enviar el informe de Historia mañana","Recuerden entregar informe de Historia mañana"),"Equivalent activity despite different verbs");
        check(!WhatsAppUnderstandingEngine.related("Informe mañana","Informe el viernes"),"Generic mentions are not safely identical");
        check(MessageParser.parse("No hay examen mañana. Se cancela la reunión.",now,zone,false).isEmpty(),"Negated/cancelled announcements yield no tasks");
        check(MessageParser.parse("¿Tenemos que enviar el informe mañana?",now,zone,false).isEmpty(),"Questions are not instructions");
        List<ConversationAnalyzer.Message> pair=Arrays.asList(
            msg("a","Entregar el informe de Historia mañana a las 15:00",0,"profesor"),
            msg("b","Recuerden enviar el informe de Historia mañana a las 15:00",3,"profesor"));
        List<ConversationAnalyzer.Finding> found=ConversationAnalyzer.analyze(pair,zone,now+5*60_000L);
        check(found.size()==1,"Two messages about same activity produce one proposal, got "+found.size());
        check(found.get(0).proposal.reason.contains("varios mensajes"),"Grouped proposal is explained");
        List<ConversationAnalyzer.Message> separate=Arrays.asList(
            msg("c","Entregar informe de Historia mañana a las 15:00",0,"profesor"),
            msg("d","Entregar informe de Biología mañana a las 15:00",1,"profesor"));
        check(ConversationAnalyzer.analyze(separate,zone,now+5*60_000L).size()==2,"Different subjects remain two activities");
        List<ConversationAnalyzer.Message> differentSenders=Arrays.asList(
            msg("e","Entregar informe de Historia mañana a las 15:00",0,"profesor"),
            msg("f","Entregar informe de Historia mañana a las 15:00",1,"alumno"));
        check(ConversationAnalyzer.analyze(differentSenders,zone,now+5*60_000L).size()==2,"Different senders must not be inferred as duplicate");
        List<ConversationAnalyzer.Message> conflictingDates=Arrays.asList(
            msg("g","Entregar informe de Historia mañana a las 15:00",0,"profesor"),
            msg("h","Entregar informe de Historia pasado mañana a las 15:00",2,"profesor"));
        found=ConversationAnalyzer.analyze(conflictingDates,zone,now+5*60_000L);
        check(found.size()==2,"Contradictory dates without correction should require review");
        check(found.get(1).proposal.ambiguous,"Date conflict explicitly marked ambiguous");
        List<ConversationAnalyzer.Message> corrected=Arrays.asList(
            msg("i","Entregar informe de Historia mañana a las 15:00",0,"profesor"),
            msg("j","Corrección: el informe de Historia pasa al 02/11/2026 a las 15:00",4,"profesor"));
        found=ConversationAnalyzer.analyze(corrected,zone,now+6*60_000L);
        check(found.size()==1,"Explicit contextual date correction yields one proposal: "+found.size());
        check(found.get(0).proposal.reason.contains("corrección contextual"),"Date change requires user review");
        check(Instant.ofEpochMilli(found.get(0).proposal.due).atZone(zone).toLocalDate().equals(LocalDate.of(2026,11,2)),"Latest date applied to suggestion");
        System.out.println("PASS WhatsApp understanding prototype: "+checks+" checks");
    }
}
