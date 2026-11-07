package pe.agendaclara.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.RemoteViews;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** PNG-first Mi horario: follows the approved, user-corrected Canva layout. */
public final class AcademicWeekWidget extends AppWidgetProvider {
    private static final String ACTION_PREV = "pe.agendaclara.app.WEEK_PREVIOUS";
    private static final String ACTION_NEXT = "pe.agendaclara.app.WEEK_NEXT";
    private static final String PREFS = "academic_week_selected_day";
    private static final DateTimeFormatter DATE =
            DateTimeFormatter.ofPattern("'Hoy' · EEEE", new Locale("es", "PE"));
    private static final DateTimeFormatter WEEKDAY =
            DateTimeFormatter.ofPattern("EEEE d MMM", new Locale("es", "PE"));

    public static void refresh(Context context) {
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        for (int id : manager.getAppWidgetIds(
                new ComponentName(context, AcademicWeekWidget.class))) {
            update(context, manager, id);
        }
    }

    private static LocalDate selectedDate(Context context, int id) {
        String saved = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getString("day_" + id, "");
        try {
            LocalDate selected = LocalDate.parse(saved);
            if (Math.abs(java.time.temporal.ChronoUnit.DAYS.between(
                    LocalDate.now(), selected)) <= 28) return selected;
        } catch (RuntimeException ignored) { }
        return LocalDate.now();
    }

