package pe.agendaclara.app;

import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Inicio > Mi día > Acciones rápidas.
 *
 * Reuses the EXACT three actions and approved PNG illustrations of the
 * existing CreationChoices popup: voice task, full task editor, dated note.
 * No new icons, data schema, microphone handling, saved recordings, or tabs.
 */
public final class MiDiaQuickActions {
    private static final int INK = 0xff182746;
    private static final int MUTED = 0xff61738f;
    private static final int LINK = 0xff3469dc;
    private static final int BORDER = 0xffdbe4f4;

    private MiDiaQuickActions() {}

    private static void option(MainActivity activity, LinearLayout parent,
                               String title, String subtitle, String png,
                               Runnable action) {
        LinearLayout card = activity.row();
        card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(activity.dp(13), activity.dp(10),
                activity.dp(13), activity.dp(10));
        card.setMinimumHeight(activity.dp(78));
        GradientDrawable surface = activity.rounded(0xffffffff, 17);
        surface.setStroke(activity.dp(1), BORDER);
        card.setBackground(surface);
        card.setElevation(activity.dp(2));
        card.setContentDescription(title + ". " + subtitle);
        card.setFocusable(true);
        card.setClickable(true);
        card.setOnClickListener(v -> action.run());

        // Icons already shipped with Agenda Clara, so no PNG generation is
        // necessary while the new 3D iconography is being designed.
        ImageView artwork = ApprovedPng.view(activity, png, 36);
        artwork.setContentDescription(null);
        artwork.setImportantForAccessibility(ImageView.IMPORTANT_FOR_ACCESSIBILITY_NO);
        artwork.setScaleType(ImageView.ScaleType.FIT_CENTER);
        LinearLayout.LayoutParams artParams =
                new LinearLayout.LayoutParams(activity.dp(45), activity.dp(45));
        artParams.rightMargin = activity.dp(12);
        card.addView(artwork, artParams);

        LinearLayout labels = activity.column();
        TextView name = activity.text(title, 16, INK, true);
        name.setMaxLines(2);
        labels.addView(name);
        TextView hint = activity.text(subtitle, 11, MUTED, false);
        hint.setMaxLines(2);
        labels.addView(hint);
        card.addView(labels, new LinearLayout.LayoutParams(0, -2, 1));

        TextView arrow = activity.text("›", 28, LINK, true);
        arrow.setGravity(Gravity.CENTER);
        arrow.setContentDescription(null);
        LinearLayout.LayoutParams arrowParams =
                new LinearLayout.LayoutParams(activity.dp(19), activity.dp(44));
        arrowParams.leftMargin = activity.dp(5);
        card.addView(arrow, arrowParams);

        LinearLayout.LayoutParams layout = new LinearLayout.LayoutParams(-1, -2);
        layout.bottomMargin = activity.dp(9);
        parent.addView(card, layout);
    }

    public static void add(MainActivity activity, LinearLayout parent) {
        LinearLayout.LayoutParams headingLayout = new LinearLayout.LayoutParams(-1, -2);
        headingLayout.topMargin = activity.dp(14);
        TextView heading = activity.text("⚡  Acciones rápidas", 17, INK, true);
        parent.addView(heading, headingLayout);
        activity.gap(parent, 8);

        option(activity, parent, "Tarea rápida",
                "Dictar con comandos · sin grabación guardada",
                "voice_microphone", () -> VoiceQuickTask.show(activity));
        option(activity, parent, "Nueva tarea",
                "Registrar una actividad",
                "save", () -> activity.openEditor(-1, null, null));
        option(activity, parent, "Nueva nota",
                "Nota adhesiva con fecha",
                "sticky_note", () -> StickyNotesUi.showEditor(activity, null));
    }
}
