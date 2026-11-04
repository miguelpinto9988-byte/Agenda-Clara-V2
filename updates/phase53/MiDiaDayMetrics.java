package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/** Pure, deterministic day aggregation. No Android dependencies or database writes. */
public final class MiDiaDayMetrics {
    private MiDiaDayMetrics() {}

    public static final class Result {
        public final int pendingToday;
        public final int doneToday;
        public final int studyPending;
        public final int totalToday;
        public final int progressPercent;
        public final List<Task> visibleTasks;

        Result(int pending, int done, int study, List<Task> tasks) {
            pendingToday = pending;
            doneToday = done;
            studyPending = study;
            totalToday = pending + done;
            progressPercent = totalToday == 0 ? 0 :
                    (int) Math.round(100d * done / totalToday);
            visibleTasks = tasks;
        }
    }

    private static String normalize(String source) {
        if (source == null) return "";
        return Normalizer.normalize(source.trim().toLowerCase(Locale.ROOT),
                Normalizer.Form.NFD).replaceAll("\\p{M}+", "");
    }

    /** Recognize academic tasks without changing existing categories or task records. */
    public static boolean isStudy(Task task) {
        String category = normalize(task.category);
        if (category.contains("estudi") || category.contains("academ")
                || category.contains("univers") || category.contains("coleg")
                || category.contains("institut") || category.contains("curso")
                || category.contains("examen") || category.contains("clase")
                || category.contains("asignatura")
                || category.contains("matematic") || category.contains("fisica")
                || category.contains("quimica") || category.contains("biologia")
                || category.contains("historia") || category.contains("ciencia")
                || category.contains("idioma") || category.contains("ingles")
                || category.contains("tesis") || category.contains("seminario")
                || category.contains("investigacion")) return true;
        String title = normalize(task.title);
        return title.startsWith("examen ") || title.startsWith("estudiar ")
                || title.startsWith("clase ") || title.startsWith("curso ")
                || title.startsWith("repasar ") || title.startsWith("evaluacion ")
                || title.startsWith("tarea de ");
    }

    /**
     * Today = unfinished due before the end of today (including overdue)
     * plus tasks completed since today's local midnight, regardless of due date.
     * Counts do not conflate a rolling 7-day summary with daily progress.
     */
    public static Result calculate(List<Task> tasks, long dayStart, long dayEnd) {
        if (dayStart >= dayEnd) throw new IllegalArgumentException("Invalid local day");
        int pending = 0, done = 0, study = 0;
        List<Task> visible = new ArrayList<>();
        for (Task task : tasks) {
            if (!task.done && isStudy(task)) study++;
            if (task.done) {
                if (task.completedAt >= dayStart && task.completedAt < dayEnd) {
                    done++;
                    visible.add(task);
                }
            } else if (task.due > 0 && task.due < dayEnd) {
                pending++;
                visible.add(task);
            }
        }
        visible.sort(new Comparator<Task>() {
            @Override public int compare(Task a, Task b) {
                if (a.done != b.done) return a.done ? 1 : -1;
                long aOrder = a.done ? a.completedAt : a.due;
                long bOrder = b.done ? b.completedAt : b.due;
                return Long.compare(aOrder, bOrder);
            }
        });
        return new Result(pending, done, study, visible);
    }
}