    private static PendingIntent dayAction(Context context, int id, String action,
                                            int requestCode) {
        Intent intent = new Intent(context, AcademicWeekWidget.class)
                .setAction(action)
                .setData(Uri.parse("agenda://academic/week/day/" + id + "/" + requestCode))
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id);
        return PendingIntent.getBroadcast(context, requestCode + id, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private static PendingIntent open(Context context, int id, String profileId) {
        Intent intent = profileId == null
                ? new Intent(context, AcademicWidgetSettingsActivity.class)
                : new Intent(context, ScheduleActivity.class).putExtra("profile_id", profileId);
        intent.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
                .setData(Uri.parse("agenda://academic/week/open/" + id));
        return PendingIntent.getActivity(context, 17000 + id, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private static void showCard(RemoteViews views, int index, ScheduleEntry entry,
                                  boolean privacy, LocalDate selected) {
        int card = index == 0 ? R.id.ac_week_card_1 : R.id.ac_week_card_2;
        int course = index == 0 ? R.id.ac_week_course_1 : R.id.ac_week_course_2;
        int time = index == 0 ? R.id.ac_week_time_1 : R.id.ac_week_time_2;
        int room = index == 0 ? R.id.ac_week_room_1 : R.id.ac_week_room_2;
        int badge = index == 0 ? R.id.ac_week_status_1 : R.id.ac_week_status_2;
        int subjectIcon = index == 0 ? R.id.ac_week_subject_1 : R.id.ac_week_subject_2;
        views.setViewVisibility(card, View.VISIBLE);
        views.setTextViewText(course, privacy ? "Clase programada" : entry.course);
        views.setTextViewText(time, AcademicWidgetRepository.timeLabel(entry.start)
                + "–" + AcademicWidgetRepository.timeLabel(entry.end));
        String place = entry.room == null || entry.room.trim().isEmpty()
                ? "Aula por definir" : entry.room.trim();
        views.setTextViewText(room, privacy ? "Aula privada" : place);
        boolean finished = selected.isBefore(LocalDate.now()) ||
                (selected.equals(LocalDate.now()) &&
                        entry.end <= LocalTime.now().toSecondOfDay() / 60);
        views.setImageViewResource(badge, finished ? R.drawable.ac_week_done
                : R.drawable.ac_week_pending);
        views.setImageViewResource(subjectIcon, index == 0 ? R.drawable.ac_week_books
                : R.drawable.ac_week_flask);
    }

    public static void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews views = new RemoteViews(context.getPackageName(),
                R.layout.widget_academic_week);
        LocalDate selected = selectedDate(context, id);
        String day = selected.equals(LocalDate.now()) ? DATE.format(selected)
                : WEEKDAY.format(selected);
        views.setTextViewText(R.id.ac_week_day, day);
        views.setOnClickPendingIntent(R.id.ac_week_previous,
                dayAction(context, id, ACTION_PREV, 18000));
        views.setOnClickPendingIntent(R.id.ac_week_next,
                dayAction(context, id, ACTION_NEXT, 19000));
        views.setViewVisibility(R.id.ac_week_card_2, View.GONE);
        Bundle opts = manager.getAppWidgetOptions(id);
        int height = opts == null ? 235 : opts.getInt(
                AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 235);
        boolean compact = height < 205;
        AcademicSchedules.Profile profile = null;
        try { profile = AcademicWidgetRepository.profile(context, id); }
        catch (RuntimeException ignored) { }
        String profileId = profile == null ? null : profile.id;
        PendingIntent activity = open(context, id, profileId);
        views.setOnClickPendingIntent(R.id.ac_week_heading, activity);
        views.setOnClickPendingIntent(R.id.ac_week_card_1, activity);
        views.setOnClickPendingIntent(R.id.ac_week_card_2, activity);
        if (profile == null) {
            views.setTextViewText(R.id.ac_week_course_1, "Selecciona tu horario");
            views.setTextViewText(R.id.ac_week_time_1, "Toca para configurar");
            views.setTextViewText(R.id.ac_week_room_1, "");
            views.setImageViewResource(R.id.ac_week_status_1, R.drawable.ac_week_pending);
        } else {
            try {
                WidgetAppearance.Settings settings = WidgetAppearance.read(context, id);
                List<ScheduleEntry> all = AcademicWidgetRepository.classes(context, profile.id);
                List<ScheduleEntry> current = new ArrayList<>();
                for (ScheduleEntry entry : all) {
                    if (entry.day == selected.getDayOfWeek().getValue()) current.add(entry);
                }
                if (current.isEmpty()) {
                    views.setTextViewText(R.id.ac_week_course_1, "Sin clases programadas");
                    views.setTextViewText(R.id.ac_week_time_1, "Elige otro día");
                    views.setTextViewText(R.id.ac_week_room_1, "");
                    views.setImageViewResource(R.id.ac_week_status_1,
                            R.drawable.ac_week_pending);
                } else {
                    showCard(views, 0, current.get(0), settings.hidePrivateTitles, selected);
                    if (!compact && current.size() > 1)
                        showCard(views, 1, current.get(1), settings.hidePrivateTitles, selected);
                }
            } catch (RuntimeException error) {
                views.setTextViewText(R.id.ac_week_course_1, "No se pudo leer el horario");
                views.setTextViewText(R.id.ac_week_time_1, "Abre Agenda Clara");
                views.setTextViewText(R.id.ac_week_room_1, "");
            }
        }
        manager.updateAppWidget(id, views);
    }

    @Override public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        String action = intent == null ? null : intent.getAction();
        if (!ACTION_PREV.equals(action) && !ACTION_NEXT.equals(action)) return;
        int id = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,
                AppWidgetManager.INVALID_APPWIDGET_ID);
        if (id == AppWidgetManager.INVALID_APPWIDGET_ID) return;
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        if (manager.getAppWidgetInfo(id) == null) return;
        LocalDate current = selectedDate(context, id);
        LocalDate shifted = current.plusDays(ACTION_NEXT.equals(action) ? 1 : -1);
        if (Math.abs(java.time.temporal.ChronoUnit.DAYS.between(
                LocalDate.now(), shifted)) > 28) return;
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putString("day_" + id, shifted.toString()).apply();
        update(context, manager, id);
    }
    @Override public void onUpdate(Context c, AppWidgetManager m, int[] ids) {
        for (int id : ids) update(c, m, id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c, AppWidgetManager m,
            int id, Bundle options) { update(c, m, id); }
    @Override public void onDeleted(Context c, int[] ids) {
        for (int id : ids) {
            c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                    .remove("day_" + id).apply();
            WidgetAppearance.remove(c, id);
        }
    }
}