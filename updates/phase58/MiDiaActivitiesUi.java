package pe.agendaclara.app;

import android.content.res.ColorStateList;
import android.graphics.Paint;
import android.view.Gravity;
import android.view.View;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Phase 11: the next course's linked tasks and distinct day/pending lists. */
public final class MiDiaActivitiesUi {
    private static final int INK = 0xff182746;
    private static final int MUTED = 0xff63728c;
    private static final int BLUE = 0xff1675d1;
    private static final int GREEN = 0xff10b95a;
    private MiDiaActivitiesUi() {}

    private static TextView text(MainActivity a, String text, int size, int color, boolean bold) {
        TextView v = a.text(text, size, color, bold);
        v.setGravity(Gravity.CENTER_VERTICAL);
        return v;
    }

    private static LinearLayout section(MainActivity a, LinearLayout parent, String title,
                                        int background) {
        LinearLayout block = a.column();
        block.setPadding(a.dp(12), a.dp(12), a.dp(12), a.dp(12));
        block.setBackground(a.rounded(background, 17));
        TextView header = text(a, title, 16, INK, true);
        block.addView(header);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.topMargin = a.dp(10);
        parent.addView(block, lp);
        return block;
    }

    private static void openTasks(MainActivity a) {
        MiDiaNavigation.open(a, 1);
    }

