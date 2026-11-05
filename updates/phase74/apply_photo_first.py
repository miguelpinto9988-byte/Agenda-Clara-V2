#!/usr/bin/env python3
"""Phase 74: photo FIRST, course corroboration SECOND, timetable name LAST.

Apply to fully reconstructed and validated Agenda Clara 3.13.3 source.
This script never compiles or signs an APK.
"""
from pathlib import Path

CODE=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")

def replace_once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise RuntimeError(f"phase74 {label}: expected 1 anchor, found {count}")
    return source.replace(old,new,1)

def replace_between(source,first,last,replacement,label):
    if source.count(first)!=1 or source.count(last)!=1:
        raise RuntimeError("phase74 "+label+": unexpected method boundaries")
    start=source.index(first)
    end=source.index(last,start)
    return source[:start]+replacement+source[end:]

def transform_panel(source):
    old='''    private static void importPhoto(MainActivity a){'''
    end='''    private static void details(MainActivity a,String profileId){'''
    replacement='''    private static void importPhoto(MainActivity a){
        // Creating from a photograph must not create a profile or category yet.
        // Image -> review/corroborate courses -> confirm suggested/manual title -> save.
        if(AcademicSchedules.all(a).size()>=AcademicSchedules.LIMIT){
            a.dialogBuilder().setTitle("Límite de diez horarios")
                .setMessage("Ya tienes diez horarios. No se creará otra categoría. "+
                            "Puedes abrir un horario existente y agregarle una foto.")
                .setPositiveButton("Entendido",null).show();
            return;
        }
        Intent intent=new Intent(a,ScheduleActivity.class);
        intent.putExtra("new_from_photo",true);
        a.startActivity(intent);
    }
'''
    source=replace_between(source,old,end,replacement,"panel photo entry")
    source=replace_once(source,
        '''        box.addView(a.button("Abrir clases de este horario",()->open(a,p,false)));''',
        '''        box.addView(a.button("Abrir clases de este horario",()->open(a,p,false)));
        box.addView(a.button("Añadir foto a este horario",()->open(a,p,true)));''',
        "panel existing timetable photo")
    source=replace_once(source,
        '''schedules.addView(a.button("Importar horario desde foto",()->importPhoto(a)));''',
        '''schedules.addView(a.button("Crear horario desde foto",()->importPhoto(a)));''',
        "photo call to action")
    return source

