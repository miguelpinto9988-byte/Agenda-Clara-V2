package pe.agendaclara.app;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

/** Native offline daily header. Integrate only after installing its resources. */
public final class MiDiaHeaderView extends LinearLayout {
    private final ImageView landscape;
    private final TextView greeting;
    private final TextView date;
    private final TextView quote;
    private LocalDate renderedDate;

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    public MiDiaHeaderView(Context context) {
        super(context);
        setOrientation(VERTICAL);
        setBackgroundColor(Color.WHITE);
        setPadding(dp(16), dp(12), dp(16), dp(8));

        FrameLayout hero = new FrameLayout(context);
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(0xffeef5ff);
        shape.setCornerRadius(dp(18));
        hero.setBackground(shape);
        hero.setClipToOutline(true);
        addView(hero, new LayoutParams(LayoutParams.MATCH_PARENT, dp(190)));

        landscape = new ImageView(context);
        landscape.setScaleType(ImageView.ScaleType.CENTER_CROP);
        landscape.setContentDescription("Paisaje ilustrado del día");
        hero.addView(landscape, new FrameLayout.LayoutParams(-1, -1));

        View overlay = new View(context);
        overlay.setBackground(new GradientDrawable(
            GradientDrawable.Orientation.TOP_BOTTOM,
            new int[]{0xeaffffff, 0x9cffffff, 0x00ffffff}));
        hero.addView(overlay, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout heading = new LinearLayout(context);
        heading.setOrientation(VERTICAL);
        heading.setPadding(dp(16), dp(16), dp(16), dp(12));
        hero.addView(heading, new FrameLayout.LayoutParams(-1, -2, Gravity.TOP));

        greeting = new TextView(context);
        greeting.setTextSize(22);
        greeting.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        greeting.setTextColor(0xff142346);
        heading.addView(greeting);

        TextView subtitle = new TextView(context);
        subtitle.setText("Aquí tienes tu día, en un vistazo.");
        subtitle.setTextColor(0xff344566);
        subtitle.setTextSize(13);
        heading.addView(subtitle);

        date = new TextView(context);
        date.setTextSize(13);
        date.setTextColor(0xff142346);
        date.setPadding(0, dp(10), 0, dp(6));
        addView(date);

        quote = new TextView(context);
        quote.setTextSize(14);
        quote.setTextColor(0xff344566);
        quote.setPadding(dp(10), dp(9), dp(10), dp(9));
        quote.setBackgroundColor(0xfffff7e6);
        addView(quote, new LayoutParams(-1, -2));
        refresh();
    }

    public void refresh() {
        LocalDate today = LocalDate.now();
        int hour = LocalTime.now().getHour();
        greeting.setText(hour < 12 ? "¡Buenos días!" :
            hour < 19 ? "¡Buenas tardes!" : "¡Buenas noches!");
        if (!today.equals(renderedDate)) {
            renderedDate = today;
            int id = MiDiaDailyRotation.backgroundResource(getContext(), today);
            if (id != 0) landscape.setImageResource(id);
            date.setText(today.format(DateTimeFormatter.ofPattern(
                "EEEE, d 'de' MMMM", new Locale("es", "PE"))));
            quote.setText("✦  " + MiDiaDailyRotation.quote(getContext(), today));
        }
    }
}
