package pe.agendaclara.app;
import android.content.Context;
import android.content.res.Configuration;
import android.widget.RemoteViews;

/** Per-widget theme support; preserves the approved day-widget PNG illustrations. */
public final class AcademicWidgetTheme {
    private AcademicWidgetTheme(){}
    private static boolean isDark(Context c,String choice){
        return "dark".equals(choice)||("system".equals(choice)&&
            (c.getResources().getConfiguration().uiMode&
             Configuration.UI_MODE_NIGHT_MASK)==Configuration.UI_MODE_NIGHT_YES);
    }
    public static void apply(Context c,RemoteViews views,int rootId,int[] textIds,
                             int[] mutedIds,String choice){
        boolean dark=isDark(c,choice);
        views.setInt(rootId,"setBackgroundResource",
            dark?R.drawable.widget_academic_background_dark:R.drawable.widget_academic_background);
        for(int id:textIds)views.setTextColor(id,dark?0xffF0F5FF:0xff182746);
        for(int id:mutedIds)views.setTextColor(id,dark?0xffB9C7E7:0xff536583);
    }
    public static void applyDay(Context c,RemoteViews v,String choice){
        boolean dark=isDark(c,choice);
        v.setInt(R.id.academic_day_root,"setBackgroundResource",
            dark?R.drawable.ac_day_shell_dark:R.drawable.ac_day_shell);
        v.setInt(R.id.academic_day_card_1,"setBackgroundResource",
            dark?R.drawable.ac_day_card_lilac_dark:R.drawable.ac_day_card_lilac);
        v.setInt(R.id.academic_day_card_2,"setBackgroundResource",
            dark?R.drawable.ac_day_card_mint_dark:R.drawable.ac_day_card_mint);
        int primary=dark?0xffF7F0FF:0xff111A49,secondary=dark?0xffE7DDF9:0xff46527C;
        for(int id:new int[]{R.id.academic_day_course,R.id.academic_day_course_2,
            R.id.academic_day_tasks_label,R.id.academic_day_cta})v.setTextColor(id,primary);
        for(int id:new int[]{R.id.academic_day_time,R.id.academic_day_time_2,
            R.id.academic_day_room,R.id.academic_day_room_2,
            R.id.academic_day_tasks})v.setTextColor(id,secondary);
        v.setTextColor(R.id.academic_day_heading,0xff101947);
        v.setTextColor(R.id.academic_day_profile,0xff36335E);
        v.setTextColor(R.id.academic_day_date,0xff36335E);
    }
}