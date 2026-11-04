package pe.agendaclara.app;

import android.content.Intent;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

/** New Más hub, exposing every original destination rather than removing it. */
public final class MiDiaMorePage {
    private static final int INK = 0xff182746;
    private static final int MUTED = 0xff62718a;
    private static final int BLUE = 0xff3877d9;
    private MiDiaMorePage() {}

    private static void link(MainActivity a, LinearLayout parent, String name,
                             String detail, String symbol, Runnable action) {
        LinearLayout row = a.row();
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setMinimumHeight(a.dp(66));
        row.setPadding(a.dp(10), a.dp(9), a.dp(10), a.dp(9));
        row.setBackground(a.rounded(0xfff7f9ff, 14));
        ImageView icon = new ImageView(a);
        icon.setImageDrawable(new UiDesign.OutlineIcon(symbol, BLUE));
        icon.setContentDescription(null);
        LinearLayout.LayoutParams iconSize = new LinearLayout.LayoutParams(a.dp(30), a.dp(30));
        iconSize.rightMargin = a.dp(13);
        row.addView(icon, iconSize);
        LinearLayout textBlock = a.column();
        TextView title = a.text(name, 15, INK, true);
        title.setSingleLine(true);
        textBlock.addView(title);
        TextView subtitle = a.text(detail, 11, MUTED, false);
        subtitle.setMaxLines(2);
        textBlock.addView(subtitle);
        row.addView(textBlock, new LinearLayout.LayoutParams(0, -2, 1));
        row.addView(a.text("›", 25, BLUE, true));
        row.setContentDescription(name + ". " + detail);
        row.setFocusable(true);
        row.setOnClickListener(v -> action.run());
        parent.addView(row);
        a.gap(parent, 7);
    }

    private static void section(MainActivity a, String name) {
        a.body.addView(a.text(name, 17, INK, true));
        a.gap(a.body, 9);
    }

    private static void originalPage(MainActivity a, int page, int connectionTab) {
        a.page = page;
        if (page == 3) a.connectionTab = connectionTab;
        a.render();
    }

    public static void render(MainActivity a) {
        a.body.addView(a.text("Más opciones", 24, INK, true));
        a.body.addView(a.text("Todas tus funciones de Agenda Clara siguen disponibles.",
                13, MUTED, false));
        a.gap(a.body, 19);

        section(a, "Organización");
        link(a, a.body, "Mis tareas y categorías", "Buscar, editar y organizar actividades",
                "check", () -> MiDiaNavigation.open(a, 1));
        link(a, a.body, "Crear nota adhesiva", "Notas rápidas con fecha y categoría",
                "notes", () -> StickyNotesUi.showEditor(a, null));
        link(a, a.body, "Gestionar categorías", "Colores, nombres e iconos",
                "folder", () -> {
                    MiDiaNavigation.open(a, 1);
                    a.showCategories();
                });
        link(a, a.body, "Mi horario de clases", "Horarios, cursos y sesiones existentes",
                "calendar", () -> a.startActivity(new Intent(a, ScheduleActivity.class)));
        a.gap(a.body, 9);

        section(a, "Revisión y conexiones");
        link(a, a.body, "Propuestas y notificaciones",
                "Actividades pendientes de revisar", "inbox",
                () -> originalPage(a, 2, 0));
        link(a, a.body, "WhatsApp y grupos", "Permisos y grupos autorizados",
                "link", () -> originalPage(a, 3, 0));
        link(a, a.body, "Calendarios conectados",
                "Seleccionar calendarios y sincronización", "calendar",
                () -> originalPage(a, 3, 1));
        a.gap(a.body, 9);

        section(a, "Herramientas y ajustes");
        link(a, a.body, "Crear tarea por voz",
                "Usar el dictado de voz de Agenda Clara", "bell",
                () -> VoiceQuickTask.show(a));
        link(a, a.body, "Ajustes y privacidad",
                "Configuración, avisos y permisos", "gear",
                () -> originalPage(a, 3, 2));
        a.gap(a.body, 12);

        LinearLayout note = a.card(a.body);
        note.setBackground(a.rounded(0xffedf6ff, 15));
        note.addView(a.text("Tus datos siguen en el dispositivo", 14, INK, true));
        a.gap(note, 4);
        note.addView(a.text("El nuevo menú solo reorganiza accesos. "
                + "No reemplaza tu calendario, WhatsApp, tareas, notas ni widgets.",
                12, MUTED, false));
    }
}
