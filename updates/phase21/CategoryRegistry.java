package pe.agendaclara.app;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.ArrayList;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;

/** Local category catalog. Only General is seeded; prior task categories are migrated. */
public final class CategoryRegistry {
    private static final String KEY="user_categories_v2";
    public static final int[] COLORS={0xff4359e9,0xff7660e7,0xff0d9488,0xfff59e0b,0xffef6574,0xff168dbb,0xff8b5cf6,0xff64748b};
    public static final String[] COLOR_NAMES={"Azul","Violeta","Verde","Ámbar","Coral","Turquesa","Lila","Gris"};
    private CategoryRegistry(){}
    public static final class Entry {
        public final String name;
        public final int color;
        Entry(String name,int color){this.name=name;this.color=color;}
    }
    private static String normalize(String raw) {
        if(raw==null)return "";
        String name=raw.trim().replaceAll("\\s+"," ");
        return name.length()>28||name.matches("(?s).*\\p{Cntrl}.*")?"":name;
    }
    private static boolean has(List<Entry> list,String name) {
        for(Entry e:list)if(e.name.equalsIgnoreCase(name))return true;
        return false;
    }
    private static void store(Context context,List<Entry> list){
        JSONArray array=new JSONArray();
        for(Entry e:list){
            JSONObject object=new JSONObject();
            try{object.put("name",e.name);object.put("color",e.color);array.put(object);}
            catch(org.json.JSONException ignored){}
        }
        Prefs.get(context).edit().putString(KEY,array.toString()).apply();
    }
    public static synchronized List<Entry> all(Context context){
        SharedPreferences prefs=Prefs.get(context);
        ArrayList<Entry> items=new ArrayList<>();
        items.add(new Entry("General",COLORS[0]));
        if(prefs.contains(KEY)){
            try{
                JSONArray array=new JSONArray(prefs.getString(KEY,"[]"));
                for(int i=0;i<array.length()&&items.size()<40;i++){
                    JSONObject record=array.optJSONObject(i);
                    if(record==null)continue;
                    String name=normalize(record.optString("name",""));
                    if(!name.isEmpty()&&!has(items,name))items.add(new Entry(name,record.optInt("color",COLORS[items.size()%COLORS.length])));
                }
            }catch(org.json.JSONException ignored){}
            return items;
        }
        // A one-time migration retains categories already assigned to existing tasks.
        for(Task task:Store.get(context).all()){
            String category=normalize(task.category);
            if(!category.isEmpty()&&!has(items,category)&&items.size()<40)
                items.add(new Entry(category,COLORS[items.size()%COLORS.length]));
        }
        store(context,items);
        return items;
    }
    public static synchronized String[] names(Context c){
        List<Entry> items=all(c);String[] names=new String[items.size()];
        for(int i=0;i<items.size();i++)names[i]=items.get(i).name;
        return names;
    }
    public static synchronized int color(Context c,String name){
        for(Entry e:all(c))if(e.name.equalsIgnoreCase(name))return e.color;
        return COLORS[0];
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color){
        String name=normalize(desired);
        if(name.isEmpty())return false;
        List<Entry> entries=all(c);
        String old=normalize(previous);
        int oldIndex=-1;
        for(int i=0;i<entries.size();i++)if(entries.get(i).name.equalsIgnoreCase(old))oldIndex=i;
        if(oldIndex==0)return false; // General cannot be changed.
        if(oldIndex<0&&entries.size()>=40)return false;
        for(int i=0;i<entries.size();i++)if(i!=oldIndex&&entries.get(i).name.equalsIgnoreCase(name))return false;
        if(oldIndex>0){
            Store.get(c).reassignCategory(entries.get(oldIndex).name,name);
            entries.set(oldIndex,new Entry(name,color));
        }else entries.add(new Entry(name,color));
        store(c,entries);return true;
    }
    public static synchronized boolean delete(Context c,String name){
        List<Entry> entries=all(c);
        for(int i=1;i<entries.size();i++)if(entries.get(i).name.equalsIgnoreCase(name)){
            Store.get(c).reassignCategory(entries.get(i).name,"General");
            entries.remove(i);store(c,entries);return true;
        }
        return false;
    }
}
