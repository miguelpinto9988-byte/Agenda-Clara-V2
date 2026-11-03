package pe.agendaclara.app;

import android.content.res.ColorStateList;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Home-only view. Every statistic comes from existing app stores/providers. */
public final class MiDiaDashboard {
    private static final int INK = 0xff182746;
    private static final int MUTED = 0xff55647c;
    private static final Locale ES = new Locale("es", "PE");
    private MiDiaDashboard() {}

    private static TextView label(MainActivity activity, String value, int size, int color, boolean bold) {
        TextView view = activity.text(value, size, color, bold);
        view.setGravity(android.view.Gravity.CENTER_VERTICAL);
        return view;
    }

    private static LinearLayout stat(MainActivity activity, String emoji, String value,
                                     String title, String detail, int tint, String image) {
        LinearLayout tile = activity.column();
        tile.setPadding(activity.dp(14), activity.dp(13), activity.dp(12), activity.dp(13));
        tile.setBackground(activity.rounded(tint, 18));
        LinearLayout headline = activity.row();
        int imageId = activity.getResources().getIdentifier(image, "drawable", activity.getPackageName());
        if (imageId != 0) {
            ImageView icon = new ImageView(activity);
            icon.setImageResource(imageId);
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            icon.setContentDescription(title);
            LinearLayout.LayoutParams iconSize = new LinearLayout.LayoutParams(activity.dp(40), activity.dp(40));
            iconSize.rightMargin = activity.dp(5);
            headline.addView(icon, iconSize);
        }
        headline.addView(label(activity, (imageId == 0 ? emoji + "  " : "") + value, 24, INK, true));
        tile.addView(headline);
        activity.gap(tile, 7);
        tile.addView(label(activity, title, 14, INK, true));
        tile.addView(label(activity, detail, 11, MUTED, false));
        return tile;
    }

    private static void addStatRow(MainActivity activity, LinearLayout container,
                                   LinearLayout first, LinearLayout second) {
        LinearLayout row = activity.row();
        LinearLayout.LayoutParams halfA = new LinearLayout.LayoutParams(0, -2, 1);
        halfA.rightMargin = activity.dp(6);
        LinearLayout.LayoutParams halfB = new LinearLayout.LayoutParams(0, -2, 1);
        halfB.leftMargin = activity.dp(6);
        row.addView(first, halfA);
        row.addView(second, halfB);
        container.addView(row);
    }

    private static boolean study(Task task) {
        String name = TaskOrganization.category(task.category).toLowerCase(Locale.ROOT);
        return name.contains("estud") || name.contains("acad") || name.contains("examen")
                || name.contains("clase") || name.contains("curso");
    }

