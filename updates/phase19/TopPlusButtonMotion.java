package pe.agendaclara.app;

import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
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
            View add = findTopRightAdd(root, activity);
            if (add != null) style(activity, add);
        });
    }

    private static View findTopRightAdd(View root, Activity activity) {
        Rect bounds = new Rect();
        if (!root.getGlobalVisibleRect(bounds)) return null;
        final int maxY = Math.min(bounds.top + dp(activity, 240),
                bounds.top + Math.round(bounds.height() * 0.34f));
        final int minX = bounds.left + Math.round(bounds.width() * 0.54f);
        return search(root, minX, maxY, activity);
    }

    private static View search(View node, int minX, int maxY, Activity activity) {
        if (node.getVisibility() != View.VISIBLE) return null;
        View best = null;
        if (matchesPlus(node)) {
            View clickable = node;
            for (int i = 0; i < 2 && !clickable.isClickable(); i++) {
                if (!(clickable.getParent() instanceof View)) break;
                clickable = (View) clickable.getParent();
            }
            Rect area = new Rect();
            if (clickable.isClickable() && clickable.getGlobalVisibleRect(area)
                    && area.centerX() >= minX && area.centerY() <= maxY
                    && area.width() <= dp(activity, 110)
                    && area.height() <= dp(activity, 110)) {
                best = clickable;
            }
        }
        if (node instanceof ViewGroup) {
            ViewGroup parent = (ViewGroup) node;
            for (int i = 0; i < parent.getChildCount(); i++) {
                View candidate = search(parent.getChildAt(i), minX, maxY, activity);
                if (candidate != null && (best == null || isEarlier(candidate, best))) best = candidate;
            }
        }
        return best;
    }

    private static boolean isEarlier(View a, View b) {
        Rect ar = new Rect(); Rect br = new Rect();
        if (!a.getGlobalVisibleRect(ar) || !b.getGlobalVisibleRect(br)) return false;
        return ar.top < br.top || (ar.top == br.top && ar.centerX() > br.centerX());
    }

    private static boolean matchesPlus(View view) {
        if (view instanceof TextView) {
            String label = String.valueOf(((TextView) view).getText()).trim();
            if ("+".equals(label) || "＋".equals(label) || "✚".equals(label)
                    || "➕".equals(label)) return true;
        }
        if (view instanceof ImageButton) {
            CharSequence desc = view.getContentDescription();
            if (desc != null) {
                String label = desc.toString().trim().toLowerCase(java.util.Locale.ROOT);
                return label.equals("añadir") || label.equals("agregar")
                        || label.equals("nueva tarea") || label.equals("añadir tarea")
                        || label.equals("agregar tarea") || label.equals("crear tarea");
            }
        }
        return false;
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
        if (view instanceof ImageButton) ((ImageButton) view).setImageDrawable(null);
        view.setMinimumWidth(dp(activity, 52));
        view.setMinimumHeight(dp(activity, 52));
        view.setPadding(0, 0, 0, 0);
        if (view.getContentDescription() == null || view.getContentDescription().length() == 0)
            view.setContentDescription("Añadir");
        if (Build.VERSION.SDK_INT >= 26 && !ValueAnimator.areAnimatorsEnabled()) return;
        // Returning false is deliberate: Android dispatches the original click unchanged.
        view.setOnTouchListener((target, event) -> {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    target.animate().cancel();
                    target.animate().scaleX(0.91f).scaleY(0.91f).rotation(-7f)
                            .setDuration(105).start();
                    break;
                case MotionEvent.ACTION_UP:
                    target.animate().cancel();
                    target.animate().scaleX(1.04f).scaleY(1.04f).rotation(45f)
                            .setDuration(170).withEndAction(() -> target.animate()
                                    .scaleX(1f).scaleY(1f).rotation(0f)
                                    .setDuration(170).start()).start();
                    break;
                case MotionEvent.ACTION_CANCEL:
                    target.animate().cancel();
                    target.animate().scaleX(1f).scaleY(1f).rotation(0f)
                            .setDuration(120).start();
                    break;
                default:
                    break;
            }
            return false;
        });
    }

    private static int dp(Activity activity, float value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
