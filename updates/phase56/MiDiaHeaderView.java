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
    private final LinearLayout floatingDate;
    private final FrameLayout imageStack;
    private final FrameLayout landscapeFrame;
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
        // Android 15 edge-to-edge uses light status-bar icons by default in
        // some themes; keep the clock readable against the very light home.
        if (context instanceof MainActivity) {
            MainActivity host = (MainActivity) context;
            if (android.os.Build.VERSION.SDK_INT >= 30) {
                android.view.WindowInsetsController controller = host.getWindow().getInsetsController();
                if (controller != null) controller.setSystemBarsAppearance(
                        android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS,
                        android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS);
            } else {
                View decor = host.getWindow().getDecorView();
                decor.setSystemUiVisibility(decor.getSystemUiVisibility()
                        | View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
            }
        }

        // Brand + real inbox shortcut + connection/settings shortcut.
        LinearLayout top = new LinearLayout(context);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setPadding(dp(14), 0, dp(14), 0);
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
        imageStack = new FrameLayout(context);
        imageStack.setClipChildren(false);
        imageStack.setClipToPadding(false);
        addView(imageStack, new LayoutParams(-1, dp(245)));

        // Full-width panoramic hero: no inset card and no rounded photo crop.
        // Its height follows the actual view width on phones and tablets.
        landscapeFrame = new FrameLayout(context);
        landscapeFrame.setBackgroundColor(0xffe9f4ff);
        FrameLayout.LayoutParams coverParams =
                new FrameLayout.LayoutParams(-1, dp(205), Gravity.TOP);
        imageStack.addView(landscapeFrame, coverParams);

        landscape = new ImageView(context);
        landscape.setScaleType(ImageView.ScaleType.CENTER_CROP);
        landscape.setContentDescription("Paisaje ilustrado del día");
        landscapeFrame.addView(landscape, new FrameLayout.LayoutParams(-1, -1));

        View readableOverlay = new View(context);
        readableOverlay.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{0xf5ffffff, 0xaaffffff, 0x12ffffff}));
        landscapeFrame.addView(readableOverlay, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout welcome = new LinearLayout(context);
        welcome.setOrientation(VERTICAL);
        welcome.setPadding(dp(15), dp(16), dp(13), dp(8));
        landscapeFrame.addView(welcome, new FrameLayout.LayoutParams(-1, -2, Gravity.TOP));

        greeting = text(context, "", 23, INK, true);
        greeting.setContentDescription("Saludo del día. Toca para personalizar el nombre");
        welcome.addView(greeting);
        if (context instanceof MainActivity) {
            greeting.setOnClickListener(v -> nameEditor((MainActivity) context));
        }

        TextView intro = text(context, "Aquí tienes tu día, en un vistazo.", 13, MUTED, false);
        welcome.addView(intro);

        floatingDate = new LinearLayout(context);
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
        imageStack.addView(floatingDate, dateParams);

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

    @Override
    protected void onSizeChanged(int width, int height, int oldWidth, int oldHeight) {
        super.onSizeChanged(width, height, oldWidth, oldHeight);
        if (width <= 0) return;
        // Source backgrounds are 1920 x 864 (~2.22:1). Preserve that ratio
        // for tablets, yet keep enough height for greetings on narrow phones.
        int visualHeight = Math.max(dp(205),
                Math.min(dp(450), Math.round(width * 864f / 1920f)));
        LayoutParams stackParams = (LayoutParams) imageStack.getLayoutParams();
        if (stackParams.height != visualHeight + dp(40)) {
            stackParams.height = visualHeight + dp(40);
            imageStack.setLayoutParams(stackParams);
        }
        FrameLayout.LayoutParams picture =
                (FrameLayout.LayoutParams) landscapeFrame.getLayoutParams();
        if (picture.height != visualHeight) {
            picture.height = visualHeight;
            landscapeFrame.setLayoutParams(picture);
        }
    }

    public void refresh() {
        LocalDate today = LocalDate.now();
        int hour = LocalTime.now().getHour();
        String opening = hour < 12 ? "¡Buenos días" : hour < 19 ? "¡Buenas tardes" : "¡Buenas noches";
        String name = Prefs.get(getContext()).getString(NAME_KEY, "").trim();
        greeting.setText(opening + (name.isEmpty() ? "" : ", " + name) + "! 👋");
        greeting.setContentDescription(greeting.getText() + ". Toca para personalizar el nombre.");
        if (!today.equals(renderedDate)) {
            renderedDate = today;
            int background = MiDiaDailyRotation.backgroundResource(getContext(), today);
            if (background != 0) landscape.setImageResource(background);
            dateTitle.setText("Hoy, " + today.format(DateTimeFormatter.ofPattern(
                    "EEE d 'de' MMMM", ES)));
            dateSubtitle.setText("Semana " + today.get(IsoFields.WEEK_OF_WEEK_BASED_YEAR)
                    + " · Día " + today.getDayOfYear() + " del año");
            floatingDate.setContentDescription(dateTitle.getText() + ". " + dateSubtitle.getText());
            quote.setText("★  " + MiDiaDailyRotation.quote(getContext(), today));
        }
    }
}
