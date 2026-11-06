package pe.agendaclara.app;

import java.text.Normalizer;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Evidence-based resolution of numbered partial exams in a syllabus.
 * Mentions of "examen tema 14" are not independent calendar entries.
 * Correlates the same ordinal across pages but NEVER guesses an exact date.
 */
public final class SyllabusContextualPartials {
    private SyllabusContextualPartials() {}

    private static final String ORD =
        "(?:primer(?:o|a)?|segund[oa]|tercer(?:o|a)?|cuart[oa]|quint[oa]|" +
        "sext[oa]|septim[oa]|octav[oa]|noven[oa]|decim[oa]|" +
        "[1-9](?:er|ro|do|to|°|º|ª)?|10(?:mo|°|º)?|i{1,3}|iv|v|vi|vii|viii|ix|x)";
    private static final Pattern BEFORE = Pattern.compile(
        "\\b(" + ORD + ")\\s+(?:examen(?:es)?|evaluacion|parcial)\\b");
    private static final Pattern AFTER = Pattern.compile(
        "\\b(?:examen|evaluacion)\\s+(?:parcial\\s+)?(" + ORD + ")\\b");
    private static final Pattern PARTIAL_AFTER = Pattern.compile(
        "\\bparcial\\s*(?:n[.°ºo]*\\s*)?(" + ORD + ")\\b");
    private static final Pattern PARTIAL = Pattern.compile("\\bparcial(?:es)?\\b");
    private static final Pattern TOPIC = Pattern.compile(
        "\\btemas?\\s*(?:n[.°ºo]*\\s*)?([0-9]{1,2}(?:\\s*(?:,|y|al|a|-|–)\\s*[0-9]{1,2})*)\\b");
    private static final String MONTHS = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|" +
        "septiembre|setiembre|octubre|noviembre|diciembre|ene|feb|mar|abr|may|jun|jul|ago|" +
        "sep|set|oct|nov|dic";
    // An explicit day/month expression is mandatory; a weekly heading is not an exact date.
    private static final Pattern DATE_TOKEN = Pattern.compile(
        "(?iu)(?<![0-9])(?:20[0-9]{2}-[01]?[0-9]-[0-3]?[0-9]|" +
        "[0-3]?[0-9][./-][01]?[0-9][./-](?:20[0-9]{2}|[0-9]{2})|" +
        "[0-3]?[0-9]\\s+(?:de\\s+)?(?:" + MONTHS +
        ")(?:\\.?\\s+(?:de\\s+|del\\s+)?20[0-9]{2})?)(?![0-9])");
    private static final Pattern DATE_ONLY = Pattern.compile(
        "(?iu)^(?:(?:fecha|dia|día)\\s*(?:del\\s+examen)?\\s*[:=-]\\s*)?" +
        "(?:[0-9].*|del\\s+[0-9].*)$");
    private static final Pattern DISTINCT_EXAMS = Pattern.compile(
        "\\b(?:examen\\s+(?:final|oral|practico|escrito|sustitutorio|extraordinario|" +
        "de\\s+recuperacion|de\\s+suficiencia)|evaluacion\\s+final|" +
        "practica\\s+calificada|control\\s+de\\s+lectura|certamen|quiz|" +
        "prueba\\s+(?:parcial|final|oral|escrita|practica|de\\s+unidad))\\b");

    private static final String[] LABELS = {
        "", "Primer", "Segundo", "Tercer", "Cuarto", "Quinto", "Sexto",
        "Séptimo", "Octavo", "Noveno", "Décimo"
    };

    private static final class Evidence {
        final String text;
        final int page, ordinal;
        final boolean anchor, dateConflict;
        final String topic;
        final LocalDate date;
        Evidence(int page, int ordinal, String text, boolean anchor, String topic,
                 LocalDate date, boolean conflict) {
            this.page = page;
            this.ordinal = ordinal;
            this.text = text;
            this.anchor = anchor;
            this.topic = topic;
            this.date = date;
            this.dateConflict = conflict;
        }
    }

