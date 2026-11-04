package pe.agendaclara.app;

import android.content.Intent;
import android.content.res.ColorStateList;
import android.view.Gravity;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Academic overview backed by existing tasks and the existing class-schedule activity.
 * No new storage, permissions, or remote APIs.
 */
public final class MiDiaStudyPage {
    private static final int INK = 0xff182746;
    private static final int PURPLE = 0xff7046cf;
    private static final int MUTED = 0xff60738f;
    private MiDiaStudyPage() {}

    public static void render(MainActivity a) {
        List<Task> all = Store.get(a).all();
        List<Task> studies = new ArrayList<>();
        int pending = 0, completed = 0;
        for (Task task : all) {
            if (!MiDiaDayMetrics.isStudy(task)) continue;
            studies.add(task);
            if (task.done) completed++;
            else pending++;
        }
        studies.sort(new Comparator<Task>() {
            @Override public int compare(Task x, Task y) {
                if (x.done != y.done) return x.done ? 1 : -1;
                long dx = x.due <= 0 ? Long.MAX_VALUE : x.due;
                long dy = y.due <= 0 ? Long.MAX_VALUE : y.due;
                return Long.compare(dx, dy);
            }
        });

        LinearLayout heading = a.row();
        heading.setGravity(Gravity.CENTER_VERTICAL);
        ImageView icon = new ImageView(a);
        icon.setImageDrawable(new UiDesign.OutlineIcon("graduation", PURPLE));
        icon.setContentDescription(null);
        LinearLayout.LayoutParams ip = new LinearLayout.LayoutParams(a.dp(37), a.dp(37));
        ip.rightMargin = a.dp(10);
        heading.addView(icon, ip);
        LinearLayout title = a.column();
        title.addView(a.text("Mi estudio", 23, INK, true));
        title.addView(a.text("Cursos, exámenes y actividades académicas", 12, MUTED, false));
        heading.addView(title, new LinearLayout.LayoutParams(0, -2, 1));
        a.body.addView(heading);
        a.gap(a.body, 18);

        LinearLayout summary = a.card(a.body);
        summary.setBackground(a.rounded(0xfff2edff, 20));
        summary.addView(a.text("Tu actividad académica", 18, INK, true));
        a.gap(summary, 9);
        summary.addView(a.text(pending + " pendientes  ·  " + completed + " completadas",
                15, PURPLE, true));
        summary.addView(a.text("Se muestran las tareas que puedes identificar como estudios, "
                + "cursos o exámenes por su categoría o título.", 12, MUTED, false));
        a.gap(summary, 12);
        Button schedule = a.button("Abrir mi horario de clases", () ->
                a.startActivity(new Intent(a, ScheduleActivity.class)));
        schedule.setContentDescription("Abrir el horario de clases existente");
        summary.addView(schedule);

        LinearLayout tools = a.row();
        Button newTask = a.button("＋  Nueva actividad", () -> a.openEditor(-1, null, null));
        tools.addView(newTask, new LinearLayout.LayoutParams(0, -2, 1));
        LinearLayout.LayoutParams spacer = new LinearLayout.LayoutParams(a.dp(8), 1);
        tools.addView(new android.view.View(a), spacer);
        Button allTasks = a.button("Todas las tareas", () -> MiDiaNavigation.open(a, 1));
        tools.addView(allTasks, new LinearLayout.LayoutParams(0, -2, 1));
        a.body.addView(tools);
        a.gap(a.body, 16);

        a.body.addView(a.text("Actividades de estudio", 18, INK, true));
        a.gap(a.body, 10);
        if (studies.isEmpty()) {
            LinearLayout empty = a.card(a.body);
            empty.addView(a.text("Todavía no hay actividades académicas identificadas.",
                    14, MUTED, false));
            empty.addView(a.text("Puedes crear una tarea y asignarle la categoría «Estudios» "
                    + "o la de alguno de tus cursos.", 12, MUTED, false));
            return;
        }
        int limit = Math.min(20, studies.size());
        for (int i = 0; i < limit; i++) a.taskCard(a.body, studies.get(i));
        if (studies.size() > limit) {
            LinearLayout more = a.card(a.body);
            more.addView(a.text("Hay " + (studies.size() - limit)
                    + " actividades adicionales. Usa Tareas para verlas todas.",
                    13, MUTED, false));
            more.addView(a.button("Abrir todas las tareas", () -> MiDiaNavigation.open(a, 1)));
        }
    }
}
