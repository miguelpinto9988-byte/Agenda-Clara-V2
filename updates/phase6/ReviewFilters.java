package pe.agendaclara.app;

/** Filters for opt-in message proposals. No messages are added to tasks here. */
public final class ReviewFilters {
    private ReviewFilters(){}
    public static boolean matches(String title,String source,String original,boolean dateKnown,
                                  long due,boolean historical,int mode,String search,long now){
        switch(mode){
            case 1:if(dateKnown)return false;break;
            case 2:if(!dateKnown||due<=0||due>=now)return false;break;
            case 3:if(!historical)return false;break;
            case 4:if(!dateKnown||due<now||due>now+7L*86400000L)return false;break;
            default:break;
        }
        String keyword=AgendaFilters.searchKey(search);
        return keyword.isEmpty()||AgendaFilters.searchKey(title+" "+source+" "+original).contains(keyword);
    }
}
