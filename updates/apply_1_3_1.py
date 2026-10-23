#!/usr/bin/env python3
"""Agenda Clara 1.3.1 safe upgrade from verified 1.3.0 sources."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def change(file, before, after):
    f=p/file
    s=f.read_text()
    if before not in s: raise RuntimeError("No se encuentra patrón esperado en "+file+": "+before[:90])
    f.write_text(s.replace(before,after,1))
change("Store.java",'super(c,"agenda_clara.db",null,4)','super(c,"agenda_clara.db",null,5)')
change("Store.java",'        createLinked(db);\n    }','        createLinked(db);\n        createCompletedHistory(db);\n    }')
change("Store.java",'    @Override public void onUpgrade(SQLiteDatabase db,int old,int next){',
'''    private void createCompletedHistory(SQLiteDatabase db){
        db.execSQL("CREATE TABLE IF NOT EXISTS completed_history(task_id INTEGER PRIMARY KEY,completed_at INTEGER NOT NULL)");
        db.execSQL("CREATE INDEX IF NOT EXISTS completed_history_time ON completed_history(completed_at)");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int old,int next){''')
change("Store.java",'            db.execSQL("CREATE INDEX IF NOT EXISTS tasks_completed_at ON tasks(done,completed_at)");\n        }\n    }',
'            db.execSQL("CREATE INDEX IF NOT EXISTS tasks_completed_at ON tasks(done,completed_at)");\n        }\n        if(old<5)createCompletedHistory(db);\n    }')
change("Store.java",'        return getWritableDatabase().delete("tasks","done=1 AND completed_at>0 AND completed_at<=?",new String[]{""+(now-TaskExpiryPolicy.RETENTION_MILLIS)});',
'''        SQLiteDatabase db=getWritableDatabase();
        long cutoff=now-TaskExpiryPolicy.RETENTION_MILLIS;
        db.beginTransaction();
        try{
            db.execSQL("INSERT OR IGNORE INTO completed_history(task_id,completed_at) SELECT id,completed_at FROM tasks WHERE done=1 AND completed_at>0 AND completed_at<=?",new Object[]{cutoff});
            int removed=db.delete("tasks","done=1 AND completed_at>0 AND completed_at<=?",new String[]{""+cutoff});
            db.setTransactionSuccessful();return removed;
        }finally{db.endTransaction();}''')
change("Store.java",'    public synchronized long nextCompletedExpiry(){',
'''    /** Non-identifying productivity counter that survives task purges. */
    public synchronized int completedSince(long from){
        int total=0;
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COUNT(*) FROM completed_history WHERE completed_at>=?",new String[]{""+from})){if(c.moveToFirst())total+=c.getInt(0);}
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COUNT(*) FROM tasks WHERE done=1 AND completed_at>=?",new String[]{""+from})){if(c.moveToFirst())total+=c.getInt(0);}
        return total;
    }
    public synchronized int[] purgeOldData(long now){
        SQLiteDatabase db=getWritableDatabase();
        int days=Math.max(1,Math.min(365,Prefs.get(context).getInt("wa_history_days",90)));
        int messages=db.delete("messages","stamp<?",new String[]{""+(now-days*86400000L)});
        int resolved=db.delete("inbox","state<>0 AND created<?",new String[]{""+(now-30L*86400000L)});
        return new int[]{messages,resolved};
    }
    public synchronized long nextCompletedExpiry(){''')
change("CompletedTaskCleanup.java",'int removed=Store.get(context).purgeExpiredCompleted(System.currentTimeMillis());',
'''Store store=Store.get(context);
        int removed=store.purgeExpiredCompleted(System.currentTimeMillis());
        store.purgeOldData(System.currentTimeMillis());''')
change("MainActivity.java",'        LinearLayout summary=card(body);summary.setBackground(gradient(0xffffffff,0xfff0f5ff,19));',
'''        int weekDone=Store.get(this).completedSince(System.currentTimeMillis()-7L*86400000L);
        LinearLayout summary=card(body);summary.setBackground(gradient(0xffffffff,0xfff0f5ff,19));''')
change("MainActivity.java",'gap(title,4);title.addView(text(done+" de "+all.size()+" actividades completadas",12,MUTED,false));',
'gap(title,4);title.addView(text("Activas: "+done+" de "+all.size()+" · Últimos 7 días: "+weekDone+" completadas",12,MUTED,false));')
change("MainActivity.java",'stats.addView(statLabel("Completadas",""+done,SUCCESS)',
'stats.addView(statLabel("Completadas (7d)",""+weekDone,SUCCESS)')
change("MainActivity.java",'        LinearLayout about=card(body);about.addView(text("Agenda Clara 1.3 · Diseño productividad",17,INK,true));',
'''        LinearLayout protection=card(body);
        protection.addView(text("Tus datos y copias de seguridad",20,INK,true));
        protection.addView(text("Exportar/recuperar tareas JSON sin mensajes ni claves de WhatsApp. El archivo NO está cifrado: consérvalo de forma privada.",13,MUTED,false));
        protection.addView(button("Exportar mis tareas",this::exportTasks));
        protection.addView(button("Restaurar tareas desde JSON",this::importTasks));
        protection.addView(button("Borrar mensajes y propuestas antiguos",()->dialogBuilder().setTitle("Limpieza de datos")
          .setMessage("Se borrarán los mensajes fuera del periodo de historial y propuestas atendidas hace más de 30 días. No afecta a tareas ni propuestas pendientes.")
          .setNegativeButton("Cancelar",null).setPositiveButton("Limpiar",(d,w)->new Thread(()->{
              int[] result=Store.get(this).purgeOldData(System.currentTimeMillis());
              runOnUiThread(()->toast("Mensajes: "+result[0]+" · Propuestas: "+result[1]+" retirados."));
          },"data-maintenance").start()).show()));
        protection.addView(text("Las tareas completadas se retiran de agenda tras una hora; el total semanal conserva solo fecha, sin título ni notas.",12,MUTED,false));
        LinearLayout about=card(body);about.addView(text("Agenda Clara 1.3.1 · Seguridad y recuperación",17,INK,true));''')
change("MainActivity.java",'    boolean notificationAccess(){',
'''    private static final int EXPORT_TASKS_REQUEST=642,IMPORT_TASKS_REQUEST=643;
    void exportTasks(){
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/json");
        i.putExtra(Intent.EXTRA_TITLE,"Agenda-Clara-tareas.json");startActivityForResult(i,EXPORT_TASKS_REQUEST);
    }
    void importTasks(){
        dialogBuilder().setTitle("Restaurar tareas").setMessage("Solo archivos JSON de Agenda Clara. Se omiten duplicados. No se restauran mensajes, sesiones ni ID de eventos de calendario.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Elegir archivo",(d,w)->{
                Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/json");
                startActivityForResult(i,IMPORT_TASKS_REQUEST);
            }).show();
    }
    void backupResult(int request,Uri uri){
        new Thread(()->{
            try{
                if(request==EXPORT_TASKS_REQUEST){
                    int count=TaskBackup.exportTo(this,uri);
                    runOnUiThread(()->toast("Se exportaron "+count+" tareas. Guarda el archivo en privado."));
                }else{
                    int count=TaskBackup.importFrom(this,uri);
                    CompletedTaskCleanup.run(this);Reminders.rebuild(this);TaskWidget.refresh(this);
                    runOnUiThread(()->{toast("Se recuperaron "+count+" tareas; duplicados omitidos.");forceRefresh=true;requestRefresh();});
                }
            }catch(Exception ex){runOnUiThread(()->toast("Error de copia: "+(ex.getMessage()==null?"Archivo incompatible":ex.getMessage())));}
        },"agenda-backup").start();
    }
    boolean notificationAccess(){''')
change("MainActivity.java",'        super.onActivityResult(request,result,data);if(request!=540||result!=RESULT_OK||data==null||data.getData()==null)return;',
'''        super.onActivityResult(request,result,data);
        if((request==EXPORT_TASKS_REQUEST||request==IMPORT_TASKS_REQUEST)&&result==RESULT_OK&&data!=null&&data.getData()!=null){backupResult(request,data.getData());return;}
        if(request!=540||result!=RESULT_OK||data==null||data.getData()==null)return;''')
backup = r'''package pe.agendaclara.app;

import android.content.*;
import android.database.*;
import android.database.sqlite.*;
import android.net.Uri;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Manual task-only backup; never exports WhatsApp content or credentials. */
public final class TaskBackup {
  private static final int MAX_TASKS=5000, MAX_CHARS=6*1024*1024;
  private TaskBackup(){}
  public static int exportTo(Context context,Uri uri)throws Exception{
    List<Task> list=Store.get(context).all();
    if(list.size()>MAX_TASKS)throw new IOException("Máximo 5000 tareas por copia.");
    JSONObject root=new JSONObject().put("format","agenda-clara-tasks").put("schema",1).put("exportedAt",System.currentTimeMillis());
    JSONArray rows=new JSONArray();
    for(Task t:list)rows.put(new JSONObject()
      .put("title",t.title).put("notes",t.notes).put("source",t.source)
      .put("due",t.due).put("created",t.created).put("done",t.done)
      .put("completedAt",t.completedAt).put("urgent",t.urgent).put("offsets",t.offsets)
      .put("repeatMinutes",t.repeatMinutes).put("duration",t.duration));
    root.put("tasks",rows);
    byte[] data=root.toString(2).getBytes(StandardCharsets.UTF_8);
    if(data.length>MAX_CHARS)throw new IOException("Archivo superior a 6 MB.");
    try(OutputStream out=context.getContentResolver().openOutputStream(uri,"wt")){
      if(out==null)throw new IOException("No se puede crear el archivo.");
      out.write(data);
    }
    return list.size();
  }
  public static int importFrom(Context context,Uri uri)throws Exception{
    StringBuilder b=new StringBuilder();
    try(InputStream in=context.getContentResolver().openInputStream(uri)){
      if(in==null)throw new IOException("No se puede abrir el archivo.");
      try(Reader r=new InputStreamReader(in,StandardCharsets.UTF_8)){
        char[] chunk=new char[8192];int n;
        while((n=r.read(chunk))!=-1){b.append(chunk,0,n);if(b.length()>MAX_CHARS)throw new IOException("Archivo superior a 6 MB.");}
      }
    }
    JSONObject root=new JSONObject(b.toString());
    if(!"agenda-clara-tasks".equals(root.optString("format"))||root.optInt("schema",-1)!=1)
      throw new IOException("Formato incompatible de copia.");
    JSONArray rows=root.getJSONArray("tasks");
    if(rows.length()>MAX_TASKS)throw new IOException("Demasiadas tareas en la copia.");
    List<ContentValues> validated=new ArrayList<>();
    for(int i=0;i<rows.length();i++){
      JSONObject o=rows.getJSONObject(i);
      String title=o.getString("title").trim(),notes=o.optString("notes","");
      if(title.isEmpty()||title.length()>500||notes.length()>10000)throw new IOException("Tarea inválida: "+(i+1));
      long due=o.optLong("due",0),created=o.optLong("created",0),completed=o.optLong("completedAt",0);
      if(due<0||created<0||completed<0)throw new IOException("Fecha inválida: "+(i+1));
      boolean done=o.optBoolean("done",false);
      ContentValues v=new ContentValues();
      v.put("title",title);v.put("notes",notes);v.put("source",o.optString("source","Copia restaurada"));
      v.put("due",due);v.put("created",created>0?created:System.currentTimeMillis());
      v.put("done",done?1:0);v.put("completed_at",done?(completed>0?completed:System.currentTimeMillis()):0);
      v.put("urgent",o.optBoolean("urgent",false)?1:0);v.put("offsets",o.optString("offsets","1440,60,0"));
      v.put("repeat_minutes",Math.max(0,Math.min(10080,o.optInt("repeatMinutes",0))));
      v.put("duration",Math.max(5,Math.min(1440,o.optInt("duration",60))));
      v.put("event_id",-1);v.put("calendar_id",-1);v.put("calendar_enabled",0);v.putNull("origin_key");
      validated.add(v);
    }
    Store store=Store.get(context);int count=0;
    synchronized(store){
      SQLiteDatabase db=store.getWritableDatabase();db.beginTransaction();
      try{
        for(ContentValues v:validated){
          try(Cursor c=db.query("tasks",new String[]{"id"},"title=? AND due=? AND created=?",
            new String[]{v.getAsString("title"),v.getAsString("due"),v.getAsString("created")},null,null,null,"1")){
            if(c.moveToFirst())continue;
          }
          if(db.insertOrThrow("tasks",null,v)>0)count++;
        }
        db.setTransactionSuccessful();
      }finally{db.endTransaction();}
    }
    return count;
  }
}
'''
(p/"TaskBackup.java").write_text(backup)
gradle=Path("AgendaClara/app/build.gradle")
s=gradle.read_text()
assert "versionCode 5" in s and "versionName '1.3.0'" in s
gradle.write_text(s.replace("versionCode 5","versionCode 6").replace("versionName '1.3.0'","versionName '1.3.1'"))
print("Actualización a Agenda Clara 1.3.1 aplicada.")
