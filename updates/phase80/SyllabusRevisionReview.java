package pe.agendaclara.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Local-only syllabus revision review. Does not delete or reschedule existing tasks. */
public final class SyllabusRevisionReview {
    private SyllabusRevisionReview(){}
    private static final String PREFS="academic_syllabus_revision_v1";
    private static String key(String profileId,String document){
        try{
            String raw=profileId+"|"+SyllabusReviewIntelligence.fold(document);
            byte[] hash=MessageDigest.getInstance("SHA-256").digest(raw.getBytes("UTF-8"));
            StringBuilder key=new StringBuilder();
            for(byte b:hash)key.append(String.format(java.util.Locale.ROOT,"%02x",b&255));
            return key.toString();
        }catch(Exception ex){throw new IllegalStateException(ex);}
    }
    private static Map<String,String> snapshot(List<SyllabusEventParser.Event> events){
        Map<String,String> values=new HashMap<>();
        for(SyllabusEventParser.Event e:events){
            if(e==null)continue;
            String title=SyllabusRevisionComparator.identity(e.title);
            if(title.isEmpty())continue;
            int week=SyllabusReviewIntelligence.week(e.sourceText);
            values.put(title,(e.date==null?"Fecha pendiente":e.date.toString())+
                    (week>0?" · Semana "+week:""));
        }
        return values;
    }
    public static void review(Activity activity,String profileId,String document,
                              List<SyllabusEventParser.Event> events,Runnable accepted){
        String previous=activity.getSharedPreferences(PREFS,Context.MODE_PRIVATE)
                .getString(key(profileId,document),null);
        if(previous==null){accepted.run();return;}
        List<SyllabusRevisionComparator.Change> changes=SyllabusRevisionComparator.compare(
                SyllabusRevisionComparator.parse(previous),snapshot(events));
        if(changes.isEmpty()){accepted.run();return;}
        StringBuilder details=new StringBuilder();
        for(SyllabusRevisionComparator.Change c:changes){
            if(details.length()>900){details.append("\n…");break;}
            details.append("\n• ").append(c.status).append(": ").append(c.title);
            if(!c.previousDate.isEmpty())details.append("\n  Antes: ").append(c.previousDate);
            if(!c.newDate.isEmpty())details.append("\n  Ahora: ").append(c.newDate);
        }
        new AlertDialog.Builder(activity,R.style.DialogTheme)
                .setTitle("Cambios en el sílabo")
                .setMessage("Se detectaron diferencias respecto a la última importación "+
                        "de este documento y horario. Los eventos anteriores no se borrarán "+
                        "ni modificarán automáticamente."+details)
                .setNegativeButton("Volver a revisar",null)
                .setPositiveButton("Continuar con nuevas tareas",(d,w)->accepted.run())
                .show();
    }
    public static void record(Context context,String profileId,String document,
                              List<SyllabusEventParser.Event> events){
        context.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit()
                .putString(key(profileId,document),
                        SyllabusRevisionComparator.serialize(snapshot(events))).apply();
    }
}
