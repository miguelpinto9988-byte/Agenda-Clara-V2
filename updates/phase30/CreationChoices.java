package pe.agendaclara.app;

import android.animation.ValueAnimator;
import android.app.Activity;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

/** Two floating creation actions attached to the existing approved header + image. */
public final class CreationChoices {
    private CreationChoices(){}
    private static int dp(Activity a,int n){return UiDesign.dp(a,n);}
    public static void show(MainActivity a,View anchor,Runnable taskAction,Runnable noteAction){
        if(anchor==null||!anchor.isAttachedToWindow())return;
        LinearLayout floating=new LinearLayout(a);
        floating.setOrientation(LinearLayout.VERTICAL);
        floating.setPadding(dp(a,10),dp(a,12),dp(a,10),dp(a,12));
        LinearLayout task=choice(a,"Nueva tarea","Registrar una actividad","save");
        LinearLayout note=choice(a,"Nueva nota","Nota adhesiva con fecha","sticky_note");
        LinearLayout.LayoutParams top=new LinearLayout.LayoutParams(-1,dp(a,72));
        top.bottomMargin=dp(a,7);
        floating.addView(task,top);
        floating.addView(note,new LinearLayout.LayoutParams(-1,dp(a,72)));
        PopupWindow menu=new PopupWindow(floating,dp(a,246),-2,true);
        menu.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        menu.setElevation(dp(a,12));menu.setOutsideTouchable(true);
        task.setOnClickListener(v->{menu.dismiss();taskAction.run();});
        note.setOnClickListener(v->{menu.dismiss();noteAction.run();});
        // The menu aligns with the right edge of the top + and never touches the bottom tabs.
        menu.showAsDropDown(anchor,-dp(a,138),-dp(a,4),Gravity.END);
        if(ValueAnimator.areAnimatorsEnabled()){
            floating.setAlpha(0f);floating.setTranslationY(-dp(a,12));
            floating.animate().alpha(1f).translationY(0).setDuration(190).start();
        }
    }
    private static LinearLayout choice(Activity a,String title,String subtitle,String iconName){
        LinearLayout row=new LinearLayout(a);row.setGravity(Gravity.CENTER_VERTICAL);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(dp(a,12),dp(a,9),dp(a,12),dp(a,9));
        GradientDrawable back=UiDesign.shape(a,0xffffffff,18,UiDesign.BORDER);
        row.setBackground(back);row.setElevation(dp(a,5));
        ImageView icon=ApprovedPng.view(a,iconName,34);
        row.addView(icon,new LinearLayout.LayoutParams(dp(a,40),dp(a,40)));
        LinearLayout details=new LinearLayout(a);details.setOrientation(1);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.leftMargin=dp(a,10);
        TextView main=new TextView(a);main.setText(title);main.setTextSize(16);main.setTextColor(UiDesign.INK);UiDesign.text(main,true);
        TextView sub=new TextView(a);sub.setText(subtitle);sub.setTextSize(11);sub.setTextColor(UiDesign.MUTED);UiDesign.text(sub,true);
        details.addView(main);details.addView(sub);row.addView(details,lp);
        TextView chevron=new TextView(a);chevron.setText("›");chevron.setTextSize(24);
        chevron.setTextColor(UiDesign.BLUE);UiDesign.text(chevron,true);
        row.addView(chevron);row.setContentDescription(title);row.setClickable(true);row.setFocusable(true);
        return row;
    }
}
