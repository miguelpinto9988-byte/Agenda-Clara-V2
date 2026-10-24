package pe.agendaclara.app;

import android.animation.ValueAnimator;
import android.view.View;

/** Only for explicit tab changes: no animations during background data refresh. */
public final class UiMotion {
    private UiMotion(){}
    public static void reveal(View view){
        if(view==null||!ValueAnimator.areAnimatorsEnabled())return;
        view.animate().cancel();
        view.setAlpha(0.91f);
        view.animate().alpha(1f).setDuration(140).start();
    }
}