    private static final class Group {
        final int ordinal;
        final ArrayList<Evidence> evidence = new ArrayList<>();
        final LinkedHashSet<String> topics = new LinkedHashSet<>();
        final LinkedHashSet<LocalDate> dates = new LinkedHashSet<>();
        int page;
        boolean anchored, conflicting;
        Group(int ordinal) { this.ordinal = ordinal; }
        void add(Evidence item) {
            evidence.add(item);
            if (item.anchor) {
                anchored = true;
                if (page == 0) page = item.page;
            }
            if (!item.topic.isEmpty()) topics.add(item.topic);
            if (item.date != null) dates.add(item.date);
            if (item.dateConflict) conflicting = true;
        }
        SyllabusEventParser.Event result() {
            if (!anchored) return null;
            String title = LABELS[ordinal] + " examen parcial";
            if (topics.size() == 1) title += " · Tema " + topics.iterator().next();
            if (topics.size() > 1) title += " · Temas por confirmar";
            LocalDate day = !conflicting && dates.size() == 1 ?
                dates.iterator().next() : null;
            if (conflicting || dates.size() > 1) title += " · Verificar fecha";
            StringBuilder evidenceText = new StringBuilder();
            // Prioritize an explicitly dated reference, then the partial anchor.
            for (Evidence item : evidence) {
                if (item.date == null) continue;
                append(evidenceText, item);
            }
            for (Evidence item : evidence) {
                if (item.date != null) continue;
                append(evidenceText, item);
            }
            String source = evidenceText.toString();
            return new SyllabusEventParser.Event(
                title, "Examen", day, day, day, 0, 0, page, source, source);
        }
    }

    private static void append(StringBuilder output, Evidence item) {
        String text = "Pág. " + item.page + ": " + item.text;
        if (output.indexOf(text) >= 0) return;
        if (output.length() > 0) output.append(" | ");
        if (output.length() + text.length() < 950) output.append(text);
    }

    private static String fold(String text) {
        return Normalizer.normalize(
                text == null ? "" : text.toLowerCase(Locale.ROOT), Normalizer.Form.NFD)
                .replaceAll("\\p{M}+", "")
                .replaceAll("\\s+", " ").trim();
    }

