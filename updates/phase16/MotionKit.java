package pe.agendaclara.app;
import android.animation.ValueAnimator;
import android.view.View;
import android.view.animation.DecelerateInterpolator;

/** Shared native-view motion for Agenda Clara; no external assets. */
public final class MotionKit {
    private MotionKit(){}
    public static final long FAST=140L, NORMAL=240L, EXPAND=300L, STAGGER=48L;
    public static boolean enabled(){return ValueAnimator.areAnimatorsEnabled();}
    public static void enter(View view, int index){
        if(view==null)return;
        view.animate().cancel();
        if(!enabled()){view.setAlpha(1f);view.setTranslationX(0f);view.setTranslationY(0f);return;}
        float density=view.getResources().getDisplayMetrics().density;
        view.setAlpha(0f);view.setTranslationY(12f*density);
        view.animate().alpha(1f).translationY(0f).setStartDelay(index*STAGGER)
            .setDuration(NORMAL).setInterpolator(new DecelerateInterpolator()).start();
    }
    public static void expand(View view){
        if(view==null)return;
        view.animate().cancel();view.setVisibility(View.VISIBLE);
        if(!enabled()){view.setAlpha(1f);view.setTranslationY(0f);return;}
        float density=view.getResources().getDisplayMetrics().density;
        view.setAlpha(0f);view.setTranslationY(-12f*density);
        view.animate().alpha(1f).translationY(0f).setDuration(EXPAND)
            .setInterpolator(new DecelerateInterpolator()).start();
    }
    public static void collapse(View view){
        if(view==null)return;
        view.animate().cancel();
        if(!enabled()){view.setVisibility(View.GONE);view.setAlpha(1f);view.setTranslationY(0f);return;}
        view.animate().alpha(0f).translationY(-8f*view.getResources().getDisplayMetrics().density)
            .setDuration(FAST).withEndAction(()->{
                view.setVisibility(View.GONE);view.setAlpha(1f);view.setTranslationY(0f);
            }).start();
    }
    public static void press(View view){
        if(view==null||!enabled())return;
        view.animate().cancel();view.animate().scaleX(.94f).scaleY(.94f).setDuration(FAST/2)
            .withEndAction(()->view.animate().scaleX(1f).scaleY(1f).setDuration(NORMAL)
                .setInterpolator(new DecelerateInterpolator()).start()).start();
    }
}
