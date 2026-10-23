#!/usr/bin/env python3
"""Agenda Clara 2.0 - accessibility, summary metrics, efficient subtask reads, Android API 36.
Apply after 1.3.1, 1.4.0 and 1.5.0. Does not touch WhatsApp credentials or keystores.
"""
from pathlib import Path
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def repl(filename,before,after):
    file=src/filename
    data=file.read_text(encoding="utf-8")
    count=data.count(before)
    if count != 1:
        raise RuntimeError(f"{filename}: expected exactly 1 pattern, got {count}: {before[:100]!r}")
    file.write_text(data.replace(before,after,1),encoding="utf-8")

(src/"UiPreferences.java").write_text("""package pe.agendaclara.app;

import android.content.Context;

/** Private, offline, app-specific accessibility preferences. System font scaling remains active. */
public final class UiPreferences {
    private UiPreferences(){}
    public static final int[] SCALES={100,115,130};
    public static int sizePercent(Context c){
        int saved=Prefs.get(c).getInt("ui_text_percent",100);
        for(int v:SCALES)if(saved==v)return v;
        return 100;
    }
    public static void setSizePercent(Context c,int value){
        for(int v:SCALES)if(v==value){Prefs.get(c).edit().putInt("ui_text_percent",v).apply();return;}
    }
    public static int scaled(Context c,int sp){return Math.max(10,Math.round(sp*sizePercent(c)/100f));}
    public static boolean contrast(Context c){return Prefs.get(c).getBoolean("ui_high_contrast",false);}
    public static void setContrast(Context c,boolean on){Prefs.get(c).edit().putBoolean("ui_high_contrast",on).apply();}
    public static int foreground(Context c,int color,int muted){
        return contrast(c)&&color==muted?0xff344160:color;
    }
}
""",encoding="utf-8")
(src/"TaskSummary.java").write_text("""package pe.agendaclara.app;
import java.util.List;

/** Pure summary calculations: the history is counted without retaining personal task text. */
public final class TaskSummary {
    private TaskSummary(){}
    public static final class Result{
        public final int pending,completedToday,urgent,completed7days,percentage;
        private Result(int pending,int completedToday,int urgent,int completed7days,int percentage){
            this.pending=pending;this.completedToday=completedToday;this.urgent=urgent;this.completed7days=completed7days;this.percentage=percentage;
        }
    }
    public static Result calculate(List<Task> all,long now,int completed7days){
        int pending=0,done=0,urgent=0;
        for(Task t:all){
            if(t.done)done++;
            else{
                pending++;
                String s=TaskLogic.status(t,now);
                if("Urgente".equals(s)||"Vencida".equals(s))urgent++;
            }
        }
        int counted=Math.max(0,completed7days);
        // A transparent snapshot measure, not a claimed daily achievement rate.
        long denominator=(long)pending+counted;
        int pct=denominator==0?100:(int)Math.min(100,100L*counted/denominator);
        return new Result(pending,done,urgent,counted,pct);
    }
}
""",encoding="utf-8")
repl("Store.java",
'    public synchronized int[] subtaskProgress(long taskId){',
'''    /** One aggregate query for the entire visible task screen instead of an N+1 query. */
    public synchronized Map<Long,int[]> subtaskProgressAll(){
        Map<Long,int[]> result=new HashMap<>();
        try(Cursor c=getReadableDatabase().rawQuery("SELECT task_id,COUNT(*),COALESCE(SUM(done),0) FROM subtasks GROUP BY task_id",null)){
            while(c.moveToNext())result.put(c.getLong(0),new int[]{c.getInt(1),c.getInt(2)});
        }
        return result;
    }
    public synchronized int[] subtaskProgress(long taskId){''')
