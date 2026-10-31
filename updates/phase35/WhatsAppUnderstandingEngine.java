package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;

/** Privacy-first, offline review prototype for multi-activity WhatsApp messages.
 * It only groups suggestions; it neither writes tasks nor reads WhatsApp directly. */
public final class WhatsAppUnderstandingEngine {
    private WhatsAppUnderstandingEngine() {}
    private static final Pattern NUMBERED=Pattern.compile("(?m)(?:^|\\n)\\s*(?:[0-9]{1,2}[.)]|[-•*])\\s+");
    private static final Pattern ACTION=Pattern.compile("(?i)^(?:(?:para (?:el )?\\w+|mañana|hoy|el (?:lunes|martes|miercoles|miércoles|jueves|viernes|sábado|sabado|domingo))\\s*[:,]?\\s+)?(?:hay que |tenemos que |tienen que |deben |por favor |recuerden |también |tambien )?(?:entregar|envia(?:r|n)|enviar|subir|realizar|resolver|hacer|preparar|completar|leer|estudiar|repasar|presentar|llevar|traer|comprar|pagar|asistir|revisar|redactar|participar|examen|evaluación|evaluacion|reunión|reunion|taller|exposición|exposicion|actividad|tarea)\\b");
    private static final Pattern CONNECT=Pattern.compile("(?i)\\s+(?:y|adem[aá]s|tambi[eé]n|luego|aparte|por otro lado)\\s+(?=(?:(?:para\\s+)?(?:ma[ñn]ana|hoy|el\\s+(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo))\\s*[:,]?\\s+)?(?:hay que\\s+|tenemos que\\s+|deben\\s+|recuerden\\s+)?(?:entregar|enviar|subir|resolver|realizar|hacer|preparar|completar|leer|estudiar|repasar|presentar|llevar|traer|comprar|pagar|asistir|revisar|redactar|examen|reuni[oó]n|taller|exposici[oó]n|actividad)\\b)");
    private static final Pattern SENTENCE=Pattern.compile("(?<=[.!?;])\\s+(?=(?:(?:\\d+[.)]\\s*)|(?:para\\s+)?(?:ma[ñn]ana|hoy|el\\s+\\w+)[,:]?\\s+|(?:entregar|enviar|examen|reuni[oó]n|tarea|actividad|por favor|hay que|deben)\\b))",Pattern.CASE_INSENSITIVE);
    private static final Pattern STOP=Pattern.compile("(?i)\\b(?:que|el|la|los|las|un|una|de|del|para|por|en|al|con|es|se|ser|sera|será|hay|toca|tienen|tenemos|deben|debe|tenemos|recuerden|recuerda|favor|mañana|manana|hoy|pasado|lunes|martes|miercoles|jueves|viernes|sabado|domingo|proximo|proxima|semana|este|esta|ese|esa|a|las|antes|hasta|fecha|plazo|limite|del|dia|dias|hora|horas|am|pm|tarea|actividad|hacer|realizar|presentar|enviar|entregar|subir|recordatorio|recuerden|tambien|también|ademas|además|nuevo|nueva|cambio|mejor|correccion|rectificacion|entregara|entregaran|ahora|queda|se|quedo)\\b");
    private static final Pattern GENERIC=Pattern.compile("(?i)^(?:informe|trabajo|proyecto|examen|reunion|evaluacion|prueba|ejercicios|lectura|formulario|documento|pago)$");
    private static String normalize(String s){return Normalizer.normalize(s.toLowerCase(Locale.ROOT),Normalizer.Form.NFD).replaceAll("\\p{M}","");}
    private static String trim(String s){return s.replaceFirst("^\\s*(?:\\d+[.)]|[-•*])\\s*","").trim();}
    /** Split explicit multiple independent instructions but keep compound tasks intact. */
    public static List<String> split(String text){
        if(text==null||text.trim().isEmpty())return Collections.emptyList();
        String limited=text.substring(0,Math.min(text.length(),12000)).replace("\r\n","\n").replace('\r','\n');
        limited=NUMBERED.matcher(limited).replaceAll("\n");
        limited=CONNECT.matcher(limited).replaceAll("; ");
        limited=SENTENCE.matcher(limited).replaceAll("\n");
        String[] chunks=limited.split("[;\\n]+");
        List<String> result=new ArrayList<>();
        for(String part:chunks){
            String item=trim(part);
            if(item.isEmpty())continue;
            // Only produce independent candidates if a real directive is present.
            if(result.size()<40)result.add(item);
        }
        return result;
    }
    /** Folds accent/spelling variants into a semantic subject key; no content is exported. */
    public static String key(String text){
        if(text==null)return "";
        String normalized=normalize(text).replaceAll("(?:\\d{1,2}[:./-])+\\d{0,4}"," ");
        normalized=STOP.matcher(normalized).replaceAll(" ").replaceAll("[^a-z0-9 ]+"," ").trim();
        SortedSet<String> words=new TreeSet<>();
        for(String token:normalized.split("\\s+")){
            if(token.length()<3||token.matches("\\d+"))continue;
            // Common inflections; deliberately conservative on word stems.
            if(token.equals("informes"))token="informe";
            else if(token.equals("trabajos"))token="trabajo";
            else if(token.equals("ejercicios"))token="ejercicio";
            words.add(token);
        }
        return String.join(" ",words);
    }
    private static Set<String> tokens(String key){
        Set<String> out=new HashSet<>();for(String word:key.split(" "))if(!word.isEmpty())out.add(word);return out;
    }
    /** Require shared topic-specific evidence; generic nouns alone cannot merge tasks. */
    public static boolean related(String a,String b){
        String ka=key(a),kb=key(b);
        if(ka.isEmpty()||kb.isEmpty())return false;
        if(ka.equals(kb)){
            if(!ka.contains(" ")&&GENERIC.matcher(ka).matches())return false;
            return true;
        }
        Set<String> aa=tokens(ka),bb=tokens(kb);
        aa.retainAll(bb);
        int shared=aa.size();
        if(shared==0)return false;
        int max=Math.max(tokens(ka).size(),tokens(kb).size());
        boolean meaningful=false;
        for(String word:aa)if(!GENERIC.matcher(word).matches())meaningful=true;
        return meaningful && shared>=2 && shared*3>=max*2;
    }
    private static final class Last {ConversationAnalyzer.Finding finding;long timestamp;Last(ConversationAnalyzer.Finding f){finding=f;timestamp=f.message.time;}}
    private static String author(ConversationAnalyzer.Finding f){return f.message.sender==null?"":f.message.sender.trim();}
    /** Group semantically equivalent proposals from the same author within 48h.
     * No accidental correlation across different senders, chat imports or topics.
     * Retains original origin IDs for stable review and never saves a task. */
    public static List<ConversationAnalyzer.Finding> merge(List<ConversationAnalyzer.Finding> findings){
        if(findings==null||findings.size()<2)return findings==null?Collections.emptyList():findings;
        List<ConversationAnalyzer.Finding> out=new ArrayList<>();
        Map<String,List<Last>> byAuthor=new HashMap<>();
        final long window=48L*60*60*1000;
        for(ConversationAnalyzer.Finding f:findings){
            if(f==null||f.proposal==null||f.message==null)continue;
            String sender=author(f);
            String topic=f.proposal.original;
            if(sender.isEmpty()||key(topic).isEmpty()){out.add(f);continue;}
            List<Last> seen=byAuthor.computeIfAbsent(sender,x->new ArrayList<>());
            Last match=null;
            for(int i=seen.size()-1;i>=0&&i>=seen.size()-60;i--){
                Last candidate=seen.get(i);
                if(f.message.time<candidate.timestamp || f.message.time-candidate.timestamp>window)continue;
                if(related(topic,candidate.finding.proposal.original)){
                    match=candidate;break;
                }
            }
            if(match==null){out.add(f);seen.add(new Last(f));continue;}
            MessageParser.Proposal previous=match.finding.proposal, next=f.proposal;
            boolean sameDate=previous.dateKnown==next.dateKnown&&(!previous.dateKnown||previous.due==next.due);
            boolean explicitCorrection=normalize(topic).matches("(?s).*(?:correccion|rectificacion|mejor (?:el|a las)|cambio de fecha|se reprograma|nueva fecha|en vez de|en lugar de|ahora sera).*");
            if(!sameDate&&!explicitCorrection){
                // Different deadlines without an explicit correction must stay visible for review.
                next.ambiguous=true;
                next.reason="Hay otro anuncio parecido con fecha diferente. Confirma si son la misma actividad. "+next.reason;
                out.add(f);seen.add(new Last(f));continue;
            }
            if(explicitCorrection&&next.dateKnown){
                previous.due=next.due;previous.dateKnown=true;previous.timeKnown=next.timeKnown;
                previous.ambiguous=true;
                previous.reason="Se identificó una corrección de fecha para una actividad relacionada. Verifica la información antes de guardar. "+previous.reason;
            } else {
                previous.reason="Actividad mencionada en varios mensajes relacionados. Se agrupó una sola propuesta para revisión. "+previous.reason;
            }
            match.timestamp=f.message.time;
        }
        return out;
    }
    /** Corrections without reply IDs are linked only with an explicit topic and author. */
    public static void applyCorrections(List<ConversationAnalyzer.Finding> grouped,
                                        List<ConversationAnalyzer.Message> ordered,
                                        java.time.ZoneId zone){
        final long window=48L*60*60*1000;
        Pattern change=Pattern.compile("(?i)\\b(?:correcci[oó]n|rectificaci[oó]n|cambio de fecha|nueva fecha|en vez de|en lugar de|se reprograma|mejor el|mejor a las)\\b");
        for(ConversationAnalyzer.Message m:ordered){
            if(m==null||m.body==null||m.body.length()>2000||m.reply!=null&&!m.reply.isEmpty()
                    ||m.sender==null||m.sender.isEmpty()||!change.matcher(m.body).find())continue;
            MessageParser.Proposal revised=MessageParser.parseOne(m.body,m.time,zone,true);
            if(!revised.dateKnown||revised.due<=0)continue;
            ConversationAnalyzer.Finding best=null;
            for(ConversationAnalyzer.Finding f:grouped){
                if(f.message.time>m.time||m.time-f.message.time>window)continue;
                if(!m.sender.equals(f.message.sender))continue;
                if(related(m.body,f.proposal.original)){
                    if(best==null||f.message.time>best.message.time)best=f;
                }
            }
            if(best==null)continue;
            MessageParser.Proposal current=best.proposal;
            if(current.due==revised.due)continue;
            current.original=current.original+"\nActualización vinculada: "+m.body;
            current.due=revised.due;
            current.dateKnown=true;
            current.timeKnown=revised.timeKnown;
            current.ambiguous=true;
            current.reason="Posible corrección contextual del plazo; confirma la fecha antes de guardar. "+current.reason;
        }
    }
}
