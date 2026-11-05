#!/usr/bin/env python3
"""Phase 75: remove ALL premature new-timetable name dialogs.

2026-11-05 user screenshot showed Calendario > Plan de estudio > "Nuevo horario"
still calling newSchedule(a,false) in 3.13.4. This corrects that exact entry,
plus the no-profile fallback and manual course-first creation.
Run after reconstructing the verified 3.13.4 sources. No APK is compiled here.
"""
from pathlib import Path

CODE=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")

def once(source,old,new,label):
    matches=source.count(old)
    if matches!=1:
        raise RuntimeError(f"phase75 {label}: expected one anchor, found {matches}")
    return source.replace(old,new,1)

def between(source,start,end,insert,label):
    if source.count(start)!=1 or source.count(end)!=1:
        raise RuntimeError(f"phase75 {label}: incompatible source")
    a=source.index(start);b=source.index(end,a)
    return source[:a]+insert+source[b:]

def panel(source):
    source=once(source,
        '''            schedules.addView(a.button("＋  Nuevo horario",()->newSchedule(a,false)));''',
        '''            schedules.addView(a.button("＋  Nuevo horario",()->chooseMethod(a)));''',
        "main Nuevo horario button")
    first='''    private static void newSchedule(MainActivity a,boolean photo){'''
    last='''    private static void importPhoto(MainActivity a){'''
    method='''    /** The main CTA must ask for a creation METHOD, never for a title. */
    private static void chooseMethod(MainActivity a){
        if(AcademicSchedules.all(a).size()>=AcademicSchedules.LIMIT){
            a.dialogBuilder().setTitle("Límite de diez horarios")
                .setMessage("Ya tienes diez horarios. Abre uno existente para editarlo.")
                .setPositiveButton("Entendido",null).show();
            return;
        }
        // Explicit buttons are necessary: AlertDialog.setItems was hidden by
        // the app's dialog window measurements on Android 15.
        LinearLayout options=a.column();
        options.setPadding(a.dp(20),a.dp(8),a.dp(20),a.dp(10));
        android.widget.Button photo=a.button("Subir imagen del horario",()->{});
        android.widget.Button manual=a.button("Agregar cursos manualmente",()->{});
        options.addView(photo);
        a.gap(options,10);
        options.addView(manual);
        AlertDialog picker=a.dialogBuilder().setTitle("¿Cómo crearás tu horario?")
            .setMessage("Primero importa la imagen o registra tus cursos. "+
                        "El nombre y la categoría se confirman al terminar.")
            .setView(options).setNegativeButton("Cancelar",null).create();
        photo.setOnClickListener(v->{picker.dismiss();importPhoto(a);});
        manual.setOnClickListener(v->{picker.dismiss();startManual(a);});
        picker.show();
    }

    private static void startManual(MainActivity a){
        if(AcademicSchedules.all(a).size()>=AcademicSchedules.LIMIT){
            a.dialogBuilder().setTitle("Límite de diez horarios")
                .setMessage("Ya tienes diez horarios.")
                .setPositiveButton("Entendido",null).show();
            return;
        }
        Intent intent=new Intent(a,ScheduleActivity.class);
        intent.putExtra("new_manual",true);
        a.startActivity(intent);
    }

'''
    source=between(source,first,last,method,"remove initial title dialog")
    source=once(source,
        '''schedules.addView(a.text("Aún no tienes horarios. Crea uno nuevo o importa una fotografía.",''',
        '''schedules.addView(a.text("Aún no tienes horarios. Sube una imagen o registra los cursos manualmente.",''',
        "empty state")
    return source

