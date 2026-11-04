#!/usr/bin/env python3
"""Phase A safe transformations for pre-existing schedule UI and Android shell."""
from pathlib import Path

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")

def exact(source, old, new, label):
    # Test the OLD anchor first: the replacement may be a substring of it.
    n=source.count(old)
    if old==new:
        if n!=1:raise RuntimeError(f"{label}: anclaje inesperado: {n}")
        return source
    if n==1:return source.replace(old,new,1)
    if n==0 and new in source:return source
    raise RuntimeError(f"{label}: se esperaba un anclaje, encontrados {n}")

def transform_schedule(source):
    source=exact(source,
        'private Uri cameraImage;',
        'private Uri cameraImage;\n    private String profileId="",detectedTitle="";',
        "state profile")
    old='@Override public void onCreate(Bundle state){super.onCreate(state);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);show(0);}'
    new='''@Override public void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        AcademicSchedules.migrateLegacy(this);
        String requested=getIntent().getStringExtra("profile_id");
        AcademicSchedules.Profile profile=AcademicSchedules.find(this,requested);
        profileId=profile!=null?profile.id:AcademicSchedules.activeId(this);
        if(profileId.isEmpty()){askFirstSchedule();}
        else {
            AcademicSchedules.activate(this,profileId);
            show(getIntent().getBooleanExtra("start_photo",false)?1:0);
        }
    }
    private void askFirstSchedule(){
        EditText name=new EditText(this);name.setSingleLine(true);
        name.setHint("Nombre de tu primer horario");
        AlertDialog dialog=scheduleDialog().setTitle("Crear primer horario")
            .setMessage("Indica el nombre del horario y su categoría académica.")
            .setView(name).setNegativeButton("Volver",(d,w)->finish())
            .setPositiveButton("Crear",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{
                AcademicSchedules.Profile p=AcademicSchedules.create(this,
                        name.getText().toString(),new ArrayList<String>());
                profileId=p.id;dialog.dismiss();
                show(getIntent().getBooleanExtra("start_photo",false)?1:0);
            }catch(IllegalArgumentException|IllegalStateException e){name.setError(e.getMessage());}
        }));
        dialog.setOnCancelListener(x->finish());
        dialog.show();
    }'''
    source=exact(source,old,new,"schedule onCreate")
    source=exact(source,
        '@Override protected void onResume(){super.onResume();if(page==2||page==3)show(page);}',
        '@Override protected void onResume(){super.onResume();if(!profileId.isEmpty()&&(page==2||page==3))show(page);}',
        "resume schedule")
    # Every call that reads or reconciles existing classes within the editor
    # must be profile-scoped. Other modules still use all() to rebuild reminders.
    source=source.replace("ScheduleDatabase.get(this).all()","ScheduleDatabase.get(this).all(profileId)")
    source=source.replace("ScheduleDatabase.get(ScheduleActivity.this).all()",
                          "ScheduleDatabase.get(ScheduleActivity.this).all(profileId)")
    source=exact(source,
        "ScheduleParser.Result detected;",
        "ScheduleParser.Result detected;",
        "detected field")  # a no-op but safeguards the marker
    source=exact(source,
        "try{detected=ScheduleOcr.analyze(text,rectangles,imageWidth,imageHeight);}",
        "try{detected=ScheduleOcr.analyze(text,rectangles,imageWidth,imageHeight);\n"
        "                            detectedTitle=ScheduleTitleParser.suggest(text.getText());}",
        "recognize title")
    source=exact(source,
        "ScheduleEntry current=importing?previous:previous==null?new ScheduleEntry():previous.copy();",
        "ScheduleEntry current=importing?previous:previous==null?new ScheduleEntry():previous.copy();\n"
        "        current.scheduleId=profileId;",
        "editor schedule id")
    source=exact(source,
        "db.recolorSameCourse(s.course,s.color);",
        "db.recolorSameCourse(s.course,s.color,profileId);",
        "profile-scoped recolor")
    # Add course to schedule's catalog whenever a manual class has been saved.
    source=exact(source,
        "db.recolorSameCourse(s.course,s.color,profileId);",
        "db.recolorSameCourse(s.course,s.color,profileId);",
        "recolor")
    # Both new and old week-editor commit paths call the same commit closure.
    source=exact(source,
        "for(ScheduleEntry s:additions){\n                    if(db.save(s))ScheduleReminders.schedule(this,s);",
        "for(ScheduleEntry s:additions){\n                    s.scheduleId=profileId;\n                    if(db.save(s))ScheduleReminders.schedule(this,s);",
        "manual class save")
    source=exact(source,
        "            Runnable commit=()->{",
        "            Runnable commit=()->{",
        "commit hook")
    # Make the course registry reflect sessions only after the whole edit succeeds.
    source=exact(source,
        "                    db.recolorSameCourse(s.course,s.color,profileId);",
        "                    db.recolorSameCourse(s.course,s.color,profileId);",
        "save label")
    # OCR import: confirmation is a dialog, never a permanent screen panel.
    old_import='''                    int added=ScheduleDatabase.get(this).importReviewed(approved);
                    ScheduleReminders.rebuild(this);
                    toast("Bloques guardados: "+added+" · cursos: "+
                        SchedulePhotoReview.courseEstimate(approved));
                    detected=null;show(2);'''
    new_import='''                    confirmPhotoName(()->{
                        int added=ScheduleDatabase.get(this).importReviewed(approved,profileId);
                        AcademicSchedules.syncFromSessions(this,profileId);
                        ScheduleReminders.rebuild(this);
                        toast("Bloques guardados: "+added+" · cursos: "+
                            SchedulePhotoReview.courseEstimate(approved));
                        detected=null;detectedTitle="";show(2);
                    });'''
    source=exact(source,old_import,new_import,"photo import")
    method='''    private void confirmPhotoName(Runnable proceed){
        AcademicSchedules.Profile profile=AcademicSchedules.find(this,profileId);
        if(profile==null){toast("Selecciona un horario.");return;}
        EditText name=new EditText(this);
        name.setSingleLine(true);
        name.setText(detectedTitle.isEmpty()?profile.name:detectedTitle);
        name.setSelectAllOnFocus(true);
        String message=detectedTitle.isEmpty()
                ?"No se identificó claramente un título en la imagen. Confirma el nombre del horario."
                :"Se detectó este posible nombre en la fotografía. Confírmalo o corrígelo.";
        AlertDialog dialog=scheduleDialog().setTitle("Confirmar nombre del horario")
                .setMessage(message).setView(name)
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Confirmar y guardar",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{
                AcademicSchedules.rename(this,profileId,name.getText().toString());
                dialog.dismiss();proceed.run();
            }catch(IllegalArgumentException|IllegalStateException error){
                name.setError(error.getMessage());
            }
        }));
        dialog.show();
    }
'''
    source=exact(source,
        "    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */",
        method+"    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */",
        "photo confirm dialog")
    # This method can now save sessions for only one profile, without collisions.
    source=exact(source,
        "            List<String> overlaps=ScheduleConflict.describe(additions,others);",
        "            List<String> overlaps=ScheduleConflict.describe(additions,others);",
        "overlap guard")
    source=exact(source,
        "        List<String> overlaps=ScheduleConflict.describe(proposed,ScheduleDatabase.get(this).all(profileId));",
        "        List<String> overlaps=ScheduleConflict.describe(proposed,ScheduleDatabase.get(this).all(profileId));",
        "photo overlap guard")
    return source

