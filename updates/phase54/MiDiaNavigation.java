package pe.agendaclara.app;

import android.content.Context;
import android.view.inputmethod.InputMethodManager;

/** Maps the five design tabs to the original internal pages without removing routes. */
public final class MiDiaNavigation {
    public static final String[] TAB_LABELS = {"Inicio", "Tareas", "Estudio", "Calendario", "Más"};
    private MiDiaNavigation() {}

    /** The old review/connections destinations remain under the Más tab. */
    public static int selectedTab(MainActivity a) {
        if (a.page == 0) return Math.max(0, Math.min(2, a.homeSection));
        if (a.page == 1) return 3;
        return 4;
    }

    public static void open(MainActivity a, int tab) {
        if (tab < 0 || tab > 4) throw new IllegalArgumentException("Unknown Mi día tab");
        if (a.root != null) {
            a.root.requestFocus();
            InputMethodManager keyboard = (InputMethodManager) a.getSystemService(
                    Context.INPUT_METHOD_SERVICE);
            if (keyboard != null)
                keyboard.hideSoftInputFromWindow(a.root.getWindowToken(), 0);
        }
        if (tab < 3) {
            a.page = 0;
            a.homeSection = tab;
        } else if (tab == 3) {
            a.page = 1;
        } else {
            a.page = 4;
        }
        a.render();
    }
}
