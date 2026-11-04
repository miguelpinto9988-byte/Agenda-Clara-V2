package pe.agendaclara.app;

import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.content.res.ColorStateList;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.Calendar;

/**
 * Phase 12: three real actions directly on Inicio. Does not switch tabs.
 * Uses the existing Store, reminders, widgets and sticky-note editor.
 */
public final class MiDiaQuickActions {
    private static final int INK = 0xff182746;
    private static final int MUTED = 0xff556785;
    private MiDiaQuickActions() {}

    private static void saved(MainActivity a, String title, long due) {
        Task task = new Task();
        task.title = title;
        task.source = "manual";
        task.category = "General";
        task.due = due;
        long id = Store.get(a).save(task);
        if (id <= 0) {
            a.toast("No se pudo guardar. Vuelve a intentarlo.");
            return;
        }
        if (due > 0) Reminders.schedule(a, task);
        TaskWidget.refresh(a);
        a.forceRefresh = true;
        a.render();
        a.toast(due > 0 ? "Recordatorio creado." : "Tarea guardada.");
        if (due > 0 && (!Reminders.canNotify(a) || !Reminders.exact(a))) {
            a.dialogBuilder().setTitle("Permisos de recordatorio")
                    .setMessage("Se guardó la actividad. Para recibir el aviso a la hora elegida, revisa los permisos de notificaciones y alarmas en los ajustes de Agenda Clara.")
                    .setPositiveButton("Entendido", null).show();
        }
    }

    private static void chooseReminderTime(MainActivity a, String title) {
        LocalDate today = LocalDate.now();
        DatePickerDialog date = new DatePickerDialog(a, (picker, year, month, day) -> {
            LocalDate chosen = LocalDate.of(year, month + 1, day);
            LocalTime current = LocalTime.now().plusMinutes(30);
            TimePickerDialog time = new TimePickerDialog(a, (clock, hour, minute) -> {
                long due = chosen.atTime(hour, minute)
                        .atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
                if (due <= System.currentTimeMillis()) {
                    a.dialogBuilder().setTitle("Hora anterior")
                            .setMessage("Elige una fecha y hora posteriores a este momento.")
                            .setPositiveButton("Volver a elegir", (d, w) ->
                                    chooseReminderTime(a, title))
                            .setNegativeButton("Cancelar", null).show();
                } else {
                    saved(a, title, due);
                }
            }, current.getHour(), current.getMinute(), false);
            time.setTitle("Hora del recordatorio");
            time.show();
        }, today.getYear(), today.getMonthValue() - 1, today.getDayOfMonth());
        date.setTitle("Fecha del recordatorio");
        date.getDatePicker().setMinDate(System.currentTimeMillis() - 24L * 3600_000L);
        date.show();
    }

    private static void quickTask(MainActivity a, boolean reminder) {
        EditText title = a.input(reminder ? "¿Qué quieres recordar?" : "¿Qué tienes que hacer?",
                "", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        title.setSingleLine(true);
        title.setFilters(new InputFilter[]{new InputFilter.LengthFilter(140)});
        title.setContentDescription(reminder ? "Descripción del recordatorio" : "Nombre de la tarea rápida");
        LinearLayout input = a.column();
        input.setPadding(a.dp(17), a.dp(8), a.dp(17), a.dp(2));
        input.addView(title);
        AlertDialog dialog = a.dialogBuilder()
                .setTitle(reminder ? "Recordatorio rápido" : "Tarea rápida")
                .setView(input)
                .setPositiveButton(reminder ? "Elegir fecha y hora" : "Guardar", null)
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.setOnShowListener(ignored ->
                dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
                    String value = title.getText().toString().trim();
                    if (value.isEmpty()) {
                        title.setError("Escribe primero una descripción");
                        return;
                    }
                    dialog.dismiss();
                    if (reminder) chooseReminderTime(a, value);
                    else saved(a, value, 0);
                }));
        dialog.show();
    }

    private static LinearLayout tile(MainActivity a, String caption, String description,
                                     String iconName, int tint, int ink, Runnable click) {
        LinearLayout holder = a.column();
        holder.setGravity(Gravity.CENTER);
        holder.setPadding(a.dp(4), a.dp(9), a.dp(4), a.dp(9));
        holder.setMinimumHeight(a.dp(84));
        holder.setBackground(a.rounded(tint, 15));
        ImageView icon = new ImageView(a);
        icon.setImageDrawable(new UiDesign.OutlineIcon(iconName, ink));
        icon.setContentDescription(null);
        LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(a.dp(26), a.dp(26));
        imageParams.bottomMargin = a.dp(5);
        holder.addView(icon, imageParams);
        TextView text = a.text(caption, 11, INK, true);
        text.setMaxLines(2);
        text.setGravity(Gravity.CENTER);
        holder.addView(text, new LinearLayout.LayoutParams(-1, -2));
        holder.setContentDescription(description);
        holder.setFocusable(true);
        holder.setClickable(true);
        holder.setOnClickListener(v -> click.run());
        return holder;
    }

    public static void add(MainActivity a, LinearLayout parent) {
        LinearLayout.LayoutParams headingParams = new LinearLayout.LayoutParams(-1, -2);
        headingParams.topMargin = a.dp(14);
        TextView heading = a.text("⚡  Acciones rápidas", 17, INK, true);
        heading.setContentDescription("Acciones rápidas para añadir tareas, notas y recordatorios desde Inicio");
        parent.addView(heading, headingParams);
        a.gap(parent, 8);

        LinearLayout first = tile(a, "Tarea rápida", "Crear tarea rápida desde Inicio",
                "check", 0xffe8f3ff, 0xff1877d4, () -> quickTask(a, false));
        LinearLayout second = tile(a, "Nota rápida", "Crear nota rápida desde Inicio",
                "notes", 0xfff2eaff, 0xff8149d9, () -> StickyNotesUi.showEditor(a, null));
        LinearLayout third = tile(a, "Recordatorio", "Crear recordatorio con fecha y hora",
                "bell", 0xfffff4dc, 0xffdd9200, () -> quickTask(a, true));

        int widthDp = a.getResources().getConfiguration().screenWidthDp;
        float fontScale = a.getResources().getConfiguration().fontScale;
        if (widthDp < 320 || fontScale >= 1.45f) {
            for (LinearLayout tile : new LinearLayout[]{first, second, third}) {
                LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2);
                p.bottomMargin = a.dp(6);
                parent.addView(tile, p);
            }
        } else {
            LinearLayout row = a.row();
            LinearLayout[] items = {first, second, third};
            for (int i = 0; i < items.length; i++) {
                LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, -2, 1);
                if (i > 0) p.leftMargin = a.dp(5);
                row.addView(items[i], p);
            }
            parent.addView(row);
        }
    }
}
