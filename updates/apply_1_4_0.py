#!/usr/bin/env python3
"""Actualiza fuentes Agenda Clara 1.3.1 a 1.4.0, sin claves privadas."""
from pathlib import Path

root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def replace(filename,old,new):
    p=root/filename;s=p.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:raise RuntimeError(f"{filename}: se esperaba 1 coincidencia, se encontraron {n}: {old[:90]}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

replace("Task.java",'    public boolean done, urgent, calendarEnabled;','    public String category="General";\n    public boolean done, urgent, calendarEnabled;')
replace("Store.java",'super(c,"agenda_clara.db",null,5)','super(c,"agenda_clara.db",null,6)')
replace("Store.java",'created INTEGER NOT NULL,done INTEGER NOT NULL,urgent INTEGER NOT NULL,offsets TEXT NOT NULL','created INTEGER NOT NULL,done INTEGER NOT NULL,urgent INTEGER NOT NULL,category TEXT NOT NULL DEFAULT \'General\',offsets TEXT NOT NULL')
replace("Store.java",'        createCompletedHistory(db);\n    }','        createCompletedHistory(db);\n        createSubtasks(db);\n    }')
replace("Store.java",'    @Override public void onUpgrade(SQLiteDatabase db,int old,int next){',
'''    @Override public void onConfigure(SQLiteDatabase db){super.onConfigure(db);db.setForeignKeyConstraintsEnabled(true);}
    private void createSubtasks(SQLiteDatabase db){
        db.execSQL("CREATE TABLE IF NOT EXISTS subtasks(id INTEGER PRIMARY KEY AUTOINCREMENT,task_id INTEGER NOT NULL,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE)");
        db.execSQL("CREATE INDEX IF NOT EXISTS subtasks_task ON subtasks(task_id)");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int old,int next){''')
replace("Store.java",'        if(old<5)createCompletedHistory(db);\n','        if(old<5)createCompletedHistory(db);\n        if(old<6){db.execSQL("ALTER TABLE tasks ADD COLUMN category TEXT NOT NULL DEFAULT \'General\'");createSubtasks(db);}\n')
replace("Store.java",'        v.put("title",t.title);v.put("notes",t.notes);v.put("source",t.source);',
'''        v.put("title",t.title);v.put("notes",t.notes);v.put("source",t.source);v.put("category",TaskOrganization.category(t.category));''')
replace("Store.java",'t.source=c.getString(c.getColumnIndexOrThrow("source"));','t.source=c.getString(c.getColumnIndexOrThrow("source"));t.category=TaskOrganization.category(c.getString(c.getColumnIndexOrThrow("category")));')
replace("Store.java",'    public synchronized void delete(long id){','''    public static final class Subtask{
        public long id,taskId;public String title;public boolean done;
    }
    public synchronized List<Subtask> subtasks(long taskId){
        List<Subtask> out=new ArrayList<>();
        try(Cursor c=getReadableDatabase().query("subtasks",new String[]{"id","task_id","title","done"},"task_id=?",new String[]{String.valueOf(taskId)},null,null,"id ASC")){
            while(c.moveToNext()){Subtask s=new Subtask();s.id=c.getLong(0);s.taskId=c.getLong(1);s.title=c.getString(2);s.done=c.getInt(3)!=0;out.add(s);}
        }
        return out;
    }
    public synchronized int[] subtaskProgress(long taskId){
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COUNT(*),COALESCE(SUM(done),0) FROM subtasks WHERE task_id=?",new String[]{String.valueOf(taskId)})){
            return c.moveToFirst()?new int[]{c.getInt(0),c.getInt(1)}:new int[]{0,0};
        }
    }
    public synchronized boolean addSubtask(long taskId,String title){
        title=title==null?"":title.trim();
        if(!TaskOrganization.validSubtask(title)||find(taskId)==null||subtaskProgress(taskId)[0]>=50)return false;
        ContentValues v=new ContentValues();v.put("task_id",taskId);v.put("title",title);v.put("done",0);
        return getWritableDatabase().insert("subtasks",null,v)>0;
    }
    public synchronized void setSubtaskDone(long taskId,long subtaskId,boolean done){
        ContentValues v=new ContentValues();v.put("done",done?1:0);
        getWritableDatabase().update("subtasks",v,"task_id=? AND id=?",new String[]{String.valueOf(taskId),String.valueOf(subtaskId)});
    }
    public synchronized void deleteSubtask(long taskId,long subtaskId){
        getWritableDatabase().delete("subtasks","task_id=? AND id=?",new String[]{String.valueOf(taskId),String.valueOf(subtaskId)});
    }
    public synchronized void delete(long id){''')
(root/"TaskOrganization.java").write_text('''package pe.agendaclara.app;
public final class TaskOrganization{
  public static final String[] CATEGORIES={"General","Estudios","Trabajo","Personal","Salud","Otros"};
  private TaskOrganization(){}
  public static String category(String value){
    if(value==null)return "General";
    for(String c:CATEGORIES)if(c.equalsIgnoreCase(value.trim()))return c;
    return "General";
  }
  public static boolean validSubtask(String title){return title!=null&&!title.trim().isEmpty()&&title.trim().length()<=180;}
}
''',encoding="utf-8")
replace("MainActivity.java",'inboxLimit=25,taskLimit=60;String chatQuery="";','inboxLimit=25,taskLimit=24,categoryFilter=0;String chatQuery="";')
replace("MainActivity.java",'filter=state.getInt("filter");query=state.getString("query","");','filter=state.getInt("filter");categoryFilter=Math.max(0,Math.min(TaskOrganization.CATEGORIES.length,state.getInt("category_filter")));query=state.getString("query","");')
replace("MainActivity.java",'out.putInt("filter",filter);out.putString("query",query);','out.putInt("filter",filter);out.putInt("category_filter",categoryFilter);out.putString("query",query);')
replace("MainActivity.java",'        horizontal.addView(chips);body.addView(horizontal);gap(body,8);',
'''        horizontal.addView(chips);body.addView(horizontal);gap(body,8);
        TextView categoriesLabel=text("Filtrar por categoría",12,MUTED,true);body.addView(categoriesLabel);gap(body,4);
        HorizontalScrollView categoriesScroll=new HorizontalScrollView(this);categoriesScroll.setHorizontalScrollBarEnabled(false);LinearLayout categoriesChips=row();
        for(int j=0;j<=TaskOrganization.CATEGORIES.length;j++){
            final int chosen=j;String label=j==0?"Todas":TaskOrganization.CATEGORIES[j-1];
            Button b=button(label,()->{categoryFilter=chosen;taskLimit=24;render();});
            b.setTextColor(j==categoryFilter?0xffffffff:MUTED);
            b.setBackground(rounded(j==categoryFilter?VIOLET:0xffffffff,18));categoriesChips.addView(b);
        }
        categoriesScroll.addView(categoriesChips);body.addView(categoriesScroll);gap(body,8);''')
replace("MainActivity.java",'query=s.toString();taskLimit=60;','query=s.toString();taskLimit=24;')
replace("MainActivity.java",'handler.postDelayed(taskSearch,120);','handler.postDelayed(taskSearch,220);')
replace("MainActivity.java",'            if(date==null){\n                if(filter==1',
'''            if(date==null){
                if(categoryFilter>0&&!TaskOrganization.CATEGORIES[categoryFilter-1].equals(t.category))continue;
                if(filter==1''')
replace("MainActivity.java",'if(count<taskLimit)taskCard(taskList,t);count++;','if(count<taskLimit)taskCard(taskList,t);count++;')
replace("MainActivity.java",'taskLimit+=60;fillTasks(all,date);','taskLimit+=24;fillTasks(all,date);')
replace("MainActivity.java",'        c.addView(text(TaskLogic.when(t.due),14,INK,false));',
'''        c.addView(text("◈ "+TaskOrganization.category(t.category),11,VIOLET,true));gap(c,4);
        int[] progress=Store.get(this).subtaskProgress(t.id);
        if(progress[0]>0){c.addView(text("Subtareas: "+progress[1]+" de "+progress[0]+" realizadas",12,MUTED,true));gap(c,4);}
        c.addView(text(TaskLogic.when(t.due),14,INK,false));''')
replace("MainActivity.java",'        LinearLayout actions=row();actions.addView(button("✎  Editar",()->openEditor(t.id,null,null)),new LinearLayout.LayoutParams(0,-2,1));actions.addView(button("♧  Compartir",()->shareTask(t)),new LinearLayout.LayoutParams(0,-2,1));c.addView(actions);',
'''        LinearLayout actions=row();actions.addView(button("✎  Editar",()->openEditor(t.id,null,null)),new LinearLayout.LayoutParams(0,-2,1));actions.addView(button("☑  Subtareas",()->openSubtasks(t.id)),new LinearLayout.LayoutParams(0,-2,1));c.addView(actions);''')
replace("MainActivity.java",'    void calendarPage(){',
'''    void openSubtasks(long taskId){
        Task current=Store.get(this).find(taskId);if(current==null){toast("La tarea no está disponible.");return;}
        LinearLayout holder=column();holder.setPadding(dp(16),dp(8),dp(16),dp(12));
        ScrollView scroll=new WindowLayout.DialogScroll(this);scroll.addView(holder);
        LinearLayout entries=column();holder.addView(entries);
        final Runnable[] reload={null};
        reload[0]=()->{
            entries.removeAllViews();
            List<Store.Subtask> children=Store.get(this).subtasks(taskId);
            entries.addView(text("Progreso: "+Store.get(this).subtaskProgress(taskId)[1]+"/"+children.size(),13,VIOLET,true));
            if(children.isEmpty())entries.addView(text("Todavía no hay subtareas.",13,MUTED,false));
            for(Store.Subtask item:children){
                LinearLayout line=row();CheckBox check=new CheckBox(this);check.setText(item.title);check.setTextColor(INK);check.setChecked(item.done);
                line.addView(check,new LinearLayout.LayoutParams(0,-2,1));
                Button remove=button("×",()->{Store.get(this).deleteSubtask(taskId,item.id);reload[0].run();});
                remove.setContentDescription("Quitar subtarea: "+item.title);line.addView(remove);
                check.setOnCheckedChangeListener((v,on)->{Store.get(this).setSubtaskDone(taskId,item.id,on);reload[0].run();});
                entries.addView(line);
            }
        };
        holder.addView(button("＋ Nueva subtarea",()->{
            EditText name=input("Nombre de subtarea","",android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
            LinearLayout wrap=column();wrap.setPadding(dp(16),0,dp(16),0);wrap.addView(name);
            AlertDialog dlg=dialogBuilder().setTitle("Nueva subtarea").setView(wrap).setNegativeButton("Cancelar",null).setPositiveButton("Añadir",null).create();
            dlg.setOnShowListener(d->dlg.getButton(-1).setOnClickListener(v->{
                if(!Store.get(this).addSubtask(taskId,name.getText().toString())){name.setError("Escribe de 1 a 180 caracteres (máximo 50 subtareas).");return;}
                dlg.dismiss();reload[0].run();}));
            dlg.show();
        }));
        AlertDialog dlg=dialogBuilder().setTitle("Subtareas · "+current.title).setView(scroll).setPositiveButton("Cerrar",(d,w)->{forceRefresh=true;render();}).create();
        reload[0].run();dlg.show();
    }
    void calendarPage(){''')
replace("MainActivity.java",'        CheckBox urgent=new CheckBox(this);',
'''        subtitle(box,"Categoría");
        Spinner categoryPicker=new Spinner(this);categoryPicker.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,TaskOrganization.CATEGORIES));
        String currentCategory=draft!=null?draft.getString("category",t.category):t.category;
        for(int i=0;i<TaskOrganization.CATEGORIES.length;i++)if(TaskOrganization.CATEGORIES[i].equals(TaskOrganization.category(currentCategory)))categoryPicker.setSelection(i);
        box.addView(categoryPicker);
        CheckBox urgent=new CheckBox(this);''')
replace("MainActivity.java",'b.putString("origin",t.originKey);b.putBoolean("schedule"','b.putString("origin",t.originKey);b.putString("category",TaskOrganization.CATEGORIES[categoryPicker.getSelectedItemPosition()]);b.putBoolean("schedule"')
replace("MainActivity.java",'t.title=value;t.notes=notes.getText().toString().trim();','t.title=value;t.category=TaskOrganization.CATEGORIES[categoryPicker.getSelectedItemPosition()];t.notes=notes.getText().toString().trim();')
replace("MainActivity.java",'box.addView(button("Más opciones · notas, prioridad y repetición"','box.addView(button("Más opciones · notas, prioridad y repetición"') if False else None
# Copia de seguridad: v2 incluye categoría y subtareas; restaura backups 1.3.1 v1
replace("TaskBackup.java",'.put("repeatMinutes",t.repeatMinutes).put("duration",t.duration));',
''' .put("repeatMinutes",t.repeatMinutes).put("duration",t.duration).put("category",TaskOrganization.category(t.category))
      .put("subtasks",subtasksToJson(context,t.id)));''')
replace("TaskBackup.java",'  private TaskBackup(){}',
'''  private TaskBackup(){}
  private static JSONArray subtasksToJson(Context context,long taskId)throws Exception{
    JSONArray a=new JSONArray();
    for(Store.Subtask s:Store.get(context).subtasks(taskId))a.put(new JSONObject().put("title",s.title).put("done",s.done));
    return a;
  }''')
replace("TaskBackup.java",'.put("schema",1).put("exportedAt"','.put("schema",2).put("exportedAt"')
replace("TaskBackup.java",'    if(!"agenda-clara-tasks".equals(root.optString("format"))||root.optInt("schema",-1)!=1)',
'    if(!"agenda-clara-tasks".equals(root.optString("format"))||(root.optInt("schema",-1)!=1&&root.optInt("schema",-1)!=2))')
replace("TaskBackup.java",'    List<ContentValues> validated=new ArrayList<>();',
'''    List<ContentValues> validated=new ArrayList<>();
    List<List<ContentValues>> children=new ArrayList<>();''')
replace("TaskBackup.java",'      v.put("title",title);v.put("notes",notes);v.put("source",o.optString("source","Copia restaurada"));',
'''      v.put("title",title);v.put("notes",notes);v.put("source",o.optString("source","Copia restaurada"));
      v.put("category",TaskOrganization.category(o.optString("category","General")));
      JSONArray sub=o.optJSONArray("subtasks");List<ContentValues> one=new ArrayList<>();
      if(sub!=null){
        if(sub.length()>50)throw new IOException("Máximo 50 subtareas por actividad.");
        for(int j=0;j<sub.length();j++){
          JSONObject item=sub.getJSONObject(j);String st=item.getString("title").trim();
          if(!TaskOrganization.validSubtask(st))throw new IOException("Subtarea inválida.");
          ContentValues sv=new ContentValues();sv.put("title",st);sv.put("done",item.optBoolean("done",false)?1:0);one.add(sv);
        }
      }
      children.add(one);''')
replace("TaskBackup.java",'        for(ContentValues v:validated){',
'''        for(int index=0;index<validated.size();index++){
          ContentValues v=validated.get(index);''')
replace("TaskBackup.java",'          if(db.insertOrThrow("tasks",null,v)>0)count++;',
'''          long inserted=db.insertOrThrow("tasks",null,v);
          if(inserted>0){count++;
            for(ContentValues child:children.get(index)){
              child.put("task_id",inserted);db.insertOrThrow("subtasks",null,child);
            }
          }''')
gradle=Path("AgendaClara/app/build.gradle");s=gradle.read_text(encoding="utf-8")
if s.count("versionCode 6")!=1 or s.count("versionName '1.3.1'")!=1:raise RuntimeError("Unexpected Gradle version")
gradle.write_text(s.replace("versionCode 6","versionCode 7").replace("versionName '1.3.1'","versionName '1.4.0'"),encoding="utf-8")
print("Agenda Clara 1.4.0: migración, subtareas, categorías, filtros, backup v2 y paginación preparados.")
