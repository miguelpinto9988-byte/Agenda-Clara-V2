package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputFilter;
import android.text.InputType;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.IsoFields;
import java.util.Locale;

/**
 * Phase 5: visual header of Inicio — Mi día.
 * Only adds home-local chrome; the original Activity, stores and tabs remain.
 * All 30 images and 50 phrases continue to rotate fully offline.
 */
public final class MiDiaHeaderView extends LinearLayout {
    private static final int INK = 0xff132343;
    private static final int MUTED = 0xff455878;
    private static final int ACCENT = 0xff1285d5;
    private static final Locale ES = new Locale("es", "PE");
    private static final String NAME_KEY = "mi_dia_saludo_nombre";

    private final ImageView landscape;
    private final TextView greeting;
    private final TextView dateTitle;
    private final TextView dateSubtitle;
    private final TextView quote;
    private LocalDate renderedDate;

    private int dp(float n) {
        return Math.round(n * getResources().getDisplayMetrics().density);
    }

    private GradientDrawable rounded(int color, int radius) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(color);
        shape.setCornerRadius(dp(radius));
        return shape;
    }

    private TextView text(Context context, String value, float size, int color, boolean bold) {
        TextView view = new TextView(context);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        view.setGravity(Gravity.CENTER_VERTICAL);
        return view;
    }

    private FrameLayout action(Context context, String iconName, String accessibility, Runnable callback) {
        FrameLayout hit = new FrameLayout(context);
        hit.setContentDescription(accessibility);
        hit.setFocusable(true);
        hit.setClickable(true);
        hit.setBackground(rounded(0xfff5f8ff, 12));
        ImageView pictogram = new ImageView(context);
        pictogram.setImageDrawable(new UiDesign.OutlineIcon(iconName, INK));
        FrameLayout.LayoutParams picture = new FrameLayout.LayoutParams(dp(24), dp(24), Gravity.CENTER);
        hit.addView(pictogram, picture);
        hit.setOnClickListener(v -> callback.run());
        return hit;
    }

    private void nameEditor(MainActivity activity) {
        SharedPreferences preferences = Prefs.get(activity);
        EditText input = activity.input("Tu nombre (opcional)", preferences.getString(NAME_KEY, ""),
                InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_WORDS);
        input.setSingleLine(true);
        input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(28)});
        activity.dialogBuilder()
                .setTitle("Personalizar saludo")
                .setMessage("Este nombre se guarda solo en este dispositivo.")
                .setView(input)
                .setPositiveButton("Guardar", (dialog, which) -> {
                    preferences.edit().putString(NAME_KEY, input.getText().toString().trim()).apply();
                    refresh();
                })
                .setNeutralButton("Quitar nombre", (dialog, which) -> {
                    preferences.edit().remove(NAME_KEY).apply();
                    refresh();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private static String appVersion(Context context) {
        try {
            PackageInfo pkg = context.getPackageManager().getPackageInfo(context.getPackageName(), 0);
            return pkg.versionName == null ? "" : "v" + pkg.versionName;
        } catch (Exception ignored) {
            return "";
        }
    }

    public MiDiaHeaderView(Context context) {
        super(context);
        setOrientation(VERTICAL);
        setBackgroundColor(Color.TRANSPARENT);
        setTag("mi_dia_phase5_header");

        // Brand + real inbox shortcut + connection/settings shortcut.
        LinearLayout top = new LinearLayout(context);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setOrientation(HORIZONTAL);
        LayoutParams topParams = new LayoutParams(-1, dp(54));
        topParams.bottomMargin = dp(9);
        addView(top, topParams);

        ImageView logo = new ImageView(context);
        logo.setImageResource(R.drawable.ic_app);
        logo.setContentDescription("Agenda Clara");
        LinearLayout.LayoutParams logoParams = new LinearLayout.LayoutParams(dp(36), dp(36));
        logoParams.rightMargin = dp(6);
        top.addView(logo, logoParams);

        LinearLayout branding = new LinearLayout(context);
        branding.setGravity(Gravity.CENTER_VERTICAL);
        branding.setOrientation(HORIZONTAL);
        top.addView(branding, new LinearLayout.LayoutParams(0, -2, 1));

        TextView brand = text(context, "Agenda Clara", 16, INK, true);
        brand.setSingleLine(true);
        brand.setEllipsize(TextUtils.TruncateAt.END);
        branding.addView(brand, new LinearLayout.LayoutParams(0, -2, 1));

        String version = appVersion(context);
        if (!version.isEmpty()) {
            TextView versionPill = text(context, version, 10, MUTED, true);
            versionPill.setSingleLine(true);
            versionPill.setGravity(Gravity.CENTER);
            versionPill.setPadding(dp(5), dp(4), dp(5), dp(4));
            versionPill.setBackground(rounded(0xffeff1fa, 9));
            LinearLayout.LayoutParams versionParams = new LinearLayout.LayoutParams(-2, -2);
            versionParams.leftMargin = dp(4);
            branding.addView(versionPill, versionParams);
        }

        if (context instanceof MainActivity) {
            MainActivity activity = (MainActivity) context;
            FrameLayout inbox = action(context, "bell", "Revisar propuestas y notificaciones", () -> {
                activity.page = 2;
                activity.render();
            });
            LinearLayout.LayoutParams inboxParams = new LinearLayout.LayoutParams(dp(44), dp(44));
            inboxParams.leftMargin = dp(4);
            top.addView(inbox, inboxParams);
            if (!Store.get(activity).inbox().isEmpty()) {
                View dot = new View(context);
                dot.setBackground(rounded(0xffff4747, 7));
                dot.setContentDescription("Hay propuestas por revisar");
                FrameLayout.LayoutParams dotParams = new FrameLayout.LayoutParams(dp(9), dp(9),
                        Gravity.TOP | Gravity.RIGHT);
                dotParams.rightMargin = dp(6);
                dotParams.topMargin = dp(5);
                inbox.addView(dot, dotParams);
            }

            FrameLayout settings = action(context, "gear", "Abrir conexiones y ajustes", () -> {
                activity.page = 3;
                activity.render();
            });
            LinearLayout.LayoutParams settingsParams = new LinearLayout.LayoutParams(dp(44), dp(44));
            settingsParams.leftMargin = dp(4);
            top.addView(settings, settingsParams);
        }

        // Background is a day-based drawable, never a downloaded image.
        FrameLayout headerStack = new FrameLayout(context);
        headerStack.setClipChildren(false);
        headerStack.setClipToPadding(false);
        addView(headerStack, new LayoutParams(-1, dp(237)));

        FrameLayout cover = new FrameLayout(context);
        cover.setBackground(rounded(0xffe9f4ff, 19));
        cover.setClipToOutline(true);
        FrameLayout.LayoutParams coverParams = new FrameLayout.LayoutParams(-1, dp(198), Gravity.TOP);
        headerStack.addView(cover, coverParams);

        landscape = new ImageView(context);
        landscape.setScaleType(ImageView.ScaleType.CENTER_CROP);
        landscape.setContentDescription("Paisaje ilustrado del día");
        cover.addView(landscape, new FrameLayout.LayoutParams(-1, -1));

        View readableOverlay = new View(context);
        readableOverlay.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{0xf5ffffff, 0xaaffffff, 0x12ffffff}));
        cover.addView(readableOverlay, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout welcome = new LinearLayout(context);
        welcome.setOrientation(VERTICAL);
        welcome.setPadding(dp(15), dp(16), dp(13), dp(8));
        cover.addView(welcome, new FrameLayout.LayoutParams(-1, -2, Gravity.TOP));

        greeting = text(context, "", 23, INK, true);
        greeting.setContentDescription("Saludo del día. Toca para personalizar el nombre");
        welcome.addView(greeting);
        if (context instanceof MainActivity) {
            greeting.setOnClickListener(v -> nameEditor((MainActivity) context));
        }

        TextView intro = text(context, "Aquí tienes tu día, en un vistazo.", 13, MUTED, false);
        welcome.addView(intro);

        LinearLayout floatingDate = new LinearLayout(context);
        floatingDate.setOrientation(HORIZONTAL);
        floatingDate.setGravity(Gravity.CENTER_VERTICAL);
        floatingDate.setPadding(dp(13), dp(9), dp(13), dp(9));
        GradientDrawable card = rounded(0xfaffffff, 17);
        card.setStroke(dp(1), 0xffdce4f2);
        floatingDate.setBackground(card);
        floatingDate.setElevation(dp(3));
        floatingDate.setContentDescription("Fecha de hoy");
        FrameLayout.LayoutParams dateParams = new FrameLayout.LayoutParams(-1, dp(65), Gravity.BOTTOM);
        dateParams.leftMargin = dp(11);
        dateParams.rightMargin = dp(11);
        dateParams.bottomMargin = dp(8);
        headerStack.addView(floatingDate, dateParams);

        FrameLayout dateIconTile = new FrameLayout(context);
        dateIconTile.setBackground(rounded(0xffe9f6ff, 12));
        ImageView dateIcon = new ImageView(context);
        dateIcon.setImageDrawable(new UiDesign.OutlineIcon("calendar", ACCENT));
        dateIconTile.addView(dateIcon, new FrameLayout.LayoutParams(dp(25), dp(25), Gravity.CENTER));
        LinearLayout.LayoutParams dateIconParams = new LinearLayout.LayoutParams(dp(43), dp(43));
        dateIconParams.rightMargin = dp(11);
        floatingDate.addView(dateIconTile, dateIconParams);

        LinearLayout dateLines = new LinearLayout(context);
        dateLines.setOrientation(VERTICAL);
        floatingDate.addView(dateLines, new LinearLayout.LayoutParams(0, -2, 1));
        dateTitle = text(context, "", 15, INK, true);
        dateTitle.setSingleLine(true);
        dateTitle.setEllipsize(TextUtils.TruncateAt.END);
        dateLines.addView(dateTitle);
        dateSubtitle = text(context, "", 11, MUTED, false);
        dateLines.addView(dateSubtitle);

        // Quote remains here in phase 5; phase 6 will move it below progress.
        quote = text(context, "", 13, 0xff785a18, false);
        quote.setPadding(dp(12), dp(10), dp(12), dp(10));
        quote.setBackground(rounded(0xfffff5df, 14));
        quote.setContentDescription("Frase motivadora del día");
        LayoutParams quoteParams = new LayoutParams(-1, -2);
        quoteParams.topMargin = dp(8);
        addView(quote, quoteParams);

        refresh();
    }

    public void refresh() {
        LocalDate today = LocalDate.now();
        int hour = LocalTime.now().getHour();
        String opening = hour < 12 ? "¡Buenos días" : hour < 19 ? "¡Buenas tardes" : "¡Buenas noches";
        String name = Prefs.get(getContext()).getString(NAME_KEY, "").trim();
        greeting.setText(opening + (name.isEmpty() ? "" : ", " + name) + "! 👋");
        if (!today.equals(renderedDate)) {
            renderedDate = today;
            int background = MiDiaDailyRotation.backgroundResource(getContext(), today);
            if (background != 0) landscape.setImageResource(background);
            dateTitle.setText("Hoy, " + today.format(DateTimeFormatter.ofPattern(
                    "EEE d 'de' MMMM", ES)));
            dateSubtitle.setText("Semana " + today.get(IsoFields.WEEK_OF_WEEK_BASED_YEAR)
                    + " · Día " + today.getDayOfYear() + " del año");
            quote.setText("★  " + MiDiaDailyRotation.quote(getContext(), today));
        }
    }
}
