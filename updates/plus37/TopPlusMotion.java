package pe.agendaclara.app;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.TimeInterpolator;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.OvershootInterpolator;

/** Animación del botón + con pivote geométrico central y sin desplazar su layout. */
public final class TopPlusMotion {
    private TopPlusMotion() {}
    public static void toggle(View plus, View menu, boolean open) {
        if (plus == null || menu == null) return;
        plus.animate().cancel();
        menu.animate().cancel();
        // El pivote usa el centro real, incluso tras cambios de tamaño o densidad.
        plus.setPivotX(plus.getWidth() / 2f);
        plus.setPivotY(plus.getHeight() / 2f);
        menu.setPivotX(menu.getWidth() / 2f);
        menu.setPivotY(0f);
        if (open) {
            menu.setVisibility(View.VISIBLE);
            menu.setAlpha(0f);
            menu.setScaleX(.94f);
            menu.setScaleY(.94f);
            menu.setTranslationY(-dp(menu, 12));
        }
        plus.animate().rotation(open ? 45f : 0f).scaleX(1f).scaleY(1f)
            .setDuration(320).setInterpolator(new OvershootInterpolator(1.15f)).start();
        menu.animate().alpha(open ? 1f : 0f)
            .translationY(open ? 0f : -dp(menu, 12))
            .scaleX(open ? 1f : .94f).scaleY(open ? 1f : .94f)
            .setDuration(open ? 300 : 190)
            .setInterpolator(new OvershootInterpolator(.75f))
            .setListener(new AnimatorListenerAdapter() {
                @Override public void onAnimationEnd(Animator a) {
                    if (!open) menu.setVisibility(View.GONE);
                    menu.setClickable(open);
                }
            }).start();
        plus.setContentDescription(open ? "Cerrar acciones" : "Abrir acciones");
        plus.setSelected(open);
    }
    private static float dp(View v, float n) {
        return n * v.getResources().getDisplayMetrics().density;
    }
}
