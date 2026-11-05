package pe.agendaclara.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/** Stable task ID -> schedule UUID + course. Does not alter legacy task rows. */
public final class AcademicTaskLinks extends SQLiteOpenHelper {
    private static AcademicTaskLinks instance;
    private AcademicTaskLinks(Context context) {
        super(context.getApplicationContext(),"academic_task_links.db",null,1);
    }
    public static synchronized AcademicTaskLinks get(Context context) {
        if(instance==null)instance=new AcademicTaskLinks(context);
        return instance;
    }
    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE links(task_id INTEGER PRIMARY KEY,profile_id TEXT NOT NULL,course TEXT NOT NULL)");
        db.execSQL("CREATE INDEX links_profile ON links(profile_id)");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int old,int newer) {
        if(old!=newer)throw new IllegalStateException("Migra explícitamente los enlaces académicos");
    }
    public static final class Link {
        public final long taskId;
        public final String profileId,course;
        Link(long taskId,String profileId,String course) {
            this.taskId=taskId;this.profileId=profileId;this.course=course;
        }
    }
    public synchronized void assign(long id,String profileId,String course) {
        if(id<=0||profileId==null||profileId.isEmpty()||course==null||course.trim().isEmpty())
            throw new IllegalArgumentException("Vínculo académico incompleto");
        ContentValues values=new ContentValues();
        values.put("task_id",id);values.put("profile_id",profileId);values.put("course",course.trim());
        if(getWritableDatabase().insertWithOnConflict("links",null,values,
                SQLiteDatabase.CONFLICT_REPLACE)<0)
            throw new IllegalStateException("No se pudo guardar el vínculo del curso");
    }
    public synchronized Link find(long taskId) {
        try(Cursor cursor=getReadableDatabase().query("links",
                new String[]{"task_id","profile_id","course"},
                "task_id=?",new String[]{Long.toString(taskId)},null,null,null)) {
            if(!cursor.moveToFirst())return null;
            return new Link(cursor.getLong(0),cursor.getString(1),cursor.getString(2));
        }
    }
    public synchronized void clear(long taskId) {
        getWritableDatabase().delete("links","task_id=?",new String[]{Long.toString(taskId)});
    }
    public synchronized void clearProfile(String profileId) {
        if(profileId!=null&&!profileId.isEmpty())
            getWritableDatabase().delete("links","profile_id=?",new String[]{profileId});
    }
}
