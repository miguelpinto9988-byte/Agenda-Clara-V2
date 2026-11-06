package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;

/**
 * Semantic safeguards for timetable OCR. No remote model or guessed course is used.
 * Distinct head subjects are protected from an accidental generic-word match.
 */
public final class ScheduleCourseSemanticGuard {
    private ScheduleCourseSemanticGuard() {}

    private static final Set<String> LOW_INFORMATION = new HashSet<>(Arrays.asList(
        "de", "del", "la", "el", "los", "las", "a", "al", "en", "y", "e", "para",
        "con", "sin", "por", "un", "una", "que", "curso", "asignatura", "grupo",
        "educacion", "educativa", "educativas", "educativo", "educativos",
        "educacional", "educacionales", "pedagogico", "pedagogica",
        "general", "basico", "basica", "especial", "universitario",
        "universitaria", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"));
    private static final Pattern CODE_TRAIL = Pattern.compile(
        "(?iu)^(.+?)(\\s*\\([a-z]{1,3}\\))\\s+([\\p{L}]{5,})(\\s+(?:i|ii|iii|iv|v|vi|vii|viii|ix|x))?$");
    private static final Pattern LEVEL = Pattern.compile(
        "(?:^| )(?:(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)|[1-9])$");
    private static String fold(String raw) {
        return Normalizer.normalize(raw == null ? "" : raw, Normalizer.Form.NFD)
            .replaceAll("\\p{M}+", "").toLowerCase(Locale.ROOT)
            .replaceAll("[^\\p{L}\\p{N}]+", " ").trim().replaceAll("\\s+", " ");
    }
    private static boolean sameWord(String left, String right) {
        String a = fold(left), b = fold(right);
        return a.equals(b) || (a.length() >= 5 && (a+"s").equals(b)) ||
            (b.length() >= 5 && (b+"s").equals(a));
    }
    /** Only strip duplicated OCR words appearing AFTER an existing short course-code marker.
     * Roman numerals are deliberately retained: I/II might denote separate modules. */
    public static String cleanOcrName(String raw) {
        if (raw == null) return "";
        String name = raw.trim().replaceAll("\\s+", " ");
        Matcher match = CODE_TRAIL.matcher(name);
        if (!match.matches()) return name;
        String repeated = match.group(3);
        String[] words = fold(match.group(1)).split(" ");
        boolean alreadyPresent = false;
        for (String word : words) {
            if (sameWord(word, repeated)) { alreadyPresent = true; break; }
        }
        if (!alreadyPresent) return name;
        return (match.group(1) + match.group(2) +
            (match.group(4) == null ? "" : match.group(4))).trim()
            .replaceAll("\\s+", " ");
    }
    public static boolean wasCleaned(String name) {
        return name != null && !cleanOcrName(name).equals(name.trim());
    }
    public static Set<String> informative(String name) {
        LinkedHashSet<String> result = new LinkedHashSet<>();
        for (String word : fold(cleanOcrName(name)).split(" ")) {
            if (word.length() >= 3 && !LOW_INFORMATION.contains(word)) result.add(word);
        }
        return result;
    }
    public static String sharedInformative(String left, String right) {
        Set<String> known = informative(right);
        for (String token : informative(left)) if (known.contains(token)) return token;
        return "";
    }
    /** Course A + adjective "educativa" does NOT correlate with unrelated course B. */
    public static boolean meaningfulOverlap(String left, String right) {
        return !sharedInformative(left,right).isEmpty();
    }
    public static boolean strongBeginning(String left, String right) {
        String[] a = fold(cleanOcrName(left)).split(" ");
        String[] b = fold(cleanOcrName(right)).split(" ");
        return a.length>0 && b.length>0 && a[0].equals(b[0])
            && a[0].length() >= 4 && !LOW_INFORMATION.contains(a[0]);
    }
    public static String level(String name) {
        String key = fold(cleanOcrName(name));
        Matcher m = LEVEL.matcher(key);
        return m.find() ? m.group().trim() : "";
    }
    public static String withoutLevel(String name) {
        String key = fold(cleanOcrName(name));
        return LEVEL.matcher(key).replaceFirst("").trim();
    }
    /** Only one named level is uncertain; different explicit levels remain distinct. */
    public static boolean ambiguousLevel(String left, String right) {
        String a = level(left), b = level(right);
        if (a.equals(b) || (!a.isEmpty() && !b.isEmpty())) return false;
        String baseA = withoutLevel(left), baseB = withoutLevel(right);
        return !baseA.isEmpty() && (baseA.equals(baseB) ||
            (strongBeginning(baseA,baseB) && (baseA.startsWith(baseB+" ") ||
                                                    baseB.startsWith(baseA+" "))));
    }
    public static int distinctCourseCount(Collection<ScheduleEntry> sessions) {
        LinkedHashSet<String> distinct = new LinkedHashSet<>();
        if (sessions != null) for (ScheduleEntry item : sessions)
            if (item != null) distinct.add(ScheduleCourseColors.identity(item.course));
        distinct.remove("");
        return distinct.size();
    }
    /** Internal review signals are computed without altering any selected session. */
    public static List<String> audit(List<ScheduleEntry> sessions) {
        ArrayList<String> notes = new ArrayList<>();
        if (sessions == null) return notes;
        LinkedHashMap<String,String> names = new LinkedHashMap<>();
        for (ScheduleEntry session : sessions) {
            if (!ScheduleEntry.valid(session)) {
                notes.add("Se detectó una clase incompleta; revisa su día, curso u hora.");
                continue;
            }
            names.putIfAbsent(ScheduleCourseColors.identity(session.course), session.course);
        }
        ArrayList<String> items = new ArrayList<>(names.values());
        for (int i=0;i<items.size();i++) for (int j=i+1;j<items.size();j++) {
            String a=items.get(i), b=items.get(j);
            ScheduleCourseRecognition.Relation relation=ScheduleCourseRecognition.compare(a,b);
            if (relation == ScheduleCourseRecognition.Relation.DIFFERENT) continue;
            String reason=relation == ScheduleCourseRecognition.Relation.LEVEL_UNCERTAIN
                ? "Posible nivel I/II diferente" : "Posibles nombres OCR de un mismo curso";
            notes.add(reason+": «"+a+"» / «"+b+"». Se mantendrán separados hasta confirmar.");
        }
        for (int i=0;i<sessions.size();i++) for(int j=i+1;j<sessions.size();j++) {
            ScheduleEntry a=sessions.get(i), b=sessions.get(j);
            if (!ScheduleEntry.valid(a) || !ScheduleEntry.valid(b)) continue;
            if (a.day==b.day && a.start==b.start && a.end==b.end &&
                ScheduleCourseColors.same(a.course,b.course)) {
                notes.add("Bloque OCR repetido: "+a.course+" · "+ScheduleEntry.dayName(a.day)+
                    " "+ScheduleEntry.clock(a.start)+". Se revisará antes de guardar.");
            }
        }
        return notes;
    }
}
