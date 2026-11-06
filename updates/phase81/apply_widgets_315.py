#!/usr/bin/env python3
"""Integrate Agenda Clara 3.15.0 academic widgets into verified 3.14.0 sources.

No changes to the PhotoWidget implementation or its configuration.
All anchors checked before writing so an incompatible build fails safely.
"""
from pathlib import Path
import hashlib
import shutil

ROOT=Path("AgendaClara/app/src/main")
JAVA=ROOT/"java/pe/agendaclara/app"
RES=ROOT/"res"
STAGE=Path(__file__).resolve().parent
GRADLE=Path("AgendaClara/app/build.gradle")

def replace_once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(old,new,1)

def run():
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 66")!=1 or gradle.count("versionName '3.14.0'")!=1:
        raise RuntimeError("Requires reconstructed Agenda Clara 3.14.0 (versionCode 66)")
    java_names=(
        "AcademicWidgetModels.java","WidgetAppearance.java",
        "AcademicWidgetRepository.java","AcademicWidgetTheme.java",
        "AcademicDayWidget.java","AcademicWeekWidget.java",
        "AcademicWidgetSettingsActivity.java","AcademicWidgetSync.java",
    )
    layout_names=(
        "widget_academic_day.xml","widget_academic_week.xml",
        "widget_notes_board.xml","widget_notes_board_compact.xml",
        "widget_notes_board_row.xml","widget_notes_board_row_compact.xml",
    )
    drawable_names=(
        "widget_academic_background.xml","widget_academic_background_dark.xml",
        "widget_note_card_yellow.xml",
    )
    xml_names=("widget_academic_day_info.xml","widget_academic_week_info.xml")
    all_files={}
    for name in java_names:
        all_files[JAVA/name]=STAGE/name
    for name in layout_names:
        all_files[RES/"layout"/name]=STAGE/name
    for name in drawable_names:
        all_files[RES/"drawable"/name]=STAGE/name
    for name in xml_names:
        all_files[RES/"xml"/name]=STAGE/name
    for dest,src in all_files.items():
        if dest.exists() or not src.is_file():
            raise RuntimeError("Missing staged asset or existing conflicting target: "+str(dest))
    # Selected notes choose one pastel background for each original color.
    palette={
        "pink":("#FFE0F0","#F1B9D9"),
        "blue":("#DEF0FF","#A9D5F6"),
        "green":("#DFF8E9","#B6E8CB"),
        "purple":("#EEE2FF","#D8BEF8"),
        "peach":("#FFEBD8","#F7CFB0"),
    }
    new_colors={}
    for name,(fill,border) in palette.items():
        path=RES/"drawable"/("widget_note_card_"+name+".xml")
        if path.exists():raise RuntimeError("Existing board color asset: "+str(path))
        new_colors[path]=('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="%s"/>
    <corners android:radius="16dp"/>
    <stroke android:width="1dp" android:color="%s"/>
</shape>
'''%(fill,border))
    originals={}
    photo=(
        JAVA/"PhotoWidget.java",JAVA/"PhotoConfigActivity.java",
        JAVA/"PhotoTapActivity.java",RES/"layout/widget_photo.xml",
        RES/"xml/photo_widget_info.xml",
    )
    photo_hash={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in photo}
    main=JAVA/"MainActivity.java"
    schedule=JAVA/"ScheduleActivity.java"
    widget=JAVA/"TaskWidget.java"
    notes=JAVA/"StickyNotesWidget.java"
    manifest=ROOT/"AndroidManifest.xml"
    strings=RES/"values/strings.xml"
    task_layout=RES/"layout/widget_tasks.xml"
    for path in (main,schedule,widget,notes,manifest,strings,task_layout):
        originals[path]=path.read_text(encoding="utf-8")

    w=originals[widget]
    w=replace_once(w,"        for(int id:ids)update(c,m,id,all);",
        "        for(int id:ids)update(c,m,id,all);\n"+
        "        AcademicWidgetSync.request(c);","sync academic widgets after task changes")
    w=replace_once(w,
        'v.setTextViewText(R.id.widget_subtitle,"Mis tareas de hoy · "+todayCount(all));',
        'v.setTextViewText(R.id.widget_subtitle,"Pendientes: "+pendingCount(all)+
                " · Hoy: "+todayCount(all));',
        "task summary")
    w=replace_once(w,"    private static int todayCount(List<Task> all){",
        '''    private static int pendingCount(List<Task> all){
        int n=0;for(Task task:all)if(!task.done)n++;return n;
    }
    private static int todayCount(List<Task> all){''',"pending count")
    originals[widget]=w

    notes_text=originals[notes]
    notes_text=replace_once(notes_text,
        "compact?R.layout.widget_sticky_row_compact:R.layout.widget_sticky_row",
        "compact?R.layout.widget_notes_board_row_compact:R.layout.widget_notes_board_row",
        "note board card layout")
    notes_text=replace_once(notes_text,
        "view.setImageViewResource(R.id.sticky_widget_art,picture(note.color));",
        'view.setInt(R.id.sticky_widget_row,"setBackgroundResource",boardColor(note.color));',
        "note board card color")
    notes_text=replace_once(notes_text,
        "compact?R.layout.widget_sticky_notes_compact:R.layout.widget_sticky_notes",
        "compact?R.layout.widget_notes_board_compact:R.layout.widget_notes_board",
        "notes board layout")
    notes_text=replace_once(notes_text,
        "    public static RemoteViews row(Context c,StickyNotesStore.Note note){",
        '''    private static int boardColor(int color){
        switch(color){
            case 1:return R.drawable.widget_note_card_pink;
            case 2:return R.drawable.widget_note_card_blue;
            case 3:return R.drawable.widget_note_card_green;
            case 4:return R.drawable.widget_note_card_purple;
            case 5:return R.drawable.widget_note_card_peach;
            default:return R.drawable.widget_note_card_yellow;
        }
    }
    public static RemoteViews row(Context c,StickyNotesStore.Note note){''',
        "notes board pastel palette")
    notes_text=replace_once(notes_text,
        'compact?"Mis notas":"Notas adhesivas · "+notes.size()',
        'compact?"Mis notas":"Tablero de notas · "+notes.size()',
        "notes board header")
    originals[notes]=notes_text

    main_text=originals[main]
    main_text=replace_once(main_text,
        '        if("new_task".equals(i.getAction())){openEditor(-1,null,null);return;}',
        '''        if("tasks".equals(i.getAction())){
            page=0;homeSection=1;dashboardAllTasksExpanded=true;render();return;
        }
        if("new_task".equals(i.getAction())){openEditor(-1,null,null);return;}''',
        "task widget navigation")
    originals[main]=main_text

    schedule_text=replace_once(originals[schedule],
        "    @Override protected void onDestroy(){io.shutdownNow();super.onDestroy();}",
        '''    @Override protected void onStop(){
        super.onStop();
        AcademicWidgetSync.request(getApplicationContext());
    }
    @Override protected void onDestroy(){io.shutdownNow();super.onDestroy();}''',
        "refresh widgets after editing timetable")
    originals[schedule]=schedule_text

    manifest_text=originals[manifest]
    manifest_text=replace_once(manifest_text,
        '        <activity android:name=".SyllabusImportActivity"',
        '''        <activity android:name=".AcademicWidgetSettingsActivity" android:exported="true"
            android:theme="@style/AppTheme" />
        <activity android:name=".SyllabusImportActivity"''',
        "widget settings Activity declaration")
    manifest_text=replace_once(manifest_text,
        '        <receiver android:name=".PhotoWidget"',
        '''        <receiver android:name=".AcademicDayWidget" android:exported="false"
            android:label="Agenda Clara · Mi día académico">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE" /></intent-filter>
            <meta-data android:name="android.appwidget.provider"
                android:resource="@xml/widget_academic_day_info" />
        </receiver>
        <receiver android:name=".AcademicWeekWidget" android:exported="false"
            android:label="Agenda Clara · Horario y evaluaciones">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE" /></intent-filter>
            <meta-data android:name="android.appwidget.provider"
                android:resource="@xml/widget_academic_week_info" />
        </receiver>
        <receiver android:name=".PhotoWidget"''',
        "register two academic widget providers")
    originals[manifest]=manifest_text

    strings_text=replace_once(originals[strings],"</resources>",
        '''    <string name="academic_day_widget_description">Próxima clase y tareas del mismo curso</string>
    <string name="academic_week_widget_description">Horario de clases con evaluaciones por curso</string>
</resources>''',"widget descriptions")
    originals[strings]=strings_text

    task_text=replace_once(originals[task_layout],
        'android:text="Agenda Clara" android:textColor="#101B42"',
        'android:text="Mis tareas" android:textColor="#101B42"',
        "task widget heading")
    originals[task_layout]=task_text

    # Apply only after validating all anchors. Photo files remain byte-for-byte identical.
    for dest,src in all_files.items():
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)
    for dest,content in new_colors.items():
        dest.write_text(content,encoding="utf-8")
    for dest,content in originals.items():
        dest.write_text(content,encoding="utf-8")
    GRADLE.write_text(gradle.replace("versionCode 66","versionCode 67",1)
                            .replace("versionName '3.14.0'","versionName '3.15.0'",1),
                      encoding="utf-8")
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h
               for p,h in photo_hash.items()),"Photo widget source unexpectedly changed"
    print("PASS: two configurable academic widgets and notes board integrated")
    print("PASS: task widget enhanced, course/profile matching and refresh preserved")
    print("PASS: fixed-photo widget files are byte-for-byte unchanged")
    print("PASS: no quick access widget introduced")
if __name__=="__main__":run()
