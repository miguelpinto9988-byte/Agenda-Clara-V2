package pe.agendaclara.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/** Notes are date-indexed records, deliberately independent of tasks, deadlines and alarms. */
public final class StickyNotesStore extends SQLiteOpenHelper {
    private static volatile StickyNotesStore instance;
    public static StickyNotesStore get(Context context){
        if(instance==null) synchronized(StickyNotesStore.class){
            if(instance==null)instance=new StickyNotesStore(context.getApplicationContext());
        }
        return instance;
    }
    private StickyNotesStore(Context context){super(context,"agenda-sticky-notes.db",null,1);}
    @Override public void onCreate(SQLiteDatabase db){
        db.execSQL("CREATE TABLE sticky_notes (id INTEGER PRIMARY KEY AUTOINCREMENT,"+
                "title TEXT NOT NULL, body TEXT NOT NULL DEFAULT '',"+
                "day TEXT NOT NULL, category TEXT NOT NULL, color INTEGER NOT NULL,"+
                "updated_at INTEGER NOT NULL)");
        db.execSQL("CREATE INDEX sticky_notes_day_idx ON sticky_notes(day,id)");
        db.execSQL("CREATE INDEX sticky_notes_category_idx ON sticky_notes(category,day)");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int oldVersion,int newVersion){
        // There is no destructive migration: schema version 1 has no upgrade path yet.
        if(oldVersion!=newVersion)throw new IllegalStateException("Unsupported sticky notes schema migration");
    }
    public static final class Note {
        public long id;
        public String title="",body="",category="Notas";
        public LocalDate day=LocalDate.now();
        public int color=0;
    }
    private static Note read(Cursor c){
        Note n=new Note();n.id=c.getLong(0);n.title=c.getString(1);n.body=c.getString(2);
        n.day=LocalDate.parse(c.getString(3));n.category=c.getString(4);n.color=c.getInt(5);
        return n;
    }
    private List<Note> fetch(String where,String[] args){
        ArrayList<Note> notes=new ArrayList<>();
        try(Cursor c=getReadableDatabase().query("sticky_notes",
                new String[]{"id","title","body","day","category","color"},
                where,args,null,null,"day DESC, id DESC", "500")){
            while(c.moveToNext())notes.add(read(c));
        }
        return notes;
    }
    public synchronized List<Note> inCategory(String category){
        return fetch("category = ? COLLATE NOCASE",new String[]{category});
    }
    public synchronized List<Note> onDay(LocalDate date){
        return fetch("day = ?",new String[]{date.toString()});
    }
    /** One indexed query per calendar month, not one SQLite query per day cell. */
    public synchronized java.util.Set<LocalDate> daysInMonth(java.time.YearMonth month){
        java.util.HashSet<LocalDate> dates=new java.util.HashSet<>();
        String first=month.atDay(1).toString(),after=month.plusMonths(1).atDay(1).toString();
        try(Cursor c=getReadableDatabase().query(true,"sticky_notes",new String[]{"day"},
                "day>=? AND day<?",new String[]{first,after},null,null,null,null)){
            while(c.moveToNext())dates.add(LocalDate.parse(c.getString(0)));
        }
        return dates;
    }
    public synchronized Note find(long id){
        List<Note> one=fetch("id = ?",new String[]{Long.toString(id)});
        return one.isEmpty()?null:one.get(0);
    }
    public synchronized long save(Note n){
        if(n==null||n.day==null)throw new IllegalArgumentException("A note requires a calendar date");
        String title=n.title==null?"":n.title.trim();
        if(title.isEmpty()||title.length()>90)throw new IllegalArgumentException("Note title must contain 1–90 characters");
        String body=n.body==null?"":n.body.trim();
        if(body.length()>2000)throw new IllegalArgumentException("Note body exceeds 2000 characters");
        String category=n.category==null?"":n.category.trim();
        if(category.isEmpty())throw new IllegalArgumentException("A note requires a category");
        if(n.color<0||n.color>=StickyNotesUi.COLORS.length)throw new IllegalArgumentException("Unknown note color");
        ContentValues row=new ContentValues();
        row.put("title",title);row.put("body",body);row.put("day",n.day.toString());
        row.put("category",category);row.put("color",n.color);row.put("updated_at",System.currentTimeMillis());
        SQLiteDatabase db=getWritableDatabase();
        if(n.id>0){
            if(db.update("sticky_notes",row,"id=?",new String[]{Long.toString(n.id)})!=1)
                throw new IllegalStateException("Note no longer exists");
        }else n.id=db.insertOrThrow("sticky_notes",null,row);
        return n.id;
    }
    public synchronized void delete(long id){
        getWritableDatabase().delete("sticky_notes","id=?",new String[]{Long.toString(id)});
    }
    public synchronized void reassignCategory(String oldName,String newName){
        ContentValues row=new ContentValues();row.put("category",newName);
        getWritableDatabase().update("sticky_notes",row,"category=? COLLATE NOCASE",new String[]{oldName});
    }
}