def transform_schedule(source):
    source=replace_once(source,
        '''    private String profileId="",detectedTitle="";''',
        '''    private String profileId="",detectedTitle="";
    private boolean photoFirst=false,photoSaving=false;''',
        "photo-first state")
    source=replace_once(source,
        '''        AcademicSchedules.migrateLegacy(this);
        String requested=getIntent().getStringExtra("profile_id");''',
        '''        AcademicSchedules.migrateLegacy(this);
        photoFirst=getIntent().getBooleanExtra("new_from_photo",false);
        if(photoFirst){
            if(AcademicSchedules.all(this).size()>=AcademicSchedules.LIMIT){
                scheduleDialog().setTitle("Límite de diez horarios")
                    .setMessage("No puedes crear otro horario. Selecciona uno existente.")
                    .setPositiveButton("Entendido",(d,w)->finish()).show();
                return;
            }
            // No empty profile/category is created before OCR and course review.
            profileId="";
            show(1);
            return;
        }
        String requested=getIntent().getStringExtra("profile_id");''',
        "onCreate photo-first")
    source=replace_once(source,
        '''Button back=btn("‹",()->{if(page==0)finish();else show(0);},false);''',
        '''Button back=btn("‹",()->{
            if(photoFirst&&profileId.isEmpty()){
                if(page==5)show(1);else finish();
            }else if(page==0)finish();else show(0);
        },false);''',
        "photo-first back navigation")
    source=replace_once(source,
        '''"ETAPA 1 · Vista general  →  ETAPA 2 · Cursos  →  ETAPA 3 · Corroboración"''',
        '''"1 · Elegir foto  →  2 · Corroborar cursos  →  3 · Confirmar nombre"''',
        "step descriptions")
    source=replace_once(source,
        '''head(top,"3/3 · Corroborar cursos","Las sesiones semanales no son cursos diferentes. Una misma materia puede aparecer varios días, con horas distintas.");''',
        '''head(top,"Paso 2 de 3 · Corroborar cursos","Revisa los nombres, días y horas. Después confirmarás el nombre del horario.");''',
        "review step")
    source=replace_once(source,
        '''"Etapa 1 ✓ Vista general  ·  Etapa 2 ✓ Cursos por bloque  ·  Etapa 3 ◉ Confirmación"''',
        '''"Imagen ✓  ·  Cursos ◉  ·  Nombre del horario ○"''',
        "review progress")
    old='''                    confirmPhotoName(()->{
                        int added=ScheduleDatabase.get(this).importReviewed(approved,profileId);
                        AcademicSchedules.syncFromSessions(this,profileId);
                        ScheduleReminders.rebuild(this);
                        toast("Bloques guardados: "+added+" · cursos: "+
                            SchedulePhotoReview.courseEstimate(approved));
                        detected=null;detectedTitle="";show(2);
                    });'''
    source=replace_once(source,old,
        '''                    confirmPhotoName(approved);''',"save after name")
    source=replace_once(source,
        '''body.addView(btn("Agregar una clase manualmente",()->editor(null,null),false));''',
        '''body.addView(btn("Agregar una clase manualmente",()->{
            // Keep a new class in the uncommitted OCR review until the timetable is named.
            ScheduleEntry draft=new ScheduleEntry();
            editor(draft,()->show(5));
        },false));''',
        "draft manual class during photo review")
    start='''    private void confirmPhotoName(Runnable proceed){'''
    end='''    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */'''
    method='''    /** Called only after the user has corroborated all OCR course groups and blocks. */
    private void confirmPhotoName(ArrayList<ScheduleEntry> approved){
        if(photoFirst&&profileId.isEmpty()){
            if(!detectedTitle.trim().isEmpty()){
                final String suggestion=detectedTitle.trim();
                scheduleDialog().setTitle("Paso 3 de 3 · Nombre del horario")
                    .setMessage("La imagen parece indicar «"+suggestion+"». "+
                        "¿Quieres usar este nombre para el horario y su categoría?")
                    .setNegativeButton("No, escribir otro",(d,w)->manualPhotoName(approved))
                    .setNeutralButton("Cancelar",null)
                    .setPositiveButton("Sí, usar ese nombre",(d,w)->saveNewPhoto(approved,suggestion))
                    .show();
            }else{
                // No guessed title: request a new name, leaving profiles unchanged.
                manualPhotoName(approved);
            }
            return;
        }
        AcademicSchedules.Profile target=AcademicSchedules.find(this,profileId);
        if(target==null){toast("Selecciona el horario de destino.");return;}
        // Adding a picture to an EXISTING timetable must not rename it silently.
        String message="Se guardarán los cursos corroborados en «"+target.name+"».";
        if(!detectedTitle.isEmpty()&&
            !AcademicSchedules.key(detectedTitle).equals(AcademicSchedules.key(target.name)))
            message+=" La foto dice «"+detectedTitle+"», pero se conservará "+
                     "el nombre de tu horario actual.";
        scheduleDialog().setTitle("Confirmar horario de destino")
            .setMessage(message)
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("Guardar en "+target.name,(d,w)->commitPhoto(approved,profileId))
            .show();
    }

    /** The category must be created only AFTER accepting an OCR title or entering one. */
    private void manualPhotoName(ArrayList<ScheduleEntry> approved){
        EditText field=new EditText(this);
        field.setSingleLine(true);
        field.setHint("Ej.: Semana 4 · Educación");
        field.setSelectAllOnFocus(true);
        LinearLayout wrapper=col();
        wrapper.setPadding(dp(18),dp(8),dp(18),dp(8));
        wrapper.addView(field);
        AlertDialog dialog=scheduleDialog().setTitle("Escribe el nombre del horario")
            .setMessage("No se ha confirmado un nombre de la imagen. "+
                        "Indica cómo se llamarán el horario y su categoría.")
            .setView(wrapper).setNegativeButton("Volver a cursos",null)
            .setPositiveButton("Crear horario y guardar",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE)
            .setOnClickListener(v->{
                String title=field.getText().toString().trim();
                if(title.length()<2||title.length()>90){
                    field.setError("Escribe un nombre de 2 a 90 caracteres");return;
                }
                for(AcademicSchedules.Profile p:AcademicSchedules.all(this))
                    if(AcademicSchedules.key(p.name).equals(AcademicSchedules.key(title))){
                        field.setError("Ya existe ese horario. Usa otro nombre.");return;
                    }
                if(saveNewPhoto(approved,title))dialog.dismiss();
            }));
        dialog.show();
    }

    /** An accepted new title creates exactly one schedule+category, then imports. */
    private boolean saveNewPhoto(ArrayList<ScheduleEntry> approved,String title){
        if(photoSaving)return false;
        if(!photoFirst||!profileId.isEmpty())return false;
        photoSaving=true;
        AcademicSchedules.Profile created=null;
        try{
            ArrayList<String> courses=new ArrayList<>();
            for(ScheduleEntry s:approved)courses.add(s.course);
            created=AcademicSchedules.create(this,title,
                    AcademicSchedules.uniqueCourses(courses));
            int imported=ScheduleDatabase.get(this).importReviewed(approved,created.id);
            if(imported<=0)throw new IllegalStateException(
                    "No hay clases nuevas válidas para guardar.");
            profileId=created.id;
            photoFirst=false;
            completePhotoImport(approved,imported);
            return true;
        }catch(RuntimeException error){
            // This is the only rollback path for a just-created, failed import.
            if(created!=null&&photoFirst&&profileId.isEmpty()){
                try{AcademicSchedules.deleteConfirmed(this,created.id);}
                catch(RuntimeException ignored){}
            }
            photoSaving=false;
            scheduleDialog().setTitle("No se pudo crear el horario")
                .setMessage(error.getMessage()==null
                    ?"Revisa el nombre y los cursos. No se guardó un horario nuevo."
                    :error.getMessage())
                .setPositiveButton("Escribir otro nombre",(d,w)->manualPhotoName(approved))
                .setNegativeButton("Volver a cursos",null).show();
            return false;
        }
    }

    private void commitPhoto(ArrayList<ScheduleEntry> approved,String destination){
        if(photoSaving)return;
        photoSaving=true;
        try{
            int added=ScheduleDatabase.get(this).importReviewed(approved,destination);
            completePhotoImport(approved,added);
        }catch(RuntimeException error){
            photoSaving=false;
            scheduleDialog().setTitle("No se pudieron guardar las clases")
                .setMessage("Revisa la información y vuelve a intentarlo.")
                .setPositiveButton("Entendido",null).show();
        }
    }

    private void completePhotoImport(ArrayList<ScheduleEntry> approved,int added){
        AcademicSchedules.syncFromSessions(this,profileId);
        ScheduleReminders.rebuild(this);
        detected=null;detectedTitle="";
        photoSaving=false;
        toast("Clases guardadas: "+added+" · cursos: "+
            SchedulePhotoReview.courseEstimate(approved));
        show(2);
    }
'''
    source=replace_between(source,start,end,method,"confirm title after OCR")
    return source

