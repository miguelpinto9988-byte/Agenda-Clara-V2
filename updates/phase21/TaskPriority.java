package pe.agendaclara.app;

/** Presentation-only delivery priority, derived from due time. No manual flag. */
public final class TaskPriority {
    private TaskPriority(){}
    public static String label(Task task,long now){
        if(task.done)return "Completada";
        if(task.due<=0)return "Sin fecha";
        long remaining=task.due-now;
        if(remaining<0)return "Vencida";
        if(remaining<=86400000L)return "Urgente";
        if(remaining<=3L*86400000L)return "Alta";
        if(remaining<=7L*86400000L)return "Media";
        return "Baja";
    }
    public static int color(String label){
        if("Vencida".equals(label)||"Urgente".equals(label))return 0xffdb4258;
        if("Alta".equals(label))return 0xffd97706;
        if("Media".equals(label))return 0xffab7f13;
        if("Completada".equals(label))return 0xff0d9488;
        return 0xff4359e9;
    }
}