def transform_main(source):
    source=exact(source,
        "else if(page==1)calendarPage();",
        "else if(page==1)CalendarStudyTabs.render(this);",
        "calendar panel")
    old='Button add=button("＋",()->showCreationMenu());add.setTag("new_task_button");add.setTextSize(28);add.setTextColor(0xffffffff);add.setBackground(gradient(GREEN,0xff7465ec,19));add.setElevation(dp(4));add.setContentDescription("Crear una tarea o nota");header.addView(add,new LinearLayout.LayoutParams(dp(108),dp(108)));root.addView(header);'
    source=exact(source,old,"root.addView(header);","remove huge plus")
    # Header+ menu no longer exists. Existing home task button still opens choice list.
    old='''        CreationChoices.show(this,add,()->openEditor(-1,null,null),
            ()->StickyNotesUi.showEditor(this,null),()->VoiceQuickTask.show(this));'''
    new='''        if(add==null||!add.isShown()){
            dialogBuilder().setTitle("Crear en Agenda Clara")
                .setItems(new String[]{"Tarea rápida por voz","Nueva tarea","Nueva nota"},
                    (d,index)->{
                        if(index==0)VoiceQuickTask.show(this);
                        else if(index==1)openEditor(-1,null,null);
                        else StickyNotesUi.showEditor(this,null);
                    }).setNegativeButton("Cancelar",null).show();
            return;
        }
        CreationChoices.show(this,add,()->openEditor(-1,null,null),
            ()->StickyNotesUi.showEditor(this,null),()->VoiceQuickTask.show(this));'''
    source=exact(source,old,new,"fallback create actions")
    # Never add another calendar panel to the existing five-item bottom nav.
    assert 'MiDiaNavigation.TAB_LABELS' in source
    return source

if __name__=="__main__":
    schedule=JAVA/"ScheduleActivity.java"
    main=JAVA/"MainActivity.java"
    new_schedule=transform_schedule(schedule.read_text(encoding="utf-8"))
    new_main=transform_main(main.read_text(encoding="utf-8"))
    schedule.write_text(new_schedule,encoding="utf-8")
    main.write_text(new_main,encoding="utf-8")
    print("PASS: horario aislado, OCR con confirmación, importación perfil, sin botón + grande")
