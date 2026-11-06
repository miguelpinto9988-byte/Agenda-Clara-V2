package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.List;

/** Groups evaluations by actionability across every course in one academic profile. */
public final class AcademicWidgetEvaluationOrder {
    private AcademicWidgetEvaluationOrder() {}

    public static final class Entry {
        public final String course;
        public final Task task;
        public Entry(String course, Task task) {
            if (task == null) throw new IllegalArgumentException("Missing evaluation task");
            this.course = course == null ? "" : course;
            this.task = task;
        }
    }

    private static int priority(long due, long startOfToday) {
        if (due <= 0) return 2; // Unconfirmed date: never invent one.
        return due < startOfToday ? 1 : 0; // Upcoming first, overdue second.
    }

    public static List<Entry> ordered(List<Entry> entries, long startOfToday) {
        List<Entry> result = new ArrayList<>(entries);
        result.sort((a, b) -> {
            int pa = priority(a.task.due, startOfToday);
            int pb = priority(b.task.due, startOfToday);
            int cmp = Integer.compare(pa, pb);
            if (cmp != 0) return cmp;
            // Future: soonest first. Overdue: most recently overdue first.
            if (pa == 0) cmp = Long.compare(a.task.due, b.task.due);
            if (pa == 1) cmp = Long.compare(b.task.due, a.task.due);
            if (cmp != 0) return cmp;
            cmp = a.course.compareToIgnoreCase(b.course);
            if (cmp != 0) return cmp;
            return Long.compare(a.task.id, b.task.id);
        });
        return result;
    }
}
