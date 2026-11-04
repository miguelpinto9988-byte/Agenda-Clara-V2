package pe.agendaclara.app;

import android.content.res.ColorStateList;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.CheckBox;
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

/** Phase 6: the reference-inspired, fully native, data-backed Mi día home. */
public final class MiDiaDashboard {
    private static final int INK = 0xff142344;
    private static final int MUTED = 0xff61708a;
    private static final int BLUE = 0xff118de0;
    private static final int PURPLE = 0xff7844df;
    private static final int GREEN = 0xff12bd52;
    private static final Locale ES = new Locale("es", "PE");
    private MiDiaDashboard() {}

    private static GradientDrawable rounded(MainActivity a, int color, int radius) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(a.dp(radius));
        return drawable;
    }

    private static TextView text(MainActivity a, String value, int size, int color, boolean bold) {
        TextView view = a.text(value, size, color, bold);
        view.setGravity(Gravity.CENTER_VERTICAL);
        return view;
    }

    private static TextView heading(MainActivity a, String title) {
        TextView view = text(a, title, 18, INK, true);
        view.setContentDescription(title);
        return view;
    }

    private static ImageView image(MainActivity a, String name, int size, int fallbackIconColor) {
        ImageView icon = new ImageView(a);
        int id = a.getResources().getIdentifier(name, "drawable", a.getPackageName());
        if (id != 0) icon.setImageResource(id);
        else icon.setImageDrawable(new UiDesign.OutlineIcon("check", fallbackIconColor));
        icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
        icon.setLayoutParams(new LinearLayout.LayoutParams(a.dp(size), a.dp(size)));
        return icon;
    }

    private static LinearLayout stat(MainActivity a, String resource, String value, String label,
                                     int background, int accent, Runnable callback) {
        LinearLayout tile = a.column();
        tile.setGravity(Gravity.CENTER);
        tile.setPadding(a.dp(3), a.dp(9), a.dp(3), a.dp(9));
        tile.setBackground(rounded(a, background, 15));
        tile.setMinimumHeight(a.dp(105));
        ImageView icon = image(a, resource, 32, accent);
        icon.setContentDescription(null);
        tile.addView(icon);
        TextView number = text(a, value, 20, INK, true);
        number.setGravity(Gravity.CENTER);
        number.setSingleLine(true);
        tile.addView(number);
        TextView caption = text(a, label, 11, INK, false);
        caption.setGravity(Gravity.CENTER);
        caption.setSingleLine(true);
        tile.addView(caption);
        tile.setContentDescription(label + ": " + value);
        tile.setFocusable(true);
        tile.setOnClickListener(v -> callback.run());
        return tile;
    }

    private static void addStats(MainActivity a, LinearLayout parent,
                                 MiDiaDayMetrics.Result metrics, int eventsToday,
                                 boolean calendarAllowed) {
        LinearLayout row = a.row();
        row.setGravity(Gravity.CENTER_VERTICAL);
        String[] values = {
                String.valueOf(metrics.pendingToday),
                calendarAllowed ? String.valueOf(eventsToday) : "—",
                String.valueOf(metrics.studyPending),
                metrics.totalToday == 0 ? "—" : metrics.progressPercent + "%"
        };
        String[] labels = {"Tareas", "Eventos", "Estudio", "Progreso"};
        String[] icons = {"ic_midia_tareas", "ic_midia_eventos", "ic_midia_estudio", "ic_midia_logros"};
        int[] colors = {0xffedf7ff, 0xfffff0ef, 0xfff1edff, 0xfffff0f4};
        int[] accents = {BLUE, 0xffec5e50, PURPLE, 0xffe62365};
        Runnable[] actions = {
                () -> MiDiaNavigation.open(a, 1),
                () -> MiDiaNavigation.open(a, 3),
                () -> MiDiaNavigation.open(a, 2),
                () -> {
                    View progress = parent.findViewWithTag("mi_dia_progress_section");
                    if (progress != null) a.contentScroll.smoothScrollTo(0, progress.getTop());
                }
        };
        int widthDp = a.getResources().getConfiguration().screenWidthDp;
        float fontScale = a.getResources().getConfiguration().fontScale;
        boolean twoRows = widthDp < 360 || fontScale > 1.28f;
        for (int i = 0; i < labels.length; i++) {
            if (twoRows && i == 2) {
                parent.addView(row);
                a.gap(parent, 6);
                row = a.row();
                row.setGravity(Gravity.CENTER_VERTICAL);
            }
            LinearLayout card = stat(a, icons[i], values[i], labels[i],
                    colors[i], accents[i], actions[i]);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -2, 1);
            if ((twoRows && i % 2 == 1) || (!twoRows && i > 0))
                lp.leftMargin = a.dp(6);
            row.addView(card, lp);
        }
        parent.addView(row);
    }

    private static void sectionHeader(MainActivity a, LinearLayout parent, String title,
                                      String link, Runnable action) {
        LinearLayout row = a.row();
        row.addView(heading(a, title), new LinearLayout.LayoutParams(0, -2, 1));
        if (link != null) {
            TextView button = text(a, link + " ›", 13, 0xff1368c9, true);
            button.setPadding(a.dp(10), a.dp(8), a.dp(2), a.dp(8));
            button.setContentDescription(link + ": " + title);
            button.setFocusable(true);
            button.setOnClickListener(v -> action.run());
            row.addView(button);
        }
        parent.addView(row);
    }

    private static void taskRow(MainActivity a, LinearLayout parent, Task task, ZoneId zone) {
        LinearLayout row = a.row();
        row.setTag("task:" + task.id);
        row.setMinimumHeight(a.dp(47));
        CheckBox box = new CheckBox(a);
        box.setChecked(task.done);
        box.setButtonTintList(ColorStateList.valueOf(task.done ? GREEN : 0xff8896ab));
        box.setContentDescription((task.done ? "Marcar pendiente: " : "Marcar completada: ") + task.title);
        LinearLayout.LayoutParams checkSize = new LinearLayout.LayoutParams(a.dp(42), a.dp(44));
        row.addView(box, checkSize);
        TextView title = text(a, task.title, 13, task.done ? MUTED : INK, !task.done);
        title.setMaxLines(2);
        title.setEllipsize(android.text.TextUtils.TruncateAt.END);
        if (task.done) title.setPaintFlags(title.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
        title.setOnClickListener(v -> a.showTaskDetails(task.id));
        row.addView(title, new LinearLayout.LayoutParams(0, -2, 1));
        String when = task.due > 0
                ? Instant.ofEpochMilli(task.due).atZone(zone).format(
                        DateTimeFormatter.ofPattern("HH:mm", ES))
                : "Hecha";
        TextView time = text(a, when, 12, MUTED, false);
        time.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams timeSize = new LinearLayout.LayoutParams(a.dp(55), a.dp(40));
        timeSize.leftMargin = a.dp(6);
        row.addView(time, timeSize);
        parent.addView(row);
        box.setOnCheckedChangeListener((buttonView, checked) -> {
            Task saved = Store.get(a).find(task.id);
            if (saved == null || saved.done == checked) return;
            saved.done = checked;
            Store.get(a).save(saved);
            if (checked) Reminders.cancel(a, saved.id);
            else Reminders.schedule(a, saved);
            TaskWidget.refresh(a);
            a.forceRefresh = true;
            a.render();
        });
    }

    private static void addTaskList(MainActivity a, LinearLayout parent,
                                    MiDiaDayMetrics.Result metrics, ZoneId zone) {
        sectionHeader(a, parent, "☷  Mi día", "Ver todo", () -> MiDiaNavigation.open(a, 1));
        a.gap(parent, 4);
        if (metrics.visibleTasks.isEmpty()) {
            LinearLayout empty = a.column();
            empty.setPadding(a.dp(12), a.dp(14), a.dp(12), a.dp(14));
            empty.setBackground(rounded(a, 0xfff5f9ff, 14));
            empty.addView(text(a, "Tu día está libre de tareas pendientes.", 13, MUTED, false));
            TextView add = text(a, "＋  Crear una tarea", 13, BLUE, true);
            add.setPadding(0, a.dp(8), 0, a.dp(3));
            add.setOnClickListener(v -> a.openEditor(-1, null, null));
            empty.addView(add);
            parent.addView(empty);
            return;
        }
        int count = Math.min(3, metrics.visibleTasks.size());
        for (int i = 0; i < count; i++) {
            taskRow(a, parent, metrics.visibleTasks.get(i), zone);
            if (i < count - 1) {
                View divider = new View(a);
                divider.setBackgroundColor(0xffedf0f5);
                parent.addView(divider, new LinearLayout.LayoutParams(-1, a.dp(1)));
            }
        }
        if (metrics.visibleTasks.size() > count) {
            TextView more = text(a, "Ver " + (metrics.visibleTasks.size() - count)
                    + " actividad(es) más", 12, BLUE, true);
            more.setGravity(Gravity.RIGHT);
            more.setPadding(a.dp(3), a.dp(7), a.dp(3), a.dp(5));
            more.setOnClickListener(v -> MiDiaNavigation.open(a, 1));
            parent.addView(more);
        }
    }

    private static void addNextEvent(MainActivity a, LinearLayout parent,
                                     CalendarBridge.Event event, boolean allowed, ZoneId zone) {
        LinearLayout card = a.row();
        card.setPadding(a.dp(13), a.dp(12), a.dp(13), a.dp(12));
        card.setBackground(rounded(a, 0xfff2eaff, 18));
        card.setMinimumHeight(a.dp(84));
        card.setContentDescription(event == null ? "Próximo evento" : "Próximo evento: " + event.title);
        ImageView calendar = image(a, "ic_midia_eventos", 39, PURPLE);
        calendar.setContentDescription(null);
        LinearLayout.LayoutParams iconSize = new LinearLayout.LayoutParams(a.dp(42), a.dp(42));
        iconSize.rightMargin = a.dp(9);
        card.addView(calendar, iconSize);
        LinearLayout details = a.column();
        details.addView(text(a, "Próximo evento", 11, PURPLE, true));
        String title = !allowed ? "Conectar calendario" : event == null
                ? "No hay eventos próximos" : event.title;
        TextView name = text(a, title, 14, INK, true);
        name.setMaxLines(2);
        details.addView(name);
        if (event != null) {
            String time = event.allDay ? "Todo el día" : Instant.ofEpochMilli(event.start)
                    .atZone(zone).format(DateTimeFormatter.ofPattern("d MMM · HH:mm", ES));
            details.addView(text(a, time, 12, MUTED, false));
        }
        card.addView(details, new LinearLayout.LayoutParams(0, -2, 1));
        TextView arrow = text(a, "›", 29, PURPLE, true);
        card.addView(arrow);
        card.setFocusable(true);
        card.setOnClickListener(v -> {
            if (!allowed) {
                a.page = 3;
                a.connectionTab = 1;
                a.render();
            } else MiDiaNavigation.open(a, 3);
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.topMargin = a.dp(14);
        parent.addView(card, lp);
    }

    private static void addProgress(MainActivity a, LinearLayout parent,
                                    MiDiaDayMetrics.Result metrics) {
        LinearLayout panel = a.column();
        panel.setTag("mi_dia_progress_section");
        panel.setPadding(a.dp(12), a.dp(10), a.dp(12), a.dp(12));
        panel.setBackground(rounded(a, 0xfff7fafc, 15));
        LinearLayout headingRow = a.row();
        TextView title = text(a, "◎  Progreso del día", 14, INK, true);
        headingRow.addView(title, new LinearLayout.LayoutParams(0, -2, 1));
        String count = metrics.totalToday == 0 ? "Sin actividades"
                : metrics.doneToday + " de " + metrics.totalToday + " actividades";
        headingRow.addView(text(a, count, 11, MUTED, false));
        panel.addView(headingRow);
        a.gap(panel, 9);
        ProgressBar bar = new ProgressBar(a, null, android.R.attr.progressBarStyleHorizontal);
        bar.setMax(100);
        bar.setProgress(metrics.progressPercent);
        bar.setProgressTintList(ColorStateList.valueOf(GREEN));
        bar.setProgressBackgroundTintList(ColorStateList.valueOf(0xffe2e8ef));
        bar.setContentDescription("Progreso del día: " + metrics.progressPercent + " por ciento");
        panel.addView(bar, new LinearLayout.LayoutParams(-1, a.dp(9)));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.topMargin = a.dp(12);
        parent.addView(panel, lp);
    }

    private static void addQuote(MainActivity a, LinearLayout parent, LocalDate date) {
        LinearLayout card = a.row();
        card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(a.dp(12), a.dp(10), a.dp(12), a.dp(10));
        card.setBackground(rounded(a, 0xfffff5df, 14));
        TextView star = text(a, "★", 23, 0xfff59e0b, true);
        LinearLayout.LayoutParams starSize = new LinearLayout.LayoutParams(-2, -2);
        starSize.rightMargin = a.dp(9);
        card.addView(star, starSize);
        String phrase = MiDiaDailyRotation.quote(a, date);
        TextView quote = text(a, "“" + phrase + "”", 12, 0xff5a4a27, false);
        quote.setMaxLines(3);
        card.addView(quote, new LinearLayout.LayoutParams(0, -2, 1));
        card.setContentDescription("Frase motivadora: " + phrase);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.topMargin = a.dp(11);
        parent.addView(card, lp);
    }

    public static void render(MainActivity activity) {
        LinearLayout body = activity.body;
        body.addView(new MiDiaHeaderView(activity));
        activity.gap(body, 11);

        LocalDate today = LocalDate.now();
        ZoneId zone = ZoneId.systemDefault();
        long dayStart = today.atStartOfDay(zone).toInstant().toEpochMilli();
        long dayEnd = today.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli();
        List<Task> tasks = Store.get(activity).all();
        MiDiaDayMetrics.Result metrics = MiDiaDayMetrics.calculate(tasks, dayStart, dayEnd);

        boolean hasCalendarPermission = CalendarBridge.allowed(activity)
                && !Prefs.calendars(activity).isEmpty();
        List<CalendarBridge.Event> events = new ArrayList<>();
        if (hasCalendarPermission) {
            try {
                events = CalendarBridge.selectedEvents(activity);
            } catch (SecurityException | IllegalArgumentException ignored) {
                hasCalendarPermission = false;
            }
        }
        int eventsToday = 0;
        CalendarBridge.Event next = null;
        long now = System.currentTimeMillis();
        for (CalendarBridge.Event e : events) {
            if (e.start < dayEnd && e.end > dayStart) eventsToday++;
            if (next == null && e.end > now) next = e;
        }
        addStats(activity, body, metrics, eventsToday, hasCalendarPermission);
        activity.gap(body, 16);
        addTaskList(activity, body, metrics, zone);
        addNextEvent(activity, body, next, hasCalendarPermission, zone);
        addProgress(activity, body, metrics);
        addQuote(activity, body, today);
        activity.gap(body, 8);
    }
}