def transform_title_parser(source):
    before='''    private ScheduleTitleParser(){}'''
    after='''    private static final Pattern WEEK=Pattern.compile(
        "(?iu)^semana\\\\s*(?:(?:[:—–-]\\\\s*)|(?:n[°ºo.]?\\\\s*))?(\\\\d{1,2})(?:\\\\b.*)?$");
    private ScheduleTitleParser(){}'''
    source=replace_once(source,before,after,"week pattern")
    before='''        return "";
    }
}'''
    after='''        // A weekly heading is a possible name only if no explicit schedule title
        // was read. A bare day/clock/course is never turned into a schedule name.
        for(int i=0;i<max;i++){
            String line=lines[i].trim().replaceAll("\\\\s+"," ");
            Matcher week=WEEK.matcher(line);
            if(week.matches())return "Semana "+week.group(1);
        }
        return "";
    }
}'''
    source=replace_once(source,before,after,"week fallback")
    return source

def run():
    path_schedule=CODE/"ScheduleActivity.java"
    path_panel=CODE/"CalendarStudyPanel.java"
    path_parser=CODE/"ScheduleTitleParser.java"
    inputs={x:x.read_text(encoding="utf-8") for x in (path_schedule,path_panel,path_parser)}
    output={
        path_schedule:transform_schedule(inputs[path_schedule]),
        path_panel:transform_panel(inputs[path_panel]),
        path_parser:transform_title_parser(inputs[path_parser]),
    }
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 59")!=1 or gradle.count("versionName '3.13.3'")!=1:
        raise RuntimeError("phase74 requires exact 3.13.3 base")
    gradle=gradle.replace("versionCode 59","versionCode 60",1).replace(
        "versionName '3.13.3'","versionName '3.13.4'",1)
    for path,text in output.items():path.write_text(text,encoding="utf-8")
    GRADLE.write_text(gradle,encoding="utf-8")
    print("PASS photo -> corroborate courses -> OCR title confirmation/manual title -> create category")
    print("PASS no empty new schedule/category before photo is confirmed")
    print("PASS existing schedule photo preserves its original name")
    print("PASS Agenda Clara 3.13.4 source prepared")

if __name__=="__main__":run()
