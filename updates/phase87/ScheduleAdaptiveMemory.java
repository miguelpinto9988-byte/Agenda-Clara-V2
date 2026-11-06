package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

/** Persistent private on-device feedback, with an explicit erase and pause control.
 * Stores ONLY confirmed course names/decisions, never photos or OCR page text.
 * Does not require Internet or any Android runtime permissions.
 */
public final class ScheduleAdaptiveMemory {
    private ScheduleAdaptiveMemory(){}
    private static final String FILE="agenda_clara_adaptive_photo_v1";
    private static final String RULES="confirmed_pairs";
    private static final String ON="enabled";
    private static SharedPreferences pref(Context context){
        return context.getApplicationContext().getSharedPreferences(FILE,Context.MODE_PRIVATE);
    }
    public static boolean enabled(Context context){return pref(context).getBoolean(ON,true);}
    public static void setEnabled(Context context,boolean value){
        if(!pref(context).edit().putBoolean(ON,value).commit())
            throw new IllegalStateException("No se pudo guardar la preferencia");
    }
    public static synchronized List<ScheduleAdaptiveRules.Rule> all(Context context){
        ArrayList<ScheduleAdaptiveRules.Rule> result=new ArrayList<>();
        try{
            JSONArray arr=new JSONArray(pref(context).getString(RULES,"[]"));
            for(int n=0;n<Math.min(arr.length(),ScheduleAdaptiveRules.MAX_RULES);n++){
                JSONObject obj=arr.getJSONObject(n);
                String a=obj.getString("a"), b=obj.getString("b");
                if(ScheduleAdaptiveRules.pairKey(a,b).isEmpty())continue;
                result.add(new ScheduleAdaptiveRules.Rule(
                    a,b,obj.getBoolean("same"),obj.optString("name",""),
                    Math.max(1,obj.optInt("count",1)),obj.optLong("when",0)));
            }
        }catch(Exception error){
            // Do NOT silently overwrite a damaged history on the next confirmation.
            throw new IllegalStateException("El registro adaptativo no se puede leer",error);
        }
        return result;
    }
    public static synchronized ScheduleAdaptiveRules.Rule find(
            Context context,String left,String right){
        if(!enabled(context))return null;
        return ScheduleAdaptiveRules.find(all(context),left,right);
    }
    private static void save(Context context,List<ScheduleAdaptiveRules.Rule> records){
        JSONArray array=new JSONArray();
        try{
            for(ScheduleAdaptiveRules.Rule r:records){
                JSONObject obj=new JSONObject();
                obj.put("a",r.left);obj.put("b",r.right);
                obj.put("same",r.together);obj.put("name",r.canonical);
                obj.put("count",r.confirmations);obj.put("when",r.updatedAt);
                array.put(obj);
            }
        }catch(Exception failure){throw new IllegalStateException("No se pudo serializar la memoria",failure);}
        if(!pref(context).edit().putString(RULES,array.toString()).commit())
            throw new IllegalStateException("No se pudo guardar la memoria adaptativa");
    }
    /** Learning happens only after a real confirmed/committed import or manual correction. */
    public static synchronized void remember(Context c,String left,String right,
                                              boolean together,String canonical){
        if(!enabled(c))return;
        List<ScheduleAdaptiveRules.Rule> after=ScheduleAdaptiveRules.record(
            all(c),left,right,together,canonical,System.currentTimeMillis());
        save(c,after);
    }
    public static synchronized void forget(Context c,String left,String right){
        String key=ScheduleAdaptiveRules.pairKey(left,right);
        ArrayList<ScheduleAdaptiveRules.Rule> kept=new ArrayList<>();
        for(ScheduleAdaptiveRules.Rule r:all(c))
            if(!ScheduleAdaptiveRules.pairKey(r.left,r.right).equals(key))kept.add(r);
        save(c,kept);
    }
    public static synchronized void clear(Context c){
        save(c,new ArrayList<>());
    }
}