package pe.agendaclara.app;

import android.content.Context;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.Locale;

/** Offline, deterministic daily artwork and motivational quote rotation. */
public final class MiDiaDailyRotation {
    private MiDiaDailyRotation() {}
    private static final LocalDate EPOCH = LocalDate.of(2026, 1, 1);

    public static int backgroundIndex(LocalDate day) {
        return (int) Math.floorMod(ChronoUnit.DAYS.between(EPOCH, day), 30);
    }

    public static int quoteIndex(LocalDate day) {
        return (int) Math.floorMod(ChronoUnit.DAYS.between(EPOCH, day) * 7, 50);
    }

    public static int backgroundResource(Context context, LocalDate day) {
        String name = String.format(Locale.ROOT, "bg_mi_dia_%02d", backgroundIndex(day) + 1);
        return context.getResources().getIdentifier(name, "drawable", context.getPackageName());
    }

    public static String quote(Context context, LocalDate day) {
        String[] quotes = context.getResources().getStringArray(R.array.mi_dia_frases);
        return quotes[quoteIndex(day)];
    }
}
