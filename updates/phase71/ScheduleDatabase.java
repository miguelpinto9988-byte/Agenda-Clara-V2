package pe.agendaclara.app;

import android.content.*;
import android.database.Cursor;
import android.database.sqlite.*;
import java.util.*;

/** SQLite v2: class sessions belong to exactly one academic schedule profile.
 * V1 sessions are retained with empty profile IDs until explicit safe migration.
 */
public final class ScheduleDatabase extends SQLiteOpenHelper {
    private static volatile ScheduleDatabase instance;
    private final Context appContext;
    public static ScheduleDatabase get(Context c){
        if(instance==null)synchronized(ScheduleDatabase.class){
            if(instance==null)instance=new ScheduleDatabase(c.getApplicationContext());
        }
        return instance;
    }
    private ScheduleDatabase(Context c){
        super(c,"class_schedule.db",null,2);
        appContext=c.getApplicationContext();
    }
    @Override public void onCreate(SQLiteDatabase db){
        db.execSQL("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT,course TEXT NOT NULL,day INTEGER NOT NULL,start_min INTEGER NOT NULL,end_min INTEGER NOT NULL,room TEXT NOT NULL DEFAULT '',teacher TEXT NOT NULL DEFAULT '',notes TEXT NOT NULL DEFAULT '',color INTEGER NOT NULL,reminder INTEGER NOT NULL DEFAULT 10,enabled INTEGER NOT NULL DEFAULT 1,schedule_id TEXT NOT NULL DEFAULT '')");
        db.execSQL("CREATE INDEX IF NOT EXISTS schedule_day_start ON sessions(day,start_min)");
        db.execSQL("CREATE INDEX IF NOT EXISTS schedule_profile_day ON sessions(schedule_id,day,start_min)");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int old,int current){
        if(old<2){
            db.execSQL("ALTER TABLE sessions ADD COLUMN schedule_id TEXT NOT NULL DEFAULT ''");
            db.execSQL("CREATE INDEX IF NOT EXISTS schedule_profile_day ON sessions(schedule_id,day,start_min)");
        }
    }
    private static final String COLUMNS="id,course,day,start_min,end_min,room,teacher,notes,color,reminder,enabled,schedule_id";
    private ScheduleEntry read(Cursor c){
        ScheduleEntry s=new ScheduleEntry();
        s.id=c.getLong(0);s.course=c.getString(1);s.day=c.getInt(2);s.start=c.getInt(3);
        s.end=c.getInt(4);s.room=c.getString(5);s.teacher=c.getString(6);
        s.notes=c.getString(7);s.color=c.getInt(8);s.reminder=c.getInt(9);
        s.enabled=c.getInt(10)!=0;s.scheduleId=c.getString(11);
        return s;
    }
    public synchronized List<ScheduleEntry> all(){
        ArrayList<ScheduleEntry> out=new ArrayList<>();
        try(Cursor c=getReadableDatabase().rawQuery("SELECT "+COLUMNS+
                " FROM sessions ORDER BY day,start_min,course",null)){
            while(c.moveToNext())out.add(read(c));
        }
        return out;
    }
    /** Empty scheduleId selects only unassigned legacy sessions. */
    public synchronized List<ScheduleEntry> all(String scheduleId){
        ArrayList<ScheduleEntry> out=new ArrayList<>();
        if(scheduleId==null)return out;
        try(Cursor c=getReadableDatabase().rawQuery("SELECT "+COLUMNS+
                " FROM sessions WHERE schedule_id=? ORDER BY day,start_min,course",
                new String[]{scheduleId})){
            while(c.moveToNext())out.add(read(c));
        }
        return out;
    }
    public synchronized ScheduleEntry find(long id){
        try(Cursor c=getReadableDatabase().rawQuery("SELECT "+COLUMNS+" FROM sessions WHERE id=?",
                new String[]{Long.toString(id)})){
            return c.moveToFirst()?read(c):null;
        }
    }
    private static boolean allowedReminder(int n){
        return n==0||n==5||n==10||n==15||n==30||n==60;
    }
    private static ContentValues values(ScheduleEntry s){
        ContentValues v=new ContentValues();
        v.put("course",s.course.trim());v.put("day",s.day);v.put("start_min",s.start);
        v.put("end_min",s.end);v.put("room",s.room);v.put("teacher",s.teacher);
        v.put("notes",s.notes);v.put("color",s.color);v.put("reminder",s.reminder);
        v.put("enabled",s.enabled?1:0);v.put("schedule_id",s.scheduleId);
        return v;
    }
    public synchronized boolean save(ScheduleEntry s){
        if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))return false;
        if(s.scheduleId==null||s.scheduleId.isEmpty())return false;
        if(s.id>0){
            ScheduleEntry before=find(s.id);
            if(before==null||!s.scheduleId.equals(before.scheduleId))return false;
        }
        SQLiteDatabase db=getWritableDatabase();ContentValues cv=values(s);
        if(s.id==0){
            s.id=db.insert("sessions",null,cv);
            return s.id>0;
        }
        return db.update("sessions",cv,"id=?",new String[]{Long.toString(s.id)})==1;
    }
    public synchronized int recolorSameCourse(String name,int color,String profileId){
        if(profileId==null||profileId.isEmpty())return 0;
        SQLiteDatabase db=getWritableDatabase();int count=0;
        db.beginTransaction();
        try{
            for(ScheduleEntry s:all(profileId))if(ScheduleCourseColors.same(name,s.course)&&s.color!=color){
                ContentValues cv=new ContentValues();cv.put("color",color);
                count+=db.update("sessions",cv,"id=?",new String[]{Long.toString(s.id)});
            }
            db.setTransactionSuccessful();
        }finally{db.endTransaction();}
        return count;
    }
    /** Old API restricted to the active schedule; no cross-schedule recoloring. */
    public int recolorSameCourse(String name,int color){
        return recolorSameCourse(name,color,AcademicSchedules.activeId(appContext));
    }
    public synchronized void delete(long id){
        getWritableDatabase().delete("sessions","id=?",new String[]{Long.toString(id)});
    }
    public synchronized void deleteProfile(String scheduleId){
        if(scheduleId!=null&&!scheduleId.isEmpty())
            getWritableDatabase().delete("sessions","schedule_id=?",new String[]{scheduleId});
    }
    public synchronized void assignUnassigned(String scheduleId){
        if(scheduleId==null||scheduleId.isEmpty())throw new IllegalArgumentException("Horario requerido");
        ContentValues v=new ContentValues();v.put("schedule_id",scheduleId);
        getWritableDatabase().update("sessions",v,"schedule_id=?",new String[]{""});
    }
    /** Atomic profile-specific import; same-named courses in other profiles stay independent. */
    public synchronized int importReviewed(List<ScheduleEntry> incoming,String scheduleId){
        if(scheduleId==null||scheduleId.isEmpty())throw new IllegalArgumentException("Horario requerido");
        if(incoming==null||incoming.isEmpty())return 0;
        SQLiteDatabase db=getWritableDatabase();db.beginTransaction();int inserted=0;
        try{
            List<ScheduleEntry> existing=all(scheduleId);
            ScheduleCourseColors.align(incoming,existing);
            for(ScheduleEntry source:incoming){
                ScheduleEntry s=source.copy();s.scheduleId=scheduleId;s.id=0;
                if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))continue;
                boolean duplicate=false;
                for(ScheduleEntry old:existing)if(old.day==s.day&&old.start==s.start
                        &&old.end==s.end&&ScheduleCourseColors.same(old.course,s.course)){
                    duplicate=true;break;
                }
                if(duplicate)continue;
                long id=db.insert("sessions",null,values(s));
                if(id>0){s.id=id;inserted++;existing.add(s);}
            }
            db.setTransactionSuccessful();
        }finally{db.endTransaction();}
        return inserted;
    }
    /** Legacy caller: uses selected profile, refuses silently mixing unassigned sessions. */
    public synchronized int importReviewed(List<ScheduleEntry> items){
        if(items==null||items.isEmpty())return 0;
        String target=items.get(0).scheduleId;
        if(target==null||target.isEmpty())target=AcademicSchedules.activeId(appContext);
        if(target==null||target.isEmpty())throw new IllegalStateException(
                "Crea o selecciona un horario desde Plan de estudio antes de importar");
        return importReviewed(items,target);
    }
}
