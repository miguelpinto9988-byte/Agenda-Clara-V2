package pe.agendaclara.app;

import android.content.Context;
import android.content.res.Configuration;
import android.widget.RemoteViews;

/** Apply per-instance color mode without changing the app's global theme. */
public final class AcademicWidgetTheme {
    private AcademicWidgetTheme(){}
    public static void apply(Context c,RemoteViews views,int rootId,int[] textIds,
                             int[] mutedIds,String choice){
        boolean dark="dark".equals(choice)
                ||("system".equals(choice)
                && (c.getResources().getConfiguration().uiMode&Configuration.UI_MODE_NIGHT_MASK)
                    ==Configuration.UI_MODE_NIGHT_YES);
        views.setInt(rootId,"setBackgroundResource",
                dark?R.drawable.widget_academic_background_dark:
                    R.drawable.widget_academic_background);
        for(int id:textIds)views.setTextColor(id,dark?0xffF0F5FF:0xff182746);
        for(int id:mutedIds)views.setTextColor(id,dark?0xffB9C7E7:0xff536583);
    }
}