    private static int ordinalValue(String word) {
        String x = fold(word).replaceAll("[°ºª]", "");
        if (x.startsWith("decim") || x.startsWith("10")) return 10;
        if (x.startsWith("primer") || x.startsWith("1")) return 1;
        if (x.startsWith("segund") || x.startsWith("2")) return 2;
        if (x.startsWith("tercer") || x.startsWith("3")) return 3;
        if (x.startsWith("cuart") || x.startsWith("4")) return 4;
        if (x.startsWith("quint") || x.startsWith("5")) return 5;
        if (x.startsWith("sext") || x.startsWith("6")) return 6;
        if (x.startsWith("septim") || x.startsWith("7")) return 7;
        if (x.startsWith("octav") || x.startsWith("8")) return 8;
        if (x.startsWith("noven") || x.startsWith("9")) return 9;
        for (int n = 1; n <= 10; n++) {
            String[] roman = {"", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"};
            if (roman[n].equals(x)) return n;
        }
        return 0;
    }

    private static int ordinal(String text) {
        String s = fold(text);
        LinkedHashSet<Integer> candidates = new LinkedHashSet<>();
        for (Pattern pattern : Arrays.asList(BEFORE, AFTER, PARTIAL_AFTER)) {
            Matcher m = pattern.matcher(s);
            while (m.find()) {
                int value = ordinalValue(m.group(1));
                if (value > 0) candidates.add(value);
            }
        }
        // Never arbitrarily attribute a row containing several different exams.
        return candidates.size() == 1 ? candidates.iterator().next() : 0;
    }

    private static boolean isAnchor(String text) {
        return PARTIAL.matcher(fold(text)).find();
    }

    private static String topic(String text) {
        Matcher m = TOPIC.matcher(fold(text));
        return m.find() ? m.group(1).replaceAll("\\s+", " ") : "";
    }

    private static final class DateFinding {
        final LocalDate date;
        final boolean conflict;
        DateFinding(LocalDate date, boolean conflict) {
            this.date = date;
            this.conflict = conflict;
        }
    }

    private static DateFinding dated(String text, SyllabusDateInterpreter.CalendarInfo cal) {
        Matcher matcher = DATE_TOKEN.matcher(text);
        int tokens = 0;
        LocalDate found = null;
        while (matcher.find()) {
            tokens++;
            if (tokens > 1) return new DateFinding(null, true);
            found = SyllabusDateInterpreter.interpret(matcher.group(), cal).exact;
        }
        return new DateFinding(found, false);
    }

    private static boolean pureAdjacentDate(String text) {
        String x = text.trim();
        if (x.length() > 75 || !DATE_ONLY.matcher(x).matches()) return false;
        if (ordinal(x) > 0 || fold(x).matches(".*\\b(?:examen|parcial|tema)\\b.*"))
            return false;
        return DATE_TOKEN.matcher(x).find();
    }

    private static List<Evidence> collect(List<SyllabusEventParser.Page> pages) {
        ArrayList<Evidence> all = new ArrayList<>();
        SyllabusDateInterpreter.CalendarInfo calendar = SyllabusDateInterpreter.calendar(pages);
        for (SyllabusEventParser.Page page : pages) {
            if (page == null || page.text.isEmpty()) continue;
            String[] lines = page.text.split("\\r?\\n");
            for (int i = 0; i < lines.length; i++) {
                String line = lines[i].trim().replaceAll("\\s+", " ");
                if (line.length() < 5 || line.length() > 450) continue;
                int n = ordinal(line);
                if (n == 0) continue;
                // "Examen tema 14" has no ordinal anchored to an exam.
                boolean anchor = isAnchor(line);
                DateFinding date = dated(line, calendar);
                if (date.date == null && !date.conflict) {
                    // Adjacent dates are only considered when the whole cell looks like a date,
                    // never an unrelated section, topic or another exam row.
                    for (int near : new int[] {i - 1, i + 1}) {
                        if (near < 0 || near >= lines.length) continue;
                        String candidate = lines[near].trim();
                        if (!pureAdjacentDate(candidate)) continue;
                        DateFinding neighbor = dated(candidate, calendar);
                        if (neighbor.conflict) {
                            date = neighbor;
                            break;
                        }
                        if (neighbor.date != null) {
                            date = neighbor;
                            break;
                        }
                    }
                }
                all.add(new Evidence(page.number, n, line, anchor, topic(line),
                        date.date, date.conflict));
            }
        }
        return all;
    }

    /** Preserves explicitly classified exams while omitting topical mentions. */
    private static boolean keepStandalone(SyllabusEventParser.Event event) {
        if (!"Examen".equals(event.type)) return true; // Final projects/deliverables.
        String text = fold(event.title + " " + event.sourceText);
        if (ordinal(text) != 0) return false; // Numbered partials are merged above.
        return DISTINCT_EXAMS.matcher(text).find();
    }

    public static List<SyllabusEventParser.Event> resolve(
            List<SyllabusEventParser.Page> pages,
            List<SyllabusEventParser.Event> preliminary) {
        ArrayList<SyllabusEventParser.Event> result = new ArrayList<>();
        if (pages == null || pages.isEmpty()) return result;
        TreeMap<Integer, Group> groups = new TreeMap<>();
        for (Evidence evidence : collect(pages)) {
            Group group = groups.get(evidence.ordinal);
            if (group == null) {
                group = new Group(evidence.ordinal);
                groups.put(evidence.ordinal, group);
            }
            group.add(evidence);
        }
        for (Map.Entry<Integer, Group> item : groups.entrySet()) {
            SyllabusEventParser.Event event = item.getValue().result();
            if (event != null) result.add(event);
        }
        if (preliminary != null) {
            for (SyllabusEventParser.Event event : preliminary) {
                if (event != null && keepStandalone(event)) result.add(event);
            }
        }
        return result;
    }
}
