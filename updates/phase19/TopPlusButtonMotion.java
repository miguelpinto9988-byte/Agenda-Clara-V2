package pe.agendaclara.app;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.StateListAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.view.View;
import android.widget.TextView;

import java.util.Collections;
import java.util.Set;
import java.util.WeakHashMap;

/** Optional visual treatment of the existing top-right add control.
 *  Crucially, its existing OnClickListener and navigation are not replaced.
 */
public final class TopPlusButtonMotion {
    private static final Set<View> STYLED = Collections.newSetFromMap(new WeakHashMap<View, Boolean>());

    private TopPlusButtonMotion() {}

    public static void install(Activity activity) {
        if (activity == null || activity.isFinishing()) return;
        View root = activity.getWindow().getDecorView();
        // Scan only after the current page's layout is complete.
        root.post(() -> {
            if (activity.isFinishing() || (Build.VERSION.SDK_INT >= 17 && activity.isDestroyed())) return;
            View add = findTopRightAdd(root);
            if (add != null) style(activity, add);
        });
    }

    /** Match the original stable tag, not an unrelated plus in the page content. */
    private static View findTopRightAdd(View root) {
        View add = root.findViewWithTag("new_task_button");
        return add != null && add.isShown() && add.isClickable() ? add : null;
    }

    private static void style(Activity activity, View view) {
        synchronized (STYLED) {
            if (!STYLED.add(view)) return;
        }
        Drawable artwork = activity.getResources().getDrawable(R.drawable.ic_top_plus_animated, activity.getTheme());
        GradientDrawable mask = new GradientDrawable();
        mask.setShape(GradientDrawable.OVAL);
        mask.setColor(Color.WHITE);
        RippleDrawable ripple = new RippleDrawable(ColorStateList.valueOf(0x44FFFFFF), artwork, mask);
        view.setBackground(ripple);
        if (view instanceof TextView) ((TextView) view).setText("");
        view.setMinimumWidth(dp(activity, 52));
        view.setMinimumHeight(dp(activity, 52));
        view.setPadding(0, 0, 0, 0);
        if (view.getContentDescription() == null || view.getContentDescription().length() == 0)
            view.setContentDescription("Añadir");
        if (Build.VERSION.SDK_INT >= 26 && !ValueAnimator.areAnimatorsEnabled()) return;
        // Android's native state animator preserves the original click and touch handlers.
        // The released state also restores the transform after touch cancellation.
        StateListAnimator motion = new StateListAnimator();
        motion.addState(new int[] { android.R.attr.state_pressed },
                animate(view, 0.91f, -7f, 105));
        motion.addState(new int[0], animate(view, 1f, 0f, 170));
        view.setStateListAnimator(motion);
    }

    private static AnimatorSet animate(View view, float scale, float rotation, long duration) {
        AnimatorSet motion = new AnimatorSet();
        motion.playTogether(
                ObjectAnimator.ofFloat(view, View.SCALE_X, scale),
                ObjectAnimator.ofFloat(view, View.SCALE_Y, scale),
                ObjectAnimator.ofFloat(view, View.ROTATION, rotation));
        motion.setDuration(duration);
        return motion;
    }

    private static int dp(Activity activity, float value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