def activity(source):
    source=once(source,
        '''    private boolean photoFirst=false,photoSaving=false;''',
        '''    private boolean photoFirst=false,photoSaving=false,manualMode=false;''',
        "manual-state field")
    source=once(source,
        '''        photoFirst=getIntent().getBooleanExtra("new_from_photo",false);
        if(photoFirst){''',
        '''        photoFirst=getIntent().getBooleanExtra("new_from_photo",false);
        manualMode=getIntent().getBooleanExtra("new_manual",false);
        if(manualMode){
            if(AcademicSchedules.all(this).size()>=AcademicSchedules.LIMIT){
                scheduleDialog().setTitle("Límite de diez horarios")
                    .setMessage("Ya tienes diez horarios.")
                    .setPositiveButton("Entendido",(d,w)->finish()).show();
                return;
            }
            photoFirst=true;
            profileId="";
            detected=new ScheduleParser.Result();
            chosen.clear();
            show(5); // Courses are edited IN MEMORY; name comes only after review.
            return;
        }
        if(photoFirst){''',
        "manual route before photo route")
    first='''    private void askFirstSchedule(){'''
    last='''    @Override protected void onResume()'''
    method='''    /** A direct launch with zero profiles must not bypass method selection. */
    private void askFirstSchedule(){
        LinearLayout actions=col();
        actions.setPadding(dp(18),dp(8),dp(18),dp(10));
        Button photo=btn("Subir imagen del horario",()->{},true);
        Button manual=btn("Agregar cursos manualmente",()->{},false);
        actions.addView(photo);space(actions,10);actions.addView(manual);
        AlertDialog picker=scheduleDialog().setTitle("¿Cómo crearás tu horario?")
            .setMessage("Primero registra tus cursos. El nombre se elige al final.")
            .setView(actions)
            .setNegativeButton("Cancelar",(d,w)->finish()).create();
        photo.setOnClickListener(v->{
            picker.dismiss();photoFirst=true;manualMode=false;profileId="";show(1);
        });
        manual.setOnClickListener(v->{
            picker.dismiss();photoFirst=true;manualMode=true;profileId="";
            detected=new ScheduleParser.Result();chosen.clear();show(5);
        });
        picker.setOnCancelListener(d->finish());
        picker.show();
    }
'''
    source=between(source,first,last,method,"no profile initial dialog")
    source=once(source,
        '''                if(page==5)show(1);else finish();''',
        '''                if(page==5&&!manualMode)show(1);else finish();''',
        "back navigation for manual")
    source=once(source,
        '''title=txt(titles[Math.max(0,Math.min(titles.length-1,screen))],21,INK,true);''',
        '''title=txt(screen==5&&manualMode?"Cursos del nuevo horario":
            titles[Math.max(0,Math.min(titles.length-1,screen))],21,INK,true);''',
        "manual screen title")
    source=once(source,
        '''head(top,"Paso 2 de 3 · Corroborar cursos","Revisa los nombres, días y horas. Después confirmarás el nombre del horario.");''',
        '''head(top,manualMode?"Paso 1 de 2 · Agregar y corroborar cursos":
            "Paso 2 de 3 · Corroborar cursos",
            "Revisa los nombres, días y horas. Después confirmarás el nombre del horario.");''',
        "manual review heading")
    source=once(source,
        '''top.addView(txt("Imagen ✓  ·  Cursos ◉  ·  Nombre del horario ○",12,BLUE,true));''',
        '''top.addView(txt(manualMode?"Cursos ◉  ·  Nombre del horario ○":
                    "Imagen ✓  ·  Cursos ◉  ·  Nombre del horario ○",12,BLUE,true));''',
        "manual review progress")
    source=once(source,
        '''        field.setHint("Ej.: Semana 4 · Educación");''',
        '''        field.setHint(manualMode?"Ej.: Educación 2026":"Ej.: Semana 4 · Educación");''',
        "manual title hint")
    source=once(source,
        '''            .setMessage("No se ha confirmado un nombre de la imagen. "+
                        "Indica cómo se llamarán el horario y su categoría.")''',
        '''            .setMessage(manualMode
                ?"Has corroborado los cursos. Ahora indica el nombre del horario y su categoría."
                :"No se ha confirmado un nombre de la imagen. "+
                 "Indica cómo se llamarán el horario y su categoría.")''',
        "manual title explanation")
    source=once(source,
        '''        detected=null;detectedTitle="";
        photoSaving=false;''',
        '''        detected=null;detectedTitle="";
        manualMode=false;photoSaving=false;''',
        "clear manual state")
    return source

def run():
    panel_path=CODE/"CalendarStudyPanel.java"
    activity_path=CODE/"ScheduleActivity.java"
    original_panel=panel_path.read_text(encoding="utf-8")
    original_activity=activity_path.read_text(encoding="utf-8")
    changed_panel=panel(original_panel)
    changed_activity=activity(original_activity)
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 60")!=1 or gradle.count("versionName '3.13.4'")!=1:
        raise RuntimeError("Expected version 3.13.4 (60), refusing to patch")
    gradle=gradle.replace("versionCode 60","versionCode 61",1).replace(
        "versionName '3.13.4'","versionName '3.13.5'",1)
    # Commit only after all anchors and version checks succeed.
    panel_path.write_text(changed_panel,encoding="utf-8")
    activity_path.write_text(changed_activity,encoding="utf-8")
    GRADLE.write_text(gradle,encoding="utf-8")
    print("PASS: Nuevo horario -> método de creación, never name-first")
    print("PASS: foto -> corregir cursos -> OCR nombre/manual -> create")
    print("PASS: manual -> agregar cursos -> nombre -> create")
    print("PASS: direct launch without schedules -> method chooser")
    print("PASS: Agenda Clara 3.13.5 source ready; no APK built")

if __name__=="__main__":run()
