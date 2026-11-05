package pe.agendaclara.app;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Pure comparison engine: never edits existing tasks automatically. */
public final class SyllabusRevisionComparator {
    private SyllabusRevisionComparator(){}
    public static final class Change {
        public final String title,previousDate,newDate,status;
        public Change(String title,String previousDate,String newDate,String status){
            this.title=title;this.previousDate=previousDate;
            this.newDate=newDate;this.status=status;
        }
    }
    public static String identity(String title){
        return SyllabusReviewIntelligence.fold(title).replaceAll("[^a-z0-9 ]","")
                .replaceAll(" +"," ").trim();
    }
    public static List<Change> compare(Map<String,String> previous,Map<String,String> next){
        ArrayList<Change> changes=new ArrayList<>();
        for(Map.Entry<String,String> row:next.entrySet()){
            String before=previous.get(row.getKey());
            if(before==null)changes.add(new Change(row.getKey(),"",row.getValue(),"NUEVA"));
            else if(!before.equals(row.getValue()))
                changes.add(new Change(row.getKey(),before,row.getValue(),"CAMBIO"));
        }
        for(Map.Entry<String,String> row:previous.entrySet()){
            if(!next.containsKey(row.getKey()))
                changes.add(new Change(row.getKey(),row.getValue(),"","AUSENTE"));
        }
        return changes;
    }
    public static Map<String,String> parse(String serialized){
        Map<String,String> result=new HashMap<>();
        if(serialized==null)return result;
        for(String line:serialized.split("\\n")){
            int split=line.indexOf('\t');
            if(split>0)result.put(line.substring(0,split),line.substring(split+1));
        }
        return result;
    }
    public static String serialize(Map<String,String> data){
        StringBuilder out=new StringBuilder();
        for(Map.Entry<String,String> row:data.entrySet()){
            if(row.getKey().indexOf('\t')>=0||row.getKey().indexOf('\n')>=0)continue;
            if(out.length()>0)out.append('\n');
            out.append(row.getKey()).append('\t').append(row.getValue().replace("\n"," "));
        }
        return out.toString();
    }
}
