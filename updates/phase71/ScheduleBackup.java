package pe.agendaclara.app;

import android.content.Context;
import android.net.Uri;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Password-protected timetable backup v2. V1 files remain importable.
 * v2 includes schedule profiles, separate courses and stable per-session profile IDs.
 */
public final class ScheduleBackup {
    private static final int MAX_FILE=1024*1024,MAX_CLASSES=1500;
    private ScheduleBackup(){}

    public static byte[] exportBytes(Context context)throws Exception{
        AcademicSchedules.migrateLegacy(context);
        JSONArray rows=new JSONArray();
        List<ScheduleEntry> classes=ScheduleDatabase.get(context).all();
        if(classes.size()>MAX_CLASSES)throw new IOException("Máximo 1500 clases por copia.");
        for(ScheduleEntry s:classes){
            if(s.scheduleId==null||s.scheduleId.isEmpty())
                throw new IOException("Hay sesiones sin asignar. Abre Plan de estudio y repite.");
            rows.put(new JSONObject().put("scheduleId",s.scheduleId)
                    .put("course",s.course).put("day",s.day).put("start",s.start)
                    .put("end",s.end).put("room",s.room).put("teacher",s.teacher)
                    .put("notes",s.notes).put("color",s.color).put("reminder",s.reminder)
                    .put("enabled",s.enabled));
        }
        JSONArray profiles=new JSONArray();
        for(AcademicSchedules.Profile p:AcademicSchedules.all(context)){
            JSONArray courses=new JSONArray();
            for(String course:p.courses)courses.put(course);
            profiles.put(new JSONObject().put("id",p.id).put("name",p.name)
                    .put("category",p.category).put("courses",courses));
        }
        android.content.SharedPreferences prefs=context.getSharedPreferences("schedule_settings",0);
        JSONObject backup=new JSONObject().put("format","agenda-clara-class-schedule")
                .put("schema",2).put("profiles",profiles).put("sessions",rows)
                .put("semesterStart",prefs.getString("semester_start",""))
                .put("semesterEnd",prefs.getString("semester_end",""));
        byte[] raw=backup.toString().getBytes(StandardCharsets.UTF_8);
        if(raw.length>MAX_FILE)throw new IOException("La copia supera 1 MB.");
        return raw;
    }

