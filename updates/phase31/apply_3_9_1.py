#!/usr/bin/env python3
"""3.9.1: add resizable sticky-note widget without touching task widgets/navigation."""
from pathlib import Path

ROOT=Path("AgendaClara/app/src/main")
SRC=ROOT/"java/pe/agendaclara/app"
STAGE=Path(__file__).resolve().parent

def one(value,old,new,label):
    if value.count(old)!=1:
        raise RuntimeError(f"phase31 {label}: expected one anchor, found {value.count(old)}")
    return value.replace(old,new,1)

def apply():
    candidates={
        "StickyNotesStore.java":SRC/"StickyNotesStore.java",
        "StickyNotesUi.java":SRC/"StickyNotesUi.java",
        "MainActivity.java":SRC/"MainActivity.java",
        "CategoryRegistry.java":SRC/"CategoryRegistry.java",
        "SystemReceiver.java":SRC/"SystemReceiver.java",
        "AndroidManifest.xml":ROOT/"AndroidManifest.xml",
        "strings.xml":ROOT/"res/values/strings.xml",
        "build.gradle":Path("AgendaClara/app/build.gradle"),
    }
    s={key:path.read_text(encoding="utf-8") for key,path in candidates.items()}
    s["StickyNotesStore.java"]=one(s["StickyNotesStore.java"],
        '    public synchronized List<Note> inCategory(String category){',
        '    public synchronized List<Note> all(){return fetch(null,null);}\n'
        '    public synchronized List<Note> inCategory(String category){',
        "read-only all-notes collection")

    main=s["MainActivity.java"]
    main=one(main,
        '        if("new_task".equals(i.getAction())){openEditor(-1,null,null);return;}',
        '''        if("new_sticky_note".equals(i.getAction())){
            page=0;render();StickyNotesUi.showEditor(this,null);return;
        }
        if("sticky_notes".equals(i.getAction())){
            page=0;selectedCategory="Notas";render();return;
        }
        if("sticky_widget_note".equals(i.getAction())){
            StickyNotesStore.Note note=StickyNotesStore.get(this).find(
                i.getLongExtra("sticky_note_id",-1));
            if(note!=null){
                page=0;selectedCategory=note.category;render();
                StickyNotesUi.showEditor(this,note);
            }else{page=0;render();toast("La nota ya no está disponible.");}
            return;
        }
        if("new_task".equals(i.getAction())){openEditor(-1,null,null);return;}''',
        "safe widget create/open routing")
    main=one(main,
        'Reminders.rebuild(this);TaskWidget.refresh(this);',
        'Reminders.rebuild(this);TaskWidget.refresh(this);StickyNotesWidget.refresh(this);',
        "refresh both widgets after resuming")
    s["MainActivity.java"]=main

    note=s["StickyNotesUi.java"]
    note=one(note,
        'StickyNotesStore.get(a).delete(original.id);dialog.dismiss();',
        'StickyNotesStore.get(a).delete(original.id);'
        'new Thread(()->StickyNotesWidget.refresh(a.getApplicationContext()),'
        '"sticky-widget-sync").start();dialog.dismiss();',
        "widget updates when a note is removed")
    note=one(note,
        'catch(RuntimeException e){a.toast("No se pudo guardar la nota.");return;}\n                dialog.dismiss();',
        'catch(RuntimeException e){a.toast("No se pudo guardar la nota.");return;}\n'
        '                new Thread(()->StickyNotesWidget.refresh(a.getApplicationContext()),'
        '"sticky-widget-sync").start();\n                dialog.dismiss();',
        "widget updates after saving a note")
    s["StickyNotesUi.java"]=note

    categories=s["CategoryRegistry.java"]
    categories=one(categories,'        store(c,entries);return true;',
        '        store(c,entries);StickyNotesWidget.refresh(c);return true;',
        "widget update on category rename")
    categories=one(categories,'entries.remove(i);store(c,entries);return true;',
        'entries.remove(i);store(c,entries);StickyNotesWidget.refresh(c);return true;',
        "widget update on category deletion")
    s["CategoryRegistry.java"]=categories

    system=s["SystemReceiver.java"]
    system=one(system,'TaskWidget.refresh(c);PhotoWidget.refresh(c);',
        'TaskWidget.refresh(c);StickyNotesWidget.refresh(c);PhotoWidget.refresh(c);',
        "update after boot/time changes")
    s["SystemReceiver.java"]=system

    manifest=s["AndroidManifest.xml"]
    manifest=one(manifest,
        '        <service android:name=".TaskWidgetService" android:exported="false" '
        'android:permission="android.permission.BIND_REMOTEVIEWS" />',
        '        <service android:name=".TaskWidgetService" android:exported="false" '
        'android:permission="android.permission.BIND_REMOTEVIEWS" />\n'
        '        <service android:name=".StickyNotesWidgetService" android:exported="false" '
        'android:permission="android.permission.BIND_REMOTEVIEWS" />',
        "Android remote list service")
    manifest=one(manifest,
        '        <receiver android:name=".PhotoWidget" android:exported="false" android:label="Agenda Clara · foto">',
        '''        <receiver android:name=".StickyNotesWidget" android:exported="false"
            android:label="Agenda Clara · notas adhesivas">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE" /></intent-filter>
            <meta-data android:name="android.appwidget.provider"
                android:resource="@xml/sticky_notes_widget_info" />
        </receiver>
        <receiver android:name=".PhotoWidget" android:exported="false" android:label="Agenda Clara · foto">''',
        "register separate widget provider")
    s["AndroidManifest.xml"]=manifest
    s["strings.xml"]=one(s["strings.xml"],'</resources>',
        '<string name="sticky_widget_description">Notas adhesivas por fecha, '
        'con colores, vista previa y botón para crear notas.</string></resources>',
        "widget description in launcher")
    build=s["build.gradle"]
    build=one(build,'versionCode 31','versionCode 32',"version code")
    build=one(build,"versionName '3.9.0'","versionName '3.9.1'","version name")
    s["build.gradle"]=build

    generated={
        "StickyNotesWidget.java":SRC/"StickyNotesWidget.java",
        "StickyNotesWidgetService.java":SRC/"StickyNotesWidgetService.java",
        "widget_sticky_notes.xml":ROOT/"res/layout/widget_sticky_notes.xml",
        "widget_sticky_row.xml":ROOT/"res/layout/widget_sticky_row.xml",
        "sticky_notes_widget_info.xml":ROOT/"res/xml/sticky_notes_widget_info.xml",
    }
    for name,path in generated.items():
        if path.exists():raise RuntimeError("Refusing to overwrite widget file "+str(path))
        if not (STAGE/name).is_file():raise RuntimeError("Missing widget template "+name)
    oldnav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
    if 'UiDesign.OutlineIcon' not in oldnav:
        raise RuntimeError("Previously approved navigation outline icons missing")
    for key,path in candidates.items():path.write_text(s[key],encoding="utf-8")
    for name,path in generated.items():
        path.write_bytes((STAGE/name).read_bytes())
    print("PASS phase31: resizable sticky widget, +, dates, color PNG and live sync; task widget/navigation unchanged")

if __name__=="__main__":apply()
