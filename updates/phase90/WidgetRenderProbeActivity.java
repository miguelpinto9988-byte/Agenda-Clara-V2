package pe.agendaclara.app;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.FrameLayout;
import android.widget.RemoteViews;

/** Debug-build-only smoke probe. Does not read or modify the user's widget data. */
public final class WidgetRenderProbeActivity extends Activity {
    private static final String TAG = "AgendaWidgetQA";

    private void check(int layout) {
        String name = getResources().getResourceEntryName(layout);
        RemoteViews remote = new RemoteViews(getPackageName(), layout);
        if (layout == R.layout.widget_academic_day) {
            AcademicWidgetTheme.apply(this, remote, R.id.academic_day_root,
                    new int[] {R.id.academic_day_heading, R.id.academic_day_course,
                               R.id.academic_day_tasks_label},
                    new int[] {R.id.academic_day_profile, R.id.academic_day_time,
                               R.id.academic_day_tasks}, "dark");
        } else if (layout == R.layout.widget_academic_week) {
            // The revised PNG background must not be replaced by legacy theme code.
            remote.setTextViewText(R.id.ac_week_day, "Hoy · Miércoles");
            remote.setTextViewText(R.id.ac_week_course_1, "Clase de prueba");
            remote.setTextViewText(R.id.ac_week_time_1, "08:00–10:00");
            remote.setTextViewText(R.id.ac_week_room_1, "Aula 101");
            remote.setViewVisibility(R.id.ac_week_card_2, android.view.View.VISIBLE);
            remote.setTextViewText(R.id.ac_week_course_2, "Segunda clase");
            remote.setImageViewResource(R.id.ac_week_status_1, R.drawable.ac_week_done);
            remote.setImageViewResource(R.id.ac_week_status_2, R.drawable.ac_week_pending);
        }
        FrameLayout parent = new FrameLayout(this);
        if (remote.apply(this, parent) == null) {
            throw new IllegalStateException("RemoteViews.apply returned null: " + name);
        }
        Log.i(TAG, "OK " + name);
    }

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        int[] layouts = {
            R.layout.widget_tasks,
            R.layout.widget_row,
            R.layout.widget_sticky_notes,
            R.layout.widget_sticky_notes_compact,
            R.layout.widget_sticky_row,
            R.layout.widget_sticky_row_compact,
            R.layout.widget_notes_board,
            R.layout.widget_notes_board_compact,
            R.layout.widget_notes_board_row,
            R.layout.widget_notes_board_row_compact,
            R.layout.widget_academic_day,
            R.layout.widget_academic_week,
            R.layout.widget_photo
        };
        int passed = 0;
        try {
            for (int layout : layouts) {
                check(layout);
                passed++;
            }
            Log.i(TAG, "PASS: " + passed + "/" + layouts.length
                    + " widget XML layouts inflated with RemoteViews.apply");
        } catch (Throwable problem) {
            Log.e(TAG, "FAIL rendering widget layout " + (passed + 1), problem);
            throw new IllegalStateException("Widget RemoteViews inflation QA failed", problem);
        } finally {
            finish();
        }
    }
}