    private static void row(MainActivity a, LinearLayout parent, Task task,
                            boolean allowUnlink) {
        LinearLayout line = a.row();
        line.setGravity(Gravity.CENTER_VERTICAL);
        line.setPadding(a.dp(1), a.dp(5), a.dp(1), a.dp(5));
        CheckBox done = new CheckBox(a);
        done.setChecked(task.done);
        done.setButtonTintList(ColorStateList.valueOf(
                task.done ? GREEN : 0xff8998b0));
        done.setContentDescription((task.done ? "Marcar pendiente: " :
                "Completar actividad: ") + task.title);
        line.addView(done, new LinearLayout.LayoutParams(a.dp(42), a.dp(44)));
        LinearLayout description = a.column();
        TextView name = text(a, task.title, 13, task.done ? MUTED : INK, !task.done);
        name.setMaxLines(2);
        if (task.done) name.setPaintFlags(name.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
        description.addView(name);
        String due = task.done ? "Completada" : task.due == 0
                ? "Sin fecha" : TaskLogic.when(task.due);
        TextView time = text(a, due, 11, MUTED, false);
        time.setMaxLines(2);
        description.addView(time);
        description.setOnClickListener(v -> a.showTaskDetails(task.id));
        line.addView(description, new LinearLayout.LayoutParams(0, -2, 1));
        if (allowUnlink) {
            TextView unlink = text(a, "×", 22, MUTED, false);
            unlink.setGravity(Gravity.CENTER);
            unlink.setContentDescription("Desvincular actividad del curso: " + task.title);
            unlink.setFocusable(true);
            unlink.setPadding(a.dp(10), a.dp(4), a.dp(8), a.dp(4));
            unlink.setOnClickListener(v -> a.dialogBuilder()
                    .setTitle("Desvincular actividad")
                    .setMessage("La tarea seguirá existiendo en Tareas. Solo se quitará su vínculo con el curso.")
                    .setPositiveButton("Desvincular", (d, which) -> {
                        MiDiaCourseLinks.unlink(a, task.id);
                        a.forceRefresh = true; a.render();
                    })
                    .setNegativeButton("Cancelar", null).show());
            line.addView(unlink);
        }
        parent.addView(line);
        done.setOnCheckedChangeListener((button, checked) -> {
            Task fresh = Store.get(a).find(task.id);
            if (fresh == null || fresh.done == checked) return;
            fresh.done = checked;
            Store.get(a).save(fresh);
            if (checked) Reminders.cancel(a, fresh.id);
            else Reminders.schedule(a, fresh);
            TaskWidget.refresh(a);
            a.forceRefresh = true;
            a.render();
        });
    }

    private static void chooseCourseTask(MainActivity a, String course) {
        List<Task> candidates = new ArrayList<>();
        for (Task t : Store.get(a).all()) {
            if (!t.done && t.id > 0
                    && !ScheduleCourseColors.identity(course)
                       .equals(MiDiaCourseLinks.linkedCourse(a, t.id))) {
                candidates.add(t);
                if (candidates.size() == 60) break;
            }
        }
        if (candidates.isEmpty()) {
            a.dialogBuilder().setTitle("Vincular actividad")
                    .setMessage("No hay tareas pendientes para vincular. Crea una en Tareas y después selecciónala desde aquí.")
                    .setPositiveButton("Ir a Tareas", (d, w) -> openTasks(a))
                    .setNegativeButton("Cerrar", null).show();
            return;
        }
        String[] options = new String[candidates.size()];
        for (int i = 0; i < candidates.size(); i++) {
            Task t = candidates.get(i);
            options[i] = t.title + "  ·  " + TaskOrganization.category(t.category);
        }
        a.dialogBuilder().setTitle("Vincular tarea a " + course)
                .setItems(options, (d, position) -> {
                    Task choice = candidates.get(position);
                    if (MiDiaCourseLinks.assign(a, choice.id, course)) {
                        a.forceRefresh = true; a.render();
                    } else {
                        a.toast("No se pudo vincular. Comprueba el curso y la tarea.");
                    }
                })
                .setNegativeButton("Cancelar", null).show();
    }

    public static void addCourse(MainActivity a, LinearLayout parent,
                                 MiDiaNextClass.Result next, List<Task> all) {
        LinearLayout section = section(a, parent, "Actividad del curso", 0xfff0fbf4);
        if (next == null) {
            section.addView(text(a, "Cuando registres tus clases, podrás vincular tareas a cada curso.",
                    12, MUTED, false));
            return;
        }
        String course = next.entry.course;
        List<Task> linked = MiDiaCourseLinks.forCourse(a, course, all);
        section.addView(text(a, course, 12, 0xff27874f, true));
        a.gap(section, 6);
        if (linked.isEmpty()) {
            section.addView(text(a,
                    "Aún no has vinculado actividades a este curso.", 12, MUTED, false));
        } else {
            int shown = Math.min(3, linked.size());
            for (int i = 0; i < shown; i++) row(a, section, linked.get(i), true);
            if (linked.size() > shown) {
                section.addView(text(a, "+" + (linked.size() - shown) +
                        " actividades más; consulta Tareas para revisarlas.", 11, MUTED, false));
            }
        }
        a.gap(section, 5);
        section.addView(a.button("＋ Vincular tarea al curso", () ->
                chooseCourseTask(a, course)));
    }

    public static void addToday(MainActivity a, LinearLayout parent, List<Task> all,
                                long start, long end) {
        LinearLayout section = section(a, parent, "Actividades del día", 0xfff4f8ff);
        List<Task> today = new ArrayList<>();
        for (Task task : all) {
            if ((task.due >= start && task.due < end) ||
                    (task.done && task.completedAt >= start && task.completedAt < end)) {
                today.add(task);
            }
        }
        int due = 0, completed = 0;
        for (Task task : today) {
            if (task.done) completed++;
            else due++;
        }
        section.addView(text(a, completed + " completadas · " + due +
                " pendientes para hoy", 12, MUTED, false));
        a.gap(section, 5);
        if (today.isEmpty()) {
            section.addView(text(a, "No hay actividades programadas para hoy.", 12, MUTED, false));
        } else {
            for (int i = 0; i < Math.min(4, today.size()); i++) row(a, section, today.get(i), false);
            if (today.size() > 4) {
                section.addView(a.button("Ver todas las actividades del día", () -> openTasks(a)));
            }
        }
    }

    public static void addPending(MainActivity a, LinearLayout parent,
                                  List<Task> all, long start, long end) {
        LinearLayout section = section(a, parent, "Actividades pendientes", 0xfffff5f0);
        List<Task> pending = new ArrayList<>();
        int overdue = 0;
        for (Task t : all) {
            if (t.done) continue;
            pending.add(t);
            if (t.due > 0 && t.due < start) overdue++;
        }
        section.addView(text(a, pending.size() + " tareas por realizar" +
                (overdue == 0 ? "" : " · " + overdue + " atrasadas"),
                12, MUTED, false));
        a.gap(section, 5);
        if (pending.isEmpty()) {
            section.addView(text(a, "No tienes actividades pendientes.", 12, MUTED, false));
        } else {
            for (int i = 0; i < Math.min(4, pending.size()); i++) row(a, section, pending.get(i), false);
            if (pending.size() > 4) {
                section.addView(a.button("Ver todas las pendientes", () -> openTasks(a)));
            }
        }
    }
}
