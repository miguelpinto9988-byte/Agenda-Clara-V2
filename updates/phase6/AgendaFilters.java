package pe.agendaclara.app;
import java.text.Normalizer;
import java.time.*;
import java.util.Locale;

/** Pure presentation selection; no database or Android UI dependency. */
public final class AgendaFilters {
    private AgendaFilters(){}
    public static String searchKey(String text){
        String value=Normalizer.normalize(text==null?"":text,Normalizer.Form.NFD);
        return value.replaceAll("\\p{M}+","").toLowerCase(Locale.ROOT).trim();
    }
    public static boolean matches(Task task,int statusFilter,int categoryFilter,String search,LocalDate selectedDay,long now){
        if(task==null)return false;
        if(selectedDay!=null){
            if(task.due<=0||!Instant.ofEpochMilli(task.due).atZone(ZoneId.systemDefault()).toLocalDate().equals(selectedDay))return false;
            return true;
        }
        if(categoryFilter>0){
            if(categoryFilter>TaskOrganization.CATEGORIES.length)return false;
            if(!TaskOrganization.CATEGORIES[categoryFilter-1].equals(TaskOrganization.category(task.category)))return false;
        }
        String status=TaskLogic.status(task,now);
        switch(statusFilter){
            case 1:if(!("Urgente".equals(status)||"Vencida".equals(status)))return false;break;
            case 2:if(!("Pendiente".equals(status)||"Sin fecha".equals(status)))return false;break;
            case 3:if(!"Próxima".equals(status))return false;break;
            case 4:if(!task.done)return false;break;
            default:break;
        }
        String keyword=searchKey(search);
        return keyword.isEmpty()||searchKey(task.title+" "+task.notes+" "+task.source).contains(keyword);
    }
}
