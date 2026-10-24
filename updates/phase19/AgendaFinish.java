package pe.agendaclara.app;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.graphics.Typeface;
import android.content.Context;
import android.widget.TextView;
import android.view.View;

/** Shared visual finishing tokens. Does not override accessibility font scaling. */
public final class AgendaFinish {
    private AgendaFinish(){}
    public static final int INK=0xff182b52, MUTED=0xff627391, BLUE=0xff2765f5;
    public static GradientDrawable surface(Context context,int radiusDp){
        float density=context.getResources().getDisplayMetrics().density;
        GradientDrawable d=new GradientDrawable(GradientDrawable.Orientation.TL_BR,
            new int[]{Color.WHITE,0xfff7faff,0xffedf4ff});
        d.setCornerRadius(radiusDp*density);
        d.setStroke(Math.max(1,Math.round(density)),0xffdce7f9);
        return d;
    }
    public static void heading(TextView view){
        view.setTextColor(INK);
        view.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        view.setLetterSpacing(-.012f);
        view.setIncludeFontPadding(false);
    }
    public static void secondary(TextView view){
        view.setTextColor(MUTED);
        view.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL));
        view.setLetterSpacing(.005f);
    }
    public static void elevate(View view,float dp){
        float density=view.getResources().getDisplayMetrics().density;
        view.setElevation(dp*density);
    }
}
