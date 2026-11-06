package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Verify upcoming assessments in other courses are not hidden by course group order. */
public final class AcademicWidgetEvaluationOrderTests {
    private static void check(boolean yes, String reason) {
        if (!yes) throw new AssertionError(reason);
    }
    private static AcademicWidgetEvaluationOrder.Entry e(long id, String course, long due) {
        Task task = new Task();
        task.id = id;
        task.due = due;
        task.title = "Examen " + id;
        return new AcademicWidgetEvaluationOrder.Entry(course, task);
    }
    public static void main(String[] args) {
        long today = 1_800_000_000_000L;
        List<AcademicWidgetEvaluationOrder.Entry> source = new ArrayList<>(Arrays.asList(
                e(10, "Historia", today + 20_000_000L),
                e(20, "Matemática", today + 3_600_000L),
                e(30, "Química", today - 3_600_000L),
                e(40, "Arte", 0L),
                e(50, "Biología", today + 7_200_000L)));
        List<AcademicWidgetEvaluationOrder.Entry> sorted =
                AcademicWidgetEvaluationOrder.ordered(source, today);
        long[] expected = {20,50,10,30,40};
        for (int i = 0; i < expected.length; i++)
            check(sorted.get(i).task.id == expected[i], "Wrong evaluation ordering at " + i);
        check(source.get(0).task.id == 10, "Sort unexpectedly mutated input list");
        List<AcademicWidgetEvaluationOrder.Entry> ties =
                AcademicWidgetEvaluationOrder.ordered(Arrays.asList(
                        e(2,"Biología",today+100),e(1,"Arte",today+100)),today);
        check(ties.get(0).task.id == 1,"Tie should have stable course ordering");
        System.out.println("PASS: upcoming evaluations sorted globally across all courses");
        System.out.println("PASS: overdue and unknown-date assessments retained in priority order");
        System.out.println("PASS: no mutation of data stored by Agenda Clara");
    }
}
