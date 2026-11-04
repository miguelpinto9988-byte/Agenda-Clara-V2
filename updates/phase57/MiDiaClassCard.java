package pe.agendaclara.app;

import android.content.Intent;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

/** Phase 10: the real class timetable inside Inicio — Mi día. */
public final class MiDiaClassCard {
    private static final int INK = 0xff182746;
    private static final int SECONDARY = 0xff657187;
    private static final int VIOLET = 0xff7447db;
    private static final Locale ES = new Locale("es", "PE");
    private MiDiaClassCard() {}

    private static TextView label(MainActivity a, String message, int size,
                                  int color, boolean bold) {
        return a.text(message, size, color, bold);
    }

    public static void add(MainActivity a, LinearLayout content, MiDiaNextClass.Result selection) {
        LinearLayout card = a.column();
        card.setPadding(a.dp(15), a.dp(13), a.dp(15), a.dp(13));
        card.setBackground(a.rounded(0xffeee9ff, 18));
        card.setTag("mi_dia_class_card");
        LinearLayout top = a.row();
        top.setGravity(Gravity.CENTER_VERTICAL);
        ImageView cap = new ImageView(a);
        cap.setImageDrawable(new UiDesign.OutlineIcon("graduation", VIOLET));
        cap.setContentDescription(null);
        LinearLayout.LayoutParams imageSize = new LinearLayout.LayoutParams(a.dp(31), a.dp(31));
        imageSize.rightMargin = a.dp(9);
        top.addView(cap, imageSize);
        LinearLayout lines = a.column();
        TextView small = label(a, selection != null && selection.inProgress
                ? "Clase en curso" : "Próxima clase", 12, VIOLET, true);
        lines.addView(small);
        if (selection == null) {
            lines.addView(label(a, "Todavía no hay clases en tu horario", 15, INK, true));
            a.gap(lines, 4);
            lines.addView(label(a,
                    "Agrega tus cursos en Estudio > Horario de clases.", 12, SECONDARY, false));
        } else {
            ScheduleEntry session = selection.entry;
            TextView course = label(a, session.course, 17, INK, true);
            course.setMaxLines(2);
            lines.addView(course);
            String day = selection.dayOffset == 0 ? "Hoy" :
                    selection.dayOffset == 1 ? "Mañana" :
                    Instant.ofEpochMilli(selection.beginsAt).atZone(ZoneId.systemDefault())
                            .format(DateTimeFormatter.ofPattern("EEE d MMM", ES));
            a.gap(lines, 4);
            lines.addView(label(a, day + " · " +
                    ScheduleEntry.clock(session.start) + "–" + ScheduleEntry.clock(session.end),
                    12, INK, false));
            if (session.room != null && !session.room.trim().isEmpty()) {
                lines.addView(label(a, "Aula: " + session.room, 12, SECONDARY, false));
            }
            if (session.teacher != null && !session.teacher.trim().isEmpty()) {
                lines.addView(label(a, "Profesor: " + session.teacher, 11, SECONDARY, false));
            }
            String status = selection.inProgress ? "En curso ahora" :
                    selection.minutesUntil < 60
                    ? "Empieza en " + selection.minutesUntil + " min"
                    : "Empieza en " + (selection.minutesUntil / 60) + " h"
                      + (selection.minutesUntil % 60 == 0 ? "" :
                          " " + (selection.minutesUntil % 60) + " min");
            a.gap(lines, 6);
            lines.addView(label(a, status, 12, VIOLET, true));
        }
        top.addView(lines, new LinearLayout.LayoutParams(0, -2, 1));
        TextView arrow = label(a, "›", 29, VIOLET, true);
        top.addView(arrow);
        card.addView(top);
        card.setFocusable(true);
        card.setContentDescription(selection == null
                ? "Horario de clases vacío. Abrir horario para agregar cursos."
                : (selection.inProgress ? "Clase en curso: " : "Próxima clase: ")
                + selection.entry.course + ". Abrir horario.");
        card.setOnClickListener(v -> a.startActivity(new Intent(a, ScheduleActivity.class)));
        LinearLayout.LayoutParams layout = new LinearLayout.LayoutParams(-1, -2);
        layout.topMargin = a.dp(8);
        content.addView(card, layout);
    }
}