repl("MainActivity.java",
'    String pendingHistoryChat="";ScrollView contentScroll;',
'    Map<Long,int[]> taskProgressCache=Collections.emptyMap();\n    String pendingHistoryChat="";ScrollView contentScroll;')
repl("MainActivity.java",
'    TextView text(String s,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);',
'    TextView text(String s,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(UiPreferences.scaled(this,size));t.setTextColor(UiPreferences.foreground(this,color,MUTED));')
repl("MainActivity.java",
'Button b=new Button(this);b.setText(label);b.setTextSize(14);',
'Button b=new Button(this);b.setText(label);b.setTextSize(UiPreferences.scaled(this,14));')
repl("MainActivity.java",
'b.setMinHeight(dp(44));',
'b.setMinHeight(dp(48));')
repl("MainActivity.java",
'e.setTextSize(16);e.setInputType(type);',
'e.setTextSize(UiPreferences.scaled(this,16));e.setInputType(type);')
repl("MainActivity.java",
'        body.removeAllViews();if(page==0)tasksPage();',
'        taskProgressCache=page<2?Store.get(this).subtaskProgressAll():Collections.emptyMap();\n        body.removeAllViews();if(page==0)tasksPage();')
repl("MainActivity.java",
'item.setBackground(rounded(page==n?PALE:0xffffffff,15));((ImageView)item.getChildAt(0))',
'item.setBackground(rounded(page==n?PALE:0xffffffff,15));item.setSelected(page==n);item.setContentDescription(new String[]{"Agenda","Calendario","Revisar","Conexiones"}[n]+(page==n?", pestaña actual":", abrir pestaña"));((ImageView)item.getChildAt(0))')
repl("MainActivity.java",
'TextView label=text(labels[n],10,MUTED,false);label.setGravity(Gravity.CENTER);',
'TextView label=text(labels[n],11,MUTED,false);label.setGravity(Gravity.CENTER);')
repl("MainActivity.java",
'    void tasksPage(){\n        List<Task> all=Store.get(this).all();int urgent=0,pending=0,done=0;\n        for(Task t:all){String s=TaskLogic.status(t,System.currentTimeMillis());if(t.done)done++;else{pending++;if(s.equals("Urgente")||s.equals("Vencida"))urgent++;}}\n        int weekDone=Store.get(this).completedSince(System.currentTimeMillis()-7L*86400000L);',
'''    void tasksPage(){
        List<Task> all=Store.get(this).all();
        long now=System.currentTimeMillis();
        TaskSummary.Result snapshot=TaskSummary.calculate(all,now,Store.get(this).completedSince(now-7L*86400000L));
        int pending=snapshot.pending,done=snapshot.completedToday,urgent=snapshot.urgent,weekDone=snapshot.completed7days;''')
