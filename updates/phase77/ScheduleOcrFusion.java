package pe.agendaclara.app;

import java.util.*;

/**
 * Reconciles rectangular, position-based and text-only timetable OCR.
 *
 * An additional reading is NEVER selected for import automatically: it is visible
 * in the review list, unchecked, until the user deliberately selects it.
 * This preserves plausible courses that an incomplete rectangle detector misses.
 */
public final class ScheduleOcrFusion {
    private ScheduleOcrFusion(){}
    public static final int MAX_ALTERNATIVES=32;

    public static String key(ScheduleEntry value) {
        if(value==null||value.course==null)return "";
        return value.day+"|"+value.start+"|"+value.end+"|"+
                ScheduleCourseColors.key(value.course);
    }

    private static boolean sameSession(ScheduleEntry a,ScheduleEntry b) {
        if(a.day!=b.day)return false;
        int overlap=Math.min(a.end,b.end)-Math.max(a.start,b.start);
        int duration=Math.min(a.end-a.start,b.end-b.start);
        if(overlap<=0||duration<=0||overlap<duration*.78)return false;
        ScheduleCourseRecognition.Relation relation=
            ScheduleCourseRecognition.compare(a.course,b.course);
        return relation==ScheduleCourseRecognition.Relation.EXACT||
               relation==ScheduleCourseRecognition.Relation.OCR_VARIANT;
    }

    private static boolean similarTime(ScheduleEntry a,ScheduleEntry b) {
        if(a.day!=b.day)return false;
        int overlap=Math.min(a.end,b.end)-Math.max(a.start,b.start);
        return overlap>0 && overlap>=.70*Math.min(a.end-a.start,b.end-b.start);
    }

    private static boolean hasCandidate(ScheduleParser.Result result) {
        return result!=null&&!result.candidates.isEmpty();
    }

    private static void supplement(ScheduleParser.Result destination,
                                   ScheduleParser.Result alternate,String label,
                                   Set<String> keys) {
        if(alternate==null)return;
        int added=0,discarded=0;
        for(ScheduleEntry proposed:alternate.candidates) {
            if(!ScheduleEntry.valid(proposed))continue;
            String fingerprint=key(proposed);
            if(fingerprint.isEmpty()||keys.contains(fingerprint))continue;
            boolean alreadyRead=false,conflicting=false;
            for(ScheduleEntry current:destination.candidates) {
                if(sameSession(current,proposed)) {
                    alreadyRead=true;
                    break;
                }
                if(similarTime(current,proposed))conflicting=true;
            }
            if(alreadyRead)continue;
            if(destination.reviewOnlyKeys.size()>=MAX_ALTERNATIVES) {
                discarded++;
                continue;
            }
            ScheduleEntry candidate=proposed.copy();
            destination.candidates.add(candidate);
            destination.reviewOnlyKeys.add(fingerprint);
            keys.add(fingerprint);
            added++;
            String title="Lectura complementaria sin marcar: «"+candidate.course+"» · "+
                ScheduleEntry.dayName(candidate.day)+" "+
                ScheduleEntry.clock(candidate.start)+"–"+
                ScheduleEntry.clock(candidate.end)+" ("+label+").";
            if(conflicting)title+=" Coincide en horario con otro bloque: elige cuál corresponde.";
            destination.uncertain.add(title);
        }
        if(discarded>0)
            destination.uncertain.add("Se encontraron "+discarded+
                " lecturas adicionales fuera del límite de revisión. "+
                "Revisa la imagen original o añade manualmente el curso.");
        if(added>0)
            destination.uncertain.add("Se recuperaron "+added+" posibles clases de "+
                label+". Están DESMARCADAS hasta que confirmes que existen.");
    }

    /**
     * Selects the strongest source with actual courses and adds remaining
     * readings only as optional candidates. Does not conflate two courses
     * occupying the same timetable cell.
     */
    public static ScheduleParser.Result reconcile(ScheduleParser.Result rectangles,
            ScheduleParser.Result virtual,ScheduleParser.Result lines) {
        ScheduleParser.Result primary=hasCandidate(rectangles)?rectangles:
            hasCandidate(virtual)?virtual:
            lines==null?new ScheduleParser.Result():lines;
        ScheduleParser.Result output=new ScheduleParser.Result();
        LinkedHashSet<String> keys=new LinkedHashSet<>();
        for(ScheduleEntry e:primary.candidates) {
            if(e==null||!ScheduleEntry.valid(e))continue;
            output.candidates.add(e.copy());
            keys.add(key(e));
        }
        output.uncertain.addAll(primary.uncertain);
        if(primary==rectangles) {
            supplement(output,virtual,"lectura por columnas",keys);
            supplement(output,lines,"lectura del texto",keys);
        }else if(primary==virtual) {
            supplement(output,lines,"lectura del texto",keys);
        }
        if(output.candidates.isEmpty())
            output.uncertain.add("No se recuperaron clases con día y hora verificables. "+
                "Registra manualmente los cursos que faltan.");
        return output;
    }
}
