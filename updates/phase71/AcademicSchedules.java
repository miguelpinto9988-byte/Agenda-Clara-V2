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

/** Persists up to ten distinct schedule profiles and their corresponding task categories.
 * Session records are in ScheduleDatabase v2, addressed by the stable profile UUID.
 */
public final class AcademicSchedules {
    public static final int LIMIT = 10;
    private static final String PREF = "agenda_clara_academic_schedules_v1";
    private static final String KEY = "profiles";
    private static final String SELECTED = "selected";
    private AcademicSchedules() {}

    public static final class Profile {
        public final String id, name, category;
        public final List<String> courses;
        public final boolean legacy;
        Profile(String id,String name,String category,List<String> courses,boolean legacy){
            this.id=id;this.name=name;this.category=category;
            this.courses=uniqueCourses(courses);this.legacy=legacy;
        }
    }

    private static SharedPreferences prefs(Context c){
        return c.getApplicationContext().getSharedPreferences(PREF,Context.MODE_PRIVATE);
    }
    public static String key(String raw){
        if(raw==null)return "";
        return Normalizer.normalize(raw.trim(),Normalizer.Form.NFD)
                .replaceAll("\\p{M}+","").toLowerCase(Locale.ROOT)
                .replaceAll("\\s+"," ");
    }
    public static List<String> uniqueCourses(List<String> items){
        ArrayList<String> out=new ArrayList<>();LinkedHashSet<String> seen=new LinkedHashSet<>();
        if(items!=null)for(String raw:items){
            if(raw==null)continue;
            String value=raw.trim().replaceAll("\\s+"," ");
            if(!value.isEmpty()&&seen.add(key(value)))out.add(value);
        }
        return out;
    }
    public static synchronized List<Profile> all(Context c){
        ArrayList<Profile> out=new ArrayList<>();
        try{
            JSONArray list=new JSONArray(prefs(c).getString(KEY,"[]"));
            for(int i=0;i<list.length();i++){
                JSONObject p=list.getJSONObject(i);
                ArrayList<String> courses=new ArrayList<>();
                JSONArray names=p.optJSONArray("courses");
                if(names!=null)for(int j=0;j<names.length();j++)courses.add(names.optString(j));
                String name=p.getString("name");
                out.add(new Profile(p.getString("id"),name,p.optString("category",name),
                        courses,p.optBoolean("legacy",false)));
            }
        }catch(Exception e){throw new IllegalStateException("Registro de horarios ilegible; no se sobrescribirá",e);}
        return out;
    }
    private static void save(Context c,List<Profile> profiles){
        JSONArray items=new JSONArray();
        try{
            for(Profile p:profiles){
                JSONObject o=new JSONObject();
                o.put("id",p.id);o.put("name",p.name);o.put("category",p.category);
                o.put("legacy",p.legacy);
                JSONArray names=new JSONArray();for(String course:p.courses)names.put(course);
                o.put("courses",names);items.put(o);
            }
        }catch(Exception e){throw new IllegalStateException("No se pudo serializar los horarios",e);}
        if(!prefs(c).edit().putString(KEY,items.toString()).commit())
            throw new IllegalStateException("No se pudo guardar el registro");
    }
    private static String validTitle(String raw){
        String name=raw==null?"":raw.trim().replaceAll("\\s+"," ");
        if(name.length()<2||name.length()>90||name.matches("(?s).*\\p{Cntrl}.*"))
            throw new IllegalArgumentException("Usa un nombre de entre 2 y 90 caracteres");
        return name;
    }
    private static String categoryProposal(Context c,String title,String except){
        String base=title.length()>28?title.substring(0,28).trim():title;
        ArrayList<String> occupied=new ArrayList<>();
        for(CategoryRegistry.Entry item:CategoryRegistry.all(c))
            if(except==null||!key(item.name).equals(key(except)))occupied.add(key(item.name));
        for(int suffix=1;suffix<=100;suffix++){
            String trailing=suffix==1?"":" "+suffix;
            String first=base.substring(0,Math.min(base.length(),28-trailing.length())).trim();
            String attempt=first+trailing;
            if(!attempt.equalsIgnoreCase("General")&&!occupied.contains(key(attempt)))
                return attempt;
        }
        throw new IllegalStateException("No hay un nombre de categoría disponible");
    }
    public static synchronized Profile find(Context c,String id){
        if(id!=null)for(Profile p:all(c))if(p.id.equals(id))return p;
        return null;
    }
    public static synchronized String activeId(Context c){
        String chosen=prefs(c).getString(SELECTED,"");
        if(find(c,chosen)!=null)return chosen;
        List<Profile> profiles=all(c);
        return profiles.isEmpty()?"":profiles.get(0).id;
    }
    public static synchronized void activate(Context c,String id){
        if(find(c,id)==null)throw new IllegalArgumentException("Horario desconocido");
        if(!prefs(c).edit().putString(SELECTED,id).commit())
            throw new IllegalStateException("No se pudo seleccionar el horario");
    }
    public static synchronized Profile create(Context c,String raw,List<String> courses){
        String name=validTitle(raw);
        List<Profile> current=all(c);
        if(current.size()>=LIMIT)throw new IllegalStateException("Límite de diez horarios alcanzado");
        for(Profile p:current)if(key(p.name).equals(key(name)))
            throw new IllegalArgumentException("Ya existe un horario con ese nombre");
        String category=categoryProposal(c,name,null);
        if(!CategoryRegistry.save(c,null,category,CategoryRegistry.COLORS[1],"other"))
            throw new IllegalStateException("No se pudo crear la categoría; verifica el límite de categorías");
        Profile created=new Profile(UUID.randomUUID().toString(),name,category,courses,false);
        try{
            current.add(created);save(c,current);activate(c,created.id);
            return created;
        }catch(RuntimeException err){
            CategoryRegistry.delete(c,category);throw err;
        }
    }
    public static synchronized void rename(Context c,String id,String raw){
        String title=validTitle(raw);
        List<Profile> profiles=all(c);
        Profile selected=find(c,id);
        if(selected==null)throw new IllegalArgumentException("Horario no encontrado");
        for(Profile p:profiles)if(!p.id.equals(id)&&key(p.name).equals(key(title)))
            throw new IllegalArgumentException("Ya existe un horario con ese nombre");
        String category=selected.category;
        if(!key(selected.name).equals(key(title))){
            String desired=categoryProposal(c,title,selected.category);
            if(!CategoryRegistry.save(c,selected.category,desired,
                    CategoryRegistry.color(c,selected.category),CategoryRegistry.icon(c,selected.category)))
                throw new IllegalStateException("No se pudo cambiar la categoría");
            category=desired;
        }
        for(int i=0;i<profiles.size();i++){
            Profile p=profiles.get(i);
            if(p.id.equals(id)){profiles.set(i,new Profile(p.id,title,category,p.courses,p.legacy));break;}
        }
        save(c,profiles);
    }
    public static synchronized void setCourses(Context c,String id,List<String> courses){
        List<Profile> profiles=all(c);
        boolean found=false;
        for(int i=0;i<profiles.size();i++){
            Profile p=profiles.get(i);
            if(p.id.equals(id)){
                profiles.set(i,new Profile(p.id,p.name,p.category,courses,p.legacy));
                found=true;break;
            }
        }
        if(!found)throw new IllegalArgumentException("Horario no encontrado");
        save(c,profiles);
    }
    public static synchronized void syncFromSessions(Context c,String id){
        Profile p=find(c,id);
        if(p==null)return;
        ArrayList<String> names=new ArrayList<>(p.courses);
        for(ScheduleEntry s:ScheduleDatabase.get(c).all(id))names.add(s.course);
        setCourses(c,id,uniqueCourses(names));
    }
    /** Upgrade legacy rows without deleting or resetting any preexisting sessions. */
    public static synchronized void migrateLegacy(Context c){
        List<ScheduleEntry> unassigned=ScheduleDatabase.get(c).all("");
        if(unassigned.isEmpty())return;
        List<Profile> profiles=all(c);
        Profile target=null;
        for(Profile p:profiles)if(p.legacy){target=p;break;}
        if(target==null){
            ArrayList<String> names=new ArrayList<>();
            for(ScheduleEntry s:unassigned)names.add(s.course);
            target=create(c,"Mi horario anterior",names);
            profiles=all(c);
            for(int i=0;i<profiles.size();i++){
                Profile p=profiles.get(i);
                if(p.id.equals(target.id)){
                    profiles.set(i,new Profile(p.id,p.name,p.category,p.courses,true));break;
                }
            }
            save(c,profiles);
        }
        ScheduleDatabase.get(c).assignUnassigned(target.id);
        syncFromSessions(c,target.id);
    }
    /** Explicit destructive action, only after a UI confirmation. */
    public static synchronized void deleteConfirmed(Context c,String id){
        Profile target=find(c,id);
        if(target==null)throw new IllegalArgumentException("Horario no encontrado");
        for(ScheduleEntry s:ScheduleDatabase.get(c).all(id))ScheduleReminders.cancel(c,s.id);
        ScheduleDatabase.get(c).deleteProfile(id);
        List<Profile> profiles=all(c);
        for(int i=profiles.size()-1;i>=0;i--)if(profiles.get(i).id.equals(id))profiles.remove(i);
        save(c,profiles);
        CategoryRegistry.delete(c,target.category); // Reassign dependent tasks/notes to General.
        String next=profiles.isEmpty()?"":profiles.get(0).id;
        prefs(c).edit().putString(SELECTED,next).apply();
    }
}
