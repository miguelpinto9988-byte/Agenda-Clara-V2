package pe.agendaclara.app;

import android.content.Context;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Two mutually exclusive panels inside the existing Calendario bottom tab. */
public final class CalendarStudyTabs {
    private static final String PREF="agenda_clara_calendar_study";
    private CalendarStudyTabs(){}
    public static void render(MainActivity a){
        AcademicSchedules.migrateLegacy(a);
        int selected=a.getSharedPreferences(PREF,Context.MODE_PRIVATE).getInt("panel",0);
        LinearLayout tabs=a.row();
        tabs.setPadding(a.dp(4),a.dp(5),a.dp(4),a.dp(5));
        tabs.setBackground(a.rounded(0xffeef3ff,18));
        add(a,tabs,"Calendario",0,selected);
        add(a,tabs,"Plan de estudio",1,selected);
        a.body.addView(tabs);
        a.gap(a.body,14);
        if(selected==0)a.calendarPage();
        else {
            CalendarStudyPanel.render(a);
        }
    }
    private static void add(MainActivity a,LinearLayout tabs,String label,int id,int selected){
        TextView item=a.text(label,14,selected==id?0xffffffff:0xff182746,true);
        item.setGravity(Gravity.CENTER);
        item.setMinHeight(a.dp(47));
        item.setBackground(a.rounded(selected==id?0xff3864f4:0xffeef3ff,15));
        item.setFocusable(true);
        item.setContentDescription(label+(selected==id?", pestaña seleccionada":", abrir"));
        item.setOnClickListener(v->{
            a.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putInt("panel",id).apply();
            a.render();
        });
        tabs.addView(item,new LinearLayout.LayoutParams(0,a.dp(48),1));
    }
}
