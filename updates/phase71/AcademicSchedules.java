package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * Per-install registry of up to ten academic schedules.
 * Independent of legacy ScheduleDatabase: existing sessions are never deleted.
 * The stable UUID (not the display name) is the category identity.
 */
public final class AcademicSchedules {
    public static final int LIMIT = 10;
    private static final String PREF = "agenda_clara_academic_schedules_v1";
    private static final String KEY = "profiles";
    private AcademicSchedules() {}

    public static final class Profile {
        public final String id;
        public final String name;
        public final List<String> courses;
        public final boolean legacy;
        Profile(String id, String name, List<String> courses, boolean legacy) {
            this.id=id;this.name=name;this.courses=courses;this.legacy=legacy;
        }
    }

    private static SharedPreferences prefs(Context context) {
        return context.getApplicationContext().getSharedPreferences(PREF, Context.MODE_PRIVATE);
    }

    public static String key(String raw) {
        if(raw==null)return "";
        return Normalizer.normalize(raw.trim(), Normalizer.Form.NFD)
                .replaceAll("\\p{M}+", "").toLowerCase(Locale.ROOT)
                .replaceAll("\\s+", " ");
    }

    public static List<String> uniqueCourses(List<String> input) {
        LinkedHashSet<String> keys = new LinkedHashSet<>();
        ArrayList<String> out = new ArrayList<>();
        if(input!=null)for(String course:input) {
            if(course==null)continue;
            String value=course.trim().replaceAll("\\s+"," ");
            if(!value.isEmpty() && keys.add(key(value)))out.add(value);
        }
        return out;
    }

    public static synchronized List<Profile> all(Context context) {
        ArrayList<Profile> out=new ArrayList<>();
        try {
            JSONArray profiles=new JSONArray(prefs(context).getString(KEY,"[]"));
            for(int i=0;i<profiles.length();i++) {
                JSONObject item=profiles.getJSONObject(i);
                JSONArray courses=item.optJSONArray("courses");
                ArrayList<String> names=new ArrayList<>();
                if(courses!=null)for(int j=0;j<courses.length();j++)names.add(courses.optString(j));
                out.add(new Profile(item.getString("id"),item.getString("name"),
                        uniqueCourses(names),item.optBoolean("legacy",false)));
            }
        }catch(Exception e){throw new IllegalStateException("No se pudo leer el registro académico",e);}
        return out;
    }

    private static void save(Context context,List<Profile> profiles) {
        JSONArray array=new JSONArray();
        try {
            for(Profile p:profiles){
                JSONObject o=new JSONObject();
                o.put("id",p.id);o.put("name",p.name);o.put("legacy",p.legacy);
                JSONArray courses=new JSONArray();
                for(String course:p.courses)courses.put(course);
                o.put("courses",courses);array.put(o);
            }
        }catch(Exception e){throw new IllegalStateException(e);}
        if(!prefs(context).edit().putString(KEY,array.toString()).commit())
            throw new IllegalStateException("No se pudieron guardar los horarios");
    }

    public static synchronized Profile create(Context context,String name,List<String> courses) {
        String title=name==null?"":name.trim().replaceAll("\\s+"," ");
        if(title.isEmpty()||title.length()>90)throw new IllegalArgumentException("Nombre de horario no válido");
        List<Profile> profiles=all(context);
        if(profiles.size()>=LIMIT)throw new IllegalStateException("Límite de diez horarios alcanzado");
        for(Profile p:profiles)if(key(p.name).equals(key(title)))
            throw new IllegalArgumentException("Ya existe un horario con ese nombre");
        Profile profile=new Profile(UUID.randomUUID().toString(),title,uniqueCourses(courses),false);
        profiles.add(profile);save(context,profiles);return profile;
    }

    public static synchronized void rename(Context context,String id,String name) {
        String title=name==null?"":name.trim();
        if(title.isEmpty()||title.length()>90)throw new IllegalArgumentException("Nombre no válido");
        List<Profile> profiles=all(context);
        for(Profile p:profiles)if(!p.id.equals(id)&&key(p.name).equals(key(title)))
            throw new IllegalArgumentException("Ya existe ese nombre");
        boolean found=false;
        for(int i=0;i<profiles.size();i++){
            Profile p=profiles.get(i);
            if(p.id.equals(id)){
                profiles.set(i,new Profile(p.id,title,p.courses,p.legacy));found=true;break;
            }
        }
        if(!found)throw new IllegalArgumentException("Horario no encontrado");
        save(context,profiles);
    }

    public static synchronized void setCourses(Context context,String id,List<String> courses) {
        List<Profile> profiles=all(context);boolean found=false;
        for(int i=0;i<profiles.size();i++){
            Profile p=profiles.get(i);
            if(p.id.equals(id)){
                profiles.set(i,new Profile(p.id,p.name,uniqueCourses(courses),p.legacy));
                found=true;break;
            }
        }
        if(!found)throw new IllegalArgumentException("Horario no encontrado");
        save(context,profiles);
    }

    /**
     * Non-destructive migration: create a registry entry for existing schedule sessions.
     * The original schedule rows and reminders stay in ScheduleDatabase.
     */
    public static synchronized void importLegacy(Context context,List<String> courses) {
        List<Profile> profiles=all(context);
        if(!profiles.isEmpty()||courses==null||courses.isEmpty())return;
        List<String> names=uniqueCourses(courses);
        if(names.isEmpty())return;
        Profile profile=new Profile(UUID.randomUUID().toString(),"Mi horario anterior",names,true);
        profiles.add(profile);save(context,profiles);
    }
}