    public static int importBytes(Context context,byte[] bytes)throws Exception{
        if(bytes==null||bytes.length>MAX_FILE)
            throw new IOException("Archivo de horario demasiado grande.");
        JSONObject root=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
        int schema=root.optInt("schema",0);
        if(!"agenda-clara-class-schedule".equals(root.optString("format"))
                ||(schema!=1&&schema!=2))
            throw new IOException("Copia de horario incompatible.");
        JSONArray rows=root.getJSONArray("sessions");
        if(rows.length()>MAX_CLASSES)throw new IOException("Demasiadas clases.");
        String from=root.optString("semesterStart","");
        String until=root.optString("semesterEnd","");
        java.time.LocalDate begin=from.isEmpty()?null:java.time.LocalDate.parse(from);
        java.time.LocalDate end=until.isEmpty()?null:java.time.LocalDate.parse(until);
        if(begin!=null&&end!=null&&begin.isAfter(end))
            throw new IOException("Periodo académico inválido.");

        ArrayList<ScheduleEntry> classes=new ArrayList<>();
        for(int i=0;i<rows.length();i++){
            JSONObject item=rows.getJSONObject(i);
            ScheduleEntry s=new ScheduleEntry();
            s.course=item.getString("course");s.day=item.getInt("day");
            s.start=item.getInt("start");s.end=item.getInt("end");
            s.room=item.optString("room","");s.teacher=item.optString("teacher","");
            s.notes=item.optString("notes","");s.color=item.optInt("color",ScheduleEntry.COLORS[0]);
            s.reminder=item.optInt("reminder",10);s.enabled=item.optBoolean("enabled",true);
            s.scheduleId=item.optString("scheduleId","");
            if(!ScheduleEntry.valid(s)||!(s.reminder==0||s.reminder==5||s.reminder==10||
                    s.reminder==15||s.reminder==30||s.reminder==60))
                throw new IOException("Clase inválida en fila "+(i+1));
            classes.add(s);
        }

        AcademicSchedules.migrateLegacy(context);
        Map<String,String> identity=new HashMap<>();
        Map<String,List<String>> importedCourses=new HashMap<>();
        ArrayList<String[]> missing=new ArrayList<>();
        if(schema==2){
            JSONArray profiles=root.getJSONArray("profiles");
            if(profiles.length()>AcademicSchedules.LIMIT)
                throw new IOException("La copia supera diez horarios.");
            HashSet<String> seen=new HashSet<>();
            List<AcademicSchedules.Profile> existing=AcademicSchedules.all(context);
            for(int i=0;i<profiles.length();i++){
                JSONObject p=profiles.getJSONObject(i);
                String sourceId=p.getString("id"),name=p.getString("name");
                JSONArray courseNames=p.optJSONArray("courses");
                if(courseNames!=null&&courseNames.length()>300)
                    throw new IOException("Demasiados cursos en un horario");
                ArrayList<String> courseList=new ArrayList<>();
                if(courseNames!=null)for(int j=0;j<courseNames.length();j++){
                    String course=courseNames.optString(j,"").trim();
                    if(course.length()>120)throw new IOException("Nombre de curso inválido");
                    courseList.add(course);
                }
                importedCourses.put(sourceId,AcademicSchedules.uniqueCourses(courseList));
                if(sourceId.isEmpty()||!seen.add(sourceId)||name.trim().length()<2
                        ||name.length()>90)
                    throw new IOException("Perfil inválido o repetido");
                AcademicSchedules.Profile matching=null;
                for(AcademicSchedules.Profile current:existing)
                    if(current.id.equals(sourceId)||
                            AcademicSchedules.key(current.name).equals(AcademicSchedules.key(name))){
                        matching=current;break;
                    }
                if(matching!=null)identity.put(sourceId,matching.id);
                else missing.add(new String[]{sourceId,name});
            }
            if(missing.size()+existing.size()>AcademicSchedules.LIMIT)
                throw new IOException("Se excederían los diez horarios al restaurar");
            for(ScheduleEntry s:classes)if(!seen.contains(s.scheduleId))
                throw new IOException("Clase sin perfil en el archivo.");
        }
        // All source data validated before any profile or row is written.
        if(schema==1){
            String active=AcademicSchedules.activeId(context);
            if(active.isEmpty()){
                ArrayList<String> names=new ArrayList<>();
                for(ScheduleEntry s:classes)names.add(s.course);
                active=AcademicSchedules.create(context,"Horario restaurado",names).id;
            }
            identity.put("",active);
        }else{
            for(String[] item:missing){
                AcademicSchedules.Profile created=AcademicSchedules.create(context,item[1],
                        new ArrayList<String>());
                identity.put(item[0],created.id);
            }
        }
        if(schema==2)for(Map.Entry<String,String> link:identity.entrySet()){
            AcademicSchedules.Profile current=AcademicSchedules.find(context,link.getValue());
            if(current!=null){
                ArrayList<String> courses=new ArrayList<>(current.courses);
                List<String> imported=importedCourses.get(link.getKey());
                if(imported!=null)courses.addAll(imported);
                AcademicSchedules.setCourses(context,current.id,AcademicSchedules.uniqueCourses(courses));
            }
        }
        LinkedHashMap<String,List<ScheduleEntry>> grouped=new LinkedHashMap<>();
        for(ScheduleEntry s:classes){
            String id=identity.get(s.scheduleId);
            if(id==null)throw new IOException("Horario desconocido en la copia");
            s.scheduleId=id;
            if(!grouped.containsKey(id))grouped.put(id,new ArrayList<ScheduleEntry>());
            grouped.get(id).add(s);
        }
        int added=0;
        for(Map.Entry<String,List<ScheduleEntry>> e:grouped.entrySet()){
            added+=ScheduleDatabase.get(context).importReviewed(e.getValue(),e.getKey());
            AcademicSchedules.syncFromSessions(context,e.getKey());
        }
        context.getSharedPreferences("schedule_settings",0).edit()
                .putString("semester_start",from)
                .putString("semester_end",until).apply();
        return added;
    }

    public static int exportEncrypted(Context context,Uri uri,char[] password)throws Exception{
        byte[] plain=null,sealed=null;
        try{
            plain=exportBytes(context);sealed=SecureArchive.encrypt(plain,password);
            try(OutputStream out=context.getContentResolver().openOutputStream(uri,"wt")){
                if(out==null)throw new IOException("No se pudo escribir la copia.");
                out.write(sealed);
            }
            return ScheduleDatabase.get(context).all().size();
        }finally{
            if(plain!=null)Arrays.fill(plain,(byte)0);
            if(sealed!=null)Arrays.fill(sealed,(byte)0);
            if(password!=null)Arrays.fill(password,'\0');
        }
    }
    public static int importEncrypted(Context context,Uri uri,char[] password)throws Exception{
        byte[] sealed=null,plain=null;
        try{
            try(InputStream input=context.getContentResolver().openInputStream(uri)){
                if(input==null)throw new IOException("No se pudo leer el archivo.");
                ByteArrayOutputStream out=new ByteArrayOutputStream();
                byte[] buffer=new byte[8192];int n;
                while((n=input.read(buffer))!=-1){
                    if(out.size()+n>MAX_FILE+256)throw new IOException("Archivo demasiado grande.");
                    out.write(buffer,0,n);
                }
                sealed=out.toByteArray();
            }
            plain=SecureArchive.decrypt(sealed,password);
            return importBytes(context,plain);
        }finally{
            if(sealed!=null)Arrays.fill(sealed,(byte)0);
            if(plain!=null)Arrays.fill(plain,(byte)0);
            if(password!=null)Arrays.fill(password,'\0');
        }
    }
}
