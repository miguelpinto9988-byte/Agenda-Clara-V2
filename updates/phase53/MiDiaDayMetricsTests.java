package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Pure Java tests for phase 6; run only after the final design is approved. */
public final class MiDiaDayMetricsTests {
    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }

    private static Task task(boolean done, long due, long completedAt, String category, String title) {
        Task t = new Task();
        t.done = done;
        t.due = due;
        t.completedAt = completedAt;
        t.category = category;
        t.title = title;
        return t;
    }

    public static void main(String[] args) {
        long midnight = 1_800_000_000_000L;
        long next = midnight + 86_400_000L;

        MiDiaDayMetrics.Result empty = MiDiaDayMetrics.calculate(
                new ArrayList<>(), midnight, next);
        check(empty.totalToday == 0 && empty.progressPercent == 0,
                "Empty day cannot be 100%");
        check(empty.visibleTasks.isEmpty(), "Empty day must not create tasks");

        Task pending = task(false, midnight + 3600_000, 0, "General", "Comprar víveres");
        Task overdue = task(false, midnight - 3600_000, 0, "Estudios", "Repasar álgebra");
        Task completed = task(true, next + 60000, midnight + 1800_000,
                "Estudios", "Ejercicio de clase");
        Task oldDone = task(true, midnight + 3600_000, midnight - 1000,
                "Personal", "Terminado ayer");
        Task future = task(false, next + 60_000, 0, "General", "Entrega futura");

        List<Task> tasks = Arrays.asList(pending, overdue, completed, oldDone, future);
        MiDiaDayMetrics.Result summary = MiDiaDayMetrics.calculate(tasks, midnight, next);
        check(summary.pendingToday == 2, "Due and overdue count as today");
        check(summary.doneToday == 1, "Count completion time rather than due time");
        check(summary.totalToday == 3 && summary.progressPercent == 33,
                "Daily progress should be 1 out of 3");
        check(summary.studyPending == 1, "Study count must not include done tasks");
        check(summary.visibleTasks.size() == 3 && !summary.visibleTasks.get(0).done,
                "Unfinished work must precede completed items");
        check(!MiDiaDayMetrics.isStudy(task(false, next, 0,
                "General", "Llamar a casa")), "Do not mark generic tasks as academic");
        check(MiDiaDayMetrics.isStudy(task(false, next, 0,
                "Matemáticas", "Examen parcial")), "Recognize academic exam titles");

        System.out.println("PASS daily metrics: empty, overdue, completed today, study, sorting");
    }
}
