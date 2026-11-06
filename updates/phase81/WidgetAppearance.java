package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;

/** Per-widget display preferences. Does not alter any academic records. */
public final class WidgetAppearance {
    private static final String PREFS="widget_appearance_v1";
    private WidgetAppearance(){}
    public static final class Settings {
        public final String profileId, theme, density;
        public final boolean hidePrivateTitles;
        public Settings(String profileId,String theme,String density,boolean hidePrivateTitles){
            this.profileId=profileId;this.theme=theme;this.density=density;
            this.hidePrivateTitles=hidePrivateTitles;
        }
    }
    public static Settings read(Context context,int widgetId){
        SharedPreferences p=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE);
        String key="widget_"+widgetId+"_";
        return new Settings(p.getString(key+"profile",""),
                p.getString(key+"theme","system"),p.getString(key+"density","normal"),
                p.getBoolean(key+"privacy",false));
    }
    public static void save(Context context,int widgetId,Settings s){
        if(widgetId<0)throw new IllegalArgumentException("Invalid widget ID");
        String key="widget_"+widgetId+"_";
        context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit()
                .putString(key+"profile",s.profileId)
                .putString(key+"theme",s.theme)
                .putString(key+"density",s.density)
                .putBoolean(key+"privacy",s.hidePrivateTitles).apply();
    }
    public static void remove(Context context,int widgetId){
        String key="widget_"+widgetId+"_";
        SharedPreferences.Editor e=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit();
        for(String field:new String[]{"profile","theme","density","privacy"})
            e.remove(key+field);
        e.apply();
    }
}