repl("MainActivity.java",
'text("Activas: "+done+" de "+all.size()+" · Últimos 7 días: "+weekDone+" completadas",12,MUTED,false)',
'text("Pendientes: "+pending+" · Completadas en 7 días: "+weekDone,12,MUTED,false)')
repl("MainActivity.java",
'TextView percent=text((all.isEmpty()?100:done*100/all.size())+"%",24,GREEN,true);',
'TextView percent=text(snapshot.percentage+"%",24,GREEN,true);percent.setContentDescription("Avance estimado: "+snapshot.percentage+" por ciento, completadas en siete días frente a pendientes");')
repl("MainActivity.java",
'progress.setMax(Math.max(1,all.size()));progress.setProgress(done);',
'progress.setMax(Math.max(1,pending+weekDone));progress.setProgress(weekDone);')
repl("MainActivity.java",
'        summary.addView(heading);gap(summary,12);',
'        summary.addView(heading);gap(summary,8);summary.addView(text("Avance estimado = completadas últimos 7 días / (completadas últimos 7 días + pendientes actuales).",11,MUTED,false));gap(summary,12);')
repl("MainActivity.java",
'        int[] progress=Store.get(this).subtaskProgress(t.id);',
'        int[] progress=taskProgressCache.containsKey(t.id)?taskProgressCache.get(t.id):new int[]{0,0};')
repl("MainActivity.java",
'check.setContentDescription("Completar "+t.title);',
'check.setContentDescription((t.done?"Marcar como pendiente: ":"Marcar como completada: ")+t.title);')
repl("MainActivity.java",
'check.setOnCheckedChangeListener((b,checked)->{t.done=checked;Store.get(this).save(t);',
'check.setOnCheckedChangeListener((b,checked)->{t.done=checked;Store.get(this).save(t);toast(checked?"Tarea completada":"Tarea pendiente");')
repl("MainActivity.java",
'        LinearLayout alarm=card(body);alarm.addView(text("Recordatorios",20,INK,true));',
'''        LinearLayout accessibility=card(body);
        accessibility.addView(text("Accesibilidad y lectura",20,INK,true));
        accessibility.addView(text("Elige el tamaño de letra de Agenda Clara. Se añade al tamaño establecido en Android.",13,MUTED,false));
        String[] sizes={"Normal · 100 %","Grande · 115 %","Muy grande · 130 %"};
        Spinner sizeChoice=new Spinner(this);
        sizeChoice.setContentDescription("Tamaño de texto");
        sizeChoice.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,sizes));
        int selectedSize=UiPreferences.sizePercent(this);
        sizeChoice.setSelection(selectedSize==130?2:selectedSize==115?1:0);
        accessibility.addView(sizeChoice);
        Switch contrast=new Switch(this);
        contrast.setText("Mayor contraste en textos secundarios");
        contrast.setTextColor(INK);contrast.setMinHeight(dp(52));contrast.setChecked(UiPreferences.contrast(this));
        accessibility.addView(contrast);
        accessibility.addView(button("Aplicar preferencias visuales",()->{
            UiPreferences.setSizePercent(this,UiPreferences.SCALES[sizeChoice.getSelectedItemPosition()]);
            UiPreferences.setContrast(this,contrast.isChecked());
            forceRefresh=true;render();toast("Preferencias visuales guardadas");
        }));
        accessibility.addView(text("Los lectores de pantalla reciben etiquetas para los botones de navegación y el estado de las tareas.",12,MUTED,false));
        LinearLayout alarm=card(body);alarm.addView(text("Recordatorios",20,INK,true));''')
repl("MainActivity.java",
'text("Agenda Clara 1.3.1 · Seguridad y recuperación",17,INK,true)',
'text("Agenda Clara 2.0 · Interfaz accesible y Android 16",17,INK,true)')
gradle=Path("AgendaClara/app/build.gradle")
s=gradle.read_text(encoding="utf-8")
if s.count('compileSdk 35')!=1 or s.count('targetSdk 35')!=1 or s.count('versionCode 8')!=1 or s.count("versionName '1.5.0'")!=1:raise RuntimeError("Unexpected version in Gradle")
s=s.replace('compileSdk 35','compileSdk 36').replace('targetSdk 35','targetSdk 36').replace('versionCode 8','versionCode 9').replace("versionName '1.5.0'","versionName '2.0.0'")
gradle.write_text(s,encoding="utf-8")
build=Path("AgendaClara/build.gradle")
s=build.read_text(encoding="utf-8")
if s.count("version '8.7.3'")!=1:raise RuntimeError("Unexpected Gradle plugin")
build.write_text(s.replace("version '8.7.3'","version '8.13.2'"),encoding="utf-8")
wrapper=Path("AgendaClara/gradle/wrapper/gradle-wrapper.properties")
s=wrapper.read_text(encoding="utf-8")
if 'gradle-8.9-bin.zip' not in s:raise RuntimeError("Unexpected wrapper")
wrapper.write_text(s.replace('gradle-8.9-bin.zip','gradle-8.13-bin.zip'),encoding="utf-8")
manifest=Path("AgendaClara/app/src/main/AndroidManifest.xml")
s=manifest.read_text(encoding="utf-8")
if 'android:targetSdkVersion="35"' not in s:raise RuntimeError("Unexpected manifest target")
manifest.write_text(s.replace('android:targetSdkVersion="35"','android:targetSdkVersion="36"'),encoding="utf-8")
print("Agenda Clara 2.0: accessibility, summary, batch queries, Gradle 8.13 / API 36.")