    public static void render(MainActivity activity) {
        final LinearLayout content = activity.body;
        content.addView(new MiDiaHeaderView(activity));
        activity.gap(content, 15);
        long now = System.currentTimeMillis();
        LocalDate day = LocalDate.now();
        ZoneId zone = ZoneId.systemDefault();
        long dayStart = day.atStartOfDay(zone).toInstant().toEpochMilli();
        long dayEnd = day.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli();
        List<Task> all = Store.get(activity).all();
        TaskSummary.Result summary = TaskSummary.calculate(all, now,
                Store.get(activity).completedSince(now - 7L * 86400000L));
        List<Task> dayTasks = new ArrayList<>();
        int studyPending = 0;
        for (Task task : all) {
            if (task.done) continue;
            if (study(task)) studyPending++;
            if (task.due > 0 && task.due < dayEnd) dayTasks.add(task);
        }
        dayTasks.sort((left, right) -> Long.compare(left.due, right.due));

        boolean calendarAllowed = CalendarBridge.allowed(activity);
        List<CalendarBridge.Event> events = new ArrayList<>();
        if (calendarAllowed) {
            try { events = CalendarBridge.selectedEvents(activity); }
            catch (SecurityException | IllegalArgumentException ignored) { calendarAllowed = false; }
        }
        int eventsToday = 0;
        CalendarBridge.Event next = null;
        for (CalendarBridge.Event event : events) {
            if (event.start < dayEnd && event.end > dayStart) eventsToday++;
            if (next == null && event.end > now) next = event;
        }

        content.addView(label(activity, "Tu día en números", 18, INK, true));
        activity.gap(content, 11);
        addStatRow(activity, content,
                stat(activity, "✓", String.valueOf(dayTasks.size()), "Tareas", "Para hoy y atrasadas", 0xffedf5ff, "ic_midia_tareas"),
                stat(activity, "◷", calendarAllowed ? String.valueOf(eventsToday) : "—", "Eventos",
                        calendarAllowed ? "Hoy en tus calendarios" : "Conecta calendario", 0xfff2edff, "ic_midia_eventos"));
        activity.gap(content, 11);
        addStatRow(activity, content,
                stat(activity, "✎", String.valueOf(studyPending), "Estudio", "Actividades pendientes", 0xfffff5e5, "ic_midia_estudio"),
                stat(activity, "◉", summary.percentage + "%", "Progreso", "Avance de 7 días", 0xffeaf8f0, "ic_midia_logros"));
        activity.gap(content, 23);

        LinearLayout heading = activity.row();
        heading.addView(label(activity, "Mi día", 20, INK, true), new LinearLayout.LayoutParams(0, -2, 1));
        heading.addView(activity.button("＋ Nueva", () -> activity.showCreationMenu()));
        content.addView(heading);
        activity.gap(content, 8);
        if (dayTasks.isEmpty()) {
            LinearLayout empty = activity.card(content);
            empty.addView(label(activity, "No tienes tareas pendientes para hoy.", 14, MUTED, false));
            empty.addView(activity.button("Crear tarea", () -> activity.openEditor(-1, null, null)));
        } else {
            int limit = Math.min(5, dayTasks.size());
            for (int i = 0; i < limit; i++) activity.taskCard(content, dayTasks.get(i));
            if (dayTasks.size() > limit) {
                content.addView(activity.button("Abrir lista completa de tareas (" + dayTasks.size() + " para hoy)", () -> {
                    activity.dashboardAllTasksExpanded = true;
                    activity.render();
                }));
            }
        }

        content.addView(label(activity, "Próximo evento", 20, INK, true));
        activity.gap(content, 9);
        LinearLayout eventCard = activity.card(content);
        if (!calendarAllowed) {
            eventCard.addView(label(activity, "Conecta tu calendario para consultar tus eventos.", 14, MUTED, false));
            eventCard.addView(activity.button("Conectar calendario", () -> {
                activity.page = 3;
                activity.connectionTab = 1;
                activity.render();
            }));
        } else if (next == null) {
            eventCard.addView(label(activity, "No hay próximos eventos en los calendarios seleccionados.", 14, MUTED, false));
            eventCard.addView(activity.button("Abrir calendario", () -> {
                activity.page = 1; activity.render();
            }));
        } else {
            CalendarBridge.Event first = next;
            eventCard.addView(label(activity, first.title, 16, INK, true));
            String when = Instant.ofEpochMilli(first.start).atZone(zone)
                    .format(DateTimeFormatter.ofPattern("EEE d MMM · HH:mm", ES));
            activity.gap(eventCard, 5);
            eventCard.addView(label(activity, (first.allDay ? "Todo el día" : when)
                    + (first.calendarName == null || first.calendarName.isEmpty() ? "" : " · " + first.calendarName),
                    12, MUTED, false));
            eventCard.addView(activity.button("Ver calendario", () -> {
                activity.page = 1; activity.render();
            }));
        }

        LinearLayout progressCard = activity.card(content);
        progressCard.addView(label(activity, "Tu progreso semanal", 18, INK, true));
        activity.gap(progressCard, 7);
        progressCard.addView(label(activity,
                summary.completed7days + " completadas en 7 días · " + summary.pending + " pendientes", 12, MUTED, false));
        activity.gap(progressCard, 11);
        ProgressBar progress = new ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        progress.setProgress(summary.percentage);
        progress.setProgressTintList(ColorStateList.valueOf(0xff6554d8));
        progress.setProgressBackgroundTintList(ColorStateList.valueOf(0xffe5e9f2));
        progressCard.addView(progress, new LinearLayout.LayoutParams(-1, activity.dp(8)));
        activity.gap(progressCard, 7);
        progressCard.addView(label(activity, summary.percentage + "% · completadas en 7 días respecto de pendientes actuales", 11, MUTED, false));

        content.addView(activity.button(activity.dashboardAllTasksExpanded
                ? "Ocultar lista completa de tareas" : "Todas mis tareas y categorías", () -> {
            activity.dashboardAllTasksExpanded = !activity.dashboardAllTasksExpanded;
            activity.render();
        }));
        if (activity.dashboardAllTasksExpanded) {
            activity.gap(content, 12);
            activity.tasksPage();
        }
    }
}
