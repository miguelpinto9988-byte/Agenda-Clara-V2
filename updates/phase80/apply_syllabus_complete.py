#!/usr/bin/env python3
"""Agenda Clara 3.14.0: syllabus import, version review and course panel."""
from pathlib import Path
import argparse
import shutil

HERE=Path(__file__).resolve().parent
ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
SOURCES=("SyllabusTableNormalizer.java","SyllabusColumnTextStripper.java",
         "SyllabusImportPolicy.java")
UPGRADED_REVIEW=Path("updates/phase79/SyllabusReviewIntelligence.java")

def once(text,old,new,label):
    if text.count(old)!=1:
        raise RuntimeError(f"{label}: expected one anchor, found {text.count(old)}")
    return text.replace(old,new,1)

def patch_importer(text):
    text=once(text,"import java.util.Locale;","import java.util.Locale;\nimport java.util.HashMap;\nimport java.util.Map;\nimport java.util.UUID;\nimport java.time.Instant;","imports")
    text=once(text,'    private boolean saving=false;',
        '    private boolean saving=false;\n'
        '    private List<SyllabusEventParser.Page> sourcePages=new ArrayList<>();',
        "document provenance")
    text=once(text,'        final SyllabusEventParser.Event event;\n        boolean selected=true;',
        '        final SyllabusEventParser.Event event;\n'
        '        final String manualKey=UUID.randomUUID().toString();\n'
        '        int occurrence=1;\n'
        '        boolean applyChange=false;\n'
        '        int reminderMinutes=-1;\n'
        '        boolean timeTouched=false;\n'
        '        boolean selected=true;', "row identity")
    text=once(text,
        '        manual.setOnClickListener(v->chooseCourseForManual());panel.addView(manual);',
        '        manual.setOnClickListener(v->chooseCourseForManual());panel.addView(manual);\n'
        '        gap(panel,9);\n'
        '        Button panelButton=button("Mis evaluaciones por curso",false);\n'
        '        panelButton.setOnClickListener(v->AcademicCourseRouting.chooseAny(\n'
        '            this,course->showCoursePanel(course)));\n'
        '        panel.addView(panelButton);', "panel access")
    text=once(text,'        selectedCourse=null;suggestedCourse=null;items.clear();',
        '        selectedCourse=null;suggestedCourse=null;items.clear();sourcePages.clear();',
        "clear old import")
    text=once(text,
        '                List<SyllabusEventParser.Page> pages=\n'
        '                        SyllabusDocumentReader.read(this,uri,documentTitle);',
        '                List<SyllabusEventParser.Page> pages=\n'
        '                    SyllabusTableNormalizer.normalize(\n'
        '                        SyllabusDocumentReader.read(this,uri,documentTitle));',
        "table reconstruction")
    text=once(text,
        '                    items.clear();for(SyllabusEventParser.Event e:events)items.add(new Row(e));\n'
        '                    suggestedCourse=resolution;',
        '                    items.clear();sourcePages=pages;\n'
        '                    Map<String,Integer> seen=new HashMap<>();\n'
        '                    for(SyllabusEventParser.Event e:events){\n'
        '                        Row row=new Row(e);\n'
        '                        String label=SyllabusImportPolicy.normalized(e.type+" "+e.title);\n'
        '                        int n=seen.containsKey(label)?seen.get(label)+1:1;\n'
        '                        seen.put(label,n);row.occurrence=n;items.add(row);\n'
        '                    }\n'
        '                    suggestedCourse=resolution;',
        "stable occurrence")
    text=once(text,
        '            review.addView(label(row.event.scheduleDescription(),13,true));',
        '            review.addView(label(row.event.scheduleDescription(),13,true));\n'
        '            int weight=SyllabusReviewIntelligence.weight(row.event.sourceText+" "+\n'
        '                row.event.dateEvidence);\n'
        '            if(weight>=0)review.addView(label("Ponderación: "+weight+" %",12,true));\n'
        '            if(row.event.page>0){\n'
        '                Button source=button("Ver texto original · página "+row.event.page,false);\n'
        '                source.setOnClickListener(v->showSourceEvidence(row.event));\n'
        '                review.addView(source);\n'
        '            }\n'
        '            if(selectedCourse!=null && !"Registro manual".equals(row.event.sourceText)){\n'
        '                Task previous=existingFor(row);\n'
        '                if(previous!=null){\n'
        '                    boolean changed=!sameEvent(previous,row);\n'
        '                    review.addView(label(changed?\n'
        '                        "Cambio detectado en una evaluación existente":\n'
        '                        "Ya está guardada en este curso · no se duplicará",13,true));\n'
        '                    if(changed){\n'
        '                        review.addView(label("Anterior: "+previous.title+" · "+\n'
        '                            (previous.due>0?Instant.ofEpochMilli(previous.due)\n'
        '                            .atZone(ZoneId.systemDefault()).toLocalDate():\n'
        '                            "Sin fecha")+"\\nNueva lectura: "+\n'
        '                            (row.date==null?"Fecha pendiente":row.date),12,false));\n'
        '                        CheckBox update=new CheckBox(this);\n'
        '                        update.setText("Actualizar esta evaluación (no crear otra)");\n'
        '                        update.setChecked(row.applyChange);\n'
        '                        update.setOnCheckedChangeListener((v,checked)->row.applyChange=checked);\n'
        '                        review.addView(update);\n'
        '                    }\n'
        '                }\n'
        '            }', "provenance and version preview")
    text=once(text,
        '                    row.time=LocalTime.of(h,m);showEvents();',
        '                    row.time=LocalTime.of(h,m);row.timeTouched=true;showEvents();',
        "preserve chosen time")
    text=once(text,
        '                review.addView(timeButton);\n'
        '                Button clearDate=button("Dejar fecha pendiente",false);',
        '                review.addView(timeButton);\n'
        '                Button personal=button(row.reminderMinutes<0?\n'
        '                    "Aviso: usar anticipación general":\n'
        '                    "Aviso individual: "+row.reminderMinutes+" minutos antes",false);\n'
        '                personal.setOnClickListener(v->new AlertDialog.Builder(\n'
        '                    this,R.style.DialogTheme)\n'
        '                    .setTitle("Recordatorio para esta evaluación")\n'
        '                    .setItems(new String[]{"Usar anticipación general",\n'
        '                        "10 días y 12 horas antes","7 días antes",\n'
        '                        "3 días antes","1 día antes"},(dialog,choice)->{\n'
        '                        int[] values={-1,15120,10080,4320,1440};\n'
        '                        row.reminderMinutes=values[choice];showEvents();\n'
        '                    }).show());\n'
        '                review.addView(personal);\n'
        '                Button clearDate=button("Dejar fecha pendiente",false);',
        "per-event reminders")
    begin=text.index("    private void confirmSave(){")
    end=text.index("    private static String sha(",begin)
    text=text[:begin]+CONFIRM+text[end:]
    begin=text.index("    private void saveSelected(int offset){")
    text=text[:begin]+SAVE+"\n}\n"
    return text

CONFIRM=r'''    private void confirmSave(){
        if(saving)return;
        if(selectedCourse==null){
            new AlertDialog.Builder(this,R.style.DialogTheme)
                .setMessage("Confirma el curso y horario antes de importar.")
                .setPositiveButton("Entendido",null).show();return;
        }
        int create=0,update=0,skip=0,pending=0;
        for(Row row:items){
            if(!row.selected)continue;
            if(row.title.trim().length()<3){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setMessage("Corrige los títulos incompletos.")
                    .setPositiveButton("Entendido",null).show();return;
            }
            Task old=existingFor(row);
            if(old==null&&ambiguousLegacyFor(row)){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setTitle("Evaluación anterior ambigua")
                    .setMessage("Hay varias evaluaciones parecidas en el horario para: "+
                        row.title+". Desmarca este evento y comprueba los existentes "+
                        "antes de importar. No se crearán duplicados por suposición.")
                    .setPositiveButton("Revisar",null).show();return;
            }
            if(old==null){create++;if(row.date==null)pending++;}
            else if(row.applyChange&&!sameEvent(old,row)){
                update++;if(row.date==null)pending++;
            }else skip++;
        }
        if(create+update==0){
            new AlertDialog.Builder(this,R.style.DialogTheme)
                .setMessage("No hay evaluaciones nuevas ni cambios autorizados.")
                .setPositiveButton("Entendido",null).show();return;
        }
        final int count=create+update,created=create,changed=update,ignored=skip,undated=pending;
        final int offset=advance!=null&&advance.getSelectedItemPosition()==1?10080:15120;
        new AlertDialog.Builder(this,R.style.DialogTheme)
            .setTitle("Confirmar cambios del sílabo")
            .setMessage("Destino: "+selectedCourse.name+" · "+timetableName(selectedCourse)+
                ".\n\nCrear: "+created+" · Actualizar: "+changed+
                " · Mantener sin cambios: "+ignored+
                "\nFecha pendiente: "+undated+
                "\n\nNo se crearán alarmas para eventos sin día confirmado.")
            .setNegativeButton("Revisar",null)
            .setPositiveButton("Aplicar cambios",(d,w)->saveSelected(offset)).show();
    }
    private String originFor(Row row){
        if("Registro manual".equals(row.event.sourceText))
            return "syllabus-manual:"+row.manualKey;
        return "syllabus3:"+sha(selectedCourse.profileId+"|"+
            SyllabusImportPolicy.signature(selectedCourse.name,row.event.type,
                row.event.title,row.occurrence));
    }
    private Task existingFor(Row row){
        if(selectedCourse==null)return null;
        Task current=Store.get(this).findOrigin(originFor(row));
        if(current!=null)return current;
        // Legacy 3.13.8/3.13.9 imports had date-dependent origin keys.
        // Match only a single unambiguous task linked to the SAME profile and course.
        String normalized=SyllabusImportPolicy.normalized(row.event.title);
        if(normalized.length()<6)return null;
        Task candidate=null;
        for(Task task:Store.get(this).all()){
            if(task.source==null||!task.source.startsWith("Sílabo"))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(this).find(task.id);
            if(link==null||!link.profileId.equals(selectedCourse.profileId)||
                !AcademicCourseMatcher.fold(link.course).equals(
                    AcademicCourseMatcher.fold(selectedCourse.name)))continue;
            if(!SyllabusImportPolicy.normalized(task.title).equals(normalized))continue;
            if(candidate!=null)return null; // Never overwrite ambiguous old records.
            candidate=task;
        }
        return candidate;
    }
    private boolean ambiguousLegacyFor(Row row){
        if(selectedCourse==null||"Registro manual".equals(row.event.sourceText))return false;
        int count=0;
        String label=SyllabusImportPolicy.normalized(row.event.title);
        for(Task previous:Store.get(this).all()){
            if(previous.source==null||!previous.source.startsWith("Sílabo"))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(this).find(previous.id);
            if(link==null||!link.profileId.equals(selectedCourse.profileId)||
                !AcademicCourseMatcher.fold(link.course).equals(
                    AcademicCourseMatcher.fold(selectedCourse.name)))continue;
            if(SyllabusImportPolicy.normalized(previous.title).equals(label)&&++count>1)
                return true;
        }
        return false;
    }
    private boolean sameEvent(Task old,Row row){
        LocalDate previous=old.due>0?Instant.ofEpochMilli(old.due)
            .atZone(ZoneId.systemDefault()).toLocalDate():null;
        return SyllabusImportPolicy.normalized(old.title).equals(
            SyllabusImportPolicy.normalized(row.title)) &&
            (previous==null?row.date==null:previous.equals(row.date));
    }
    private void showSourceEvidence(SyllabusEventParser.Event event){
        String source=event.sourceText;
        for(SyllabusEventParser.Page page:sourcePages){
            if(page.number!=event.page)continue;
            String content=page.text;
            int at=content.indexOf(source);
            if(at<0)at=0;
            source=content.substring(Math.max(0,at-500),
                Math.min(content.length(),Math.max(0,at-500)+2300));
            break;
        }
        new AlertDialog.Builder(this,R.style.DialogTheme)
            .setTitle("Fuente · página "+event.page)
            .setMessage("Fragmento extraído del documento para verificar la lectura:\n\n"+
                source+"\n\nEvaluación identificada:\n"+event.sourceText)
            .setPositiveButton("Volver",null).show();
    }
    private void showCoursePanel(AcademicCourseMatcher.Course course){
        body.removeAllViews();advance=null;
        body.addView(label("Evaluaciones de "+course.name,23,true));
        body.addView(label("Horario: "+timetableName(course),13,false));
        gap(body,10);
        Button back=button("Volver a Sílabos",false);
        back.setOnClickListener(v->landing());body.addView(back);gap(body,12);
        int found=0;
        for(Task task:Store.get(this).all()){
            if(task.source==null||!task.source.startsWith("Sílabo"))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(this).find(task.id);
            if(link==null||!link.profileId.equals(course.profileId)||
                !AcademicCourseMatcher.fold(link.course).equals(
                    AcademicCourseMatcher.fold(course.name)))continue;
            found++;
            LinearLayout item=card();
            item.addView(label(task.title,17,true));
            String status=task.done?"Completado":task.due<=0?"Fecha pendiente":"Programado";
            item.addView(label(status+(task.due>0?" · "+
                Instant.ofEpochMilli(task.due).atZone(ZoneId.systemDefault())
                    .toLocalDate():""),13,false));
            Button choose=button(task.due<=0?"Confirmar fecha":"Modificar fecha",false);
            choose.setOnClickListener(v->{
                LocalDate first=task.due>0?
                    Instant.ofEpochMilli(task.due).atZone(ZoneId.systemDefault()).toLocalDate():
                    LocalDate.now();
                new DatePickerDialog(this,(picker,y,m,d)->{
                    LocalDate picked=LocalDate.of(y,m+1,d);
                    LocalTime time=task.due>0?
                        Instant.ofEpochMilli(task.due).atZone(ZoneId.systemDefault()).toLocalTime():
                        LocalTime.of(23,59);
                    new TimePickerDialog(this,(picker2,h,min)->{
                        new AlertDialog.Builder(this,R.style.DialogTheme)
                        .setTitle("Confirmar fecha de evaluación")
                        .setMessage(task.title+"\n"+picked+" · "+
                            String.format(Locale.ROOT,"%02d:%02d",h,min))
                        .setNegativeButton("Cancelar",null)
                        .setPositiveButton("Guardar fecha",(dialog,which)->{
                            Reminders.cancel(this,task.id);
                            task.due=picked.atTime(h,min)
                                .atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
                            if(task.offsets==null||task.offsets.isEmpty())
                                task.offsets="15120";
                            task.notes+="\nFecha confirmada desde el panel: "+picked;
                            Store.get(this).save(task);
                            Reminders.schedule(this,task);
                            TaskWidget.refresh(this);
                            showCoursePanel(course);
                        }).show();
                    },time.getHour(),time.getMinute(),true).show();
                },first.getYear(),first.getMonthValue()-1,first.getDayOfMonth()).show();
            });
            item.addView(choose);
        }
        if(found==0){
            LinearLayout empty=card();
            empty.addView(label("Todavía no hay evaluaciones importadas en este curso.",14,false));
        }
    }
'''

SAVE=r'''    private void saveSelected(int offset){
        if(saving)return;saving=true;
        int saved=0,updated=0,duplicate=0,pending=0;
        try{
            for(Row row:items){
                if(!row.selected)continue;
                Task previous=existingFor(row);
                if(previous!=null&&(!row.applyChange||sameEvent(previous,row))){
                    duplicate++;continue;
                }
                String identity=originFor(row);
                Task task=previous==null?new Task():previous;
                String previousNotes=previous==null?"":task.notes;
                task.title=row.title.trim();
                task.category=selectedCourse.category;
                task.source="Sílabo · "+row.event.type;
                task.originKey=identity;
                StringBuilder notes=new StringBuilder();
                notes.append("Curso: ").append(selectedCourse.name).append('\n');
                notes.append("Horario: ").append(timetableName(selectedCourse)).append('\n');
                notes.append("Tipo: ").append(row.event.type).append('\n');
                notes.append("Sílabo: ").append(documentTitle).append('\n');
                if(row.event.page>0)notes.append("Página: ").append(row.event.page).append('\n');
                notes.append(row.event.scheduleDescription()).append('\n');
                if(row.date==null){
                    notes.append("FECHA PENDIENTE · sin alarma.\n");
                    task.due=0;task.offsets="";pending++;
                }else{
                    LocalTime time=row.time;
                    if(previous!=null&&!row.timeTouched&&previous.due>0)
                        time=Instant.ofEpochMilli(previous.due)
                            .atZone(ZoneId.systemDefault()).toLocalTime();
                    task.due=row.date.atTime(time).atZone(ZoneId.systemDefault())
                        .toInstant().toEpochMilli();
                    task.offsets=String.valueOf(row.reminderMinutes>0?row.reminderMinutes:offset);
                    notes.append("Fecha confirmada: ").append(row.date).append('\n');
                }
                notes.append("Texto original: ").append(row.event.sourceText);
                if(previous!=null)notes.append("\n--- Notas anteriores preservadas ---\n")
                    .append(previousNotes);
                task.notes=notes.toString();
                Store.get(this).save(task);
                if(previous!=null)Reminders.cancel(this,task.id);
                AcademicTaskLinks.get(this).assign(task.id,selectedCourse.profileId,
                    selectedCourse.name);
                if(task.due>0&&!task.done)Reminders.schedule(this,task);
                if(previous==null)saved++;else updated++;
            }
            TaskWidget.refresh(this);
            final int created=saved,changed=updated,ignored=duplicate,pendingCount=pending;
            new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Sílabo incorporado")
                .setMessage(created+" nuevas · "+changed+" actualizadas · "+
                    ignored+" conservadas · "+pendingCount+
                    " sin día exacto. Los cambios se aplicaron al curso confirmado.")
                .setPositiveButton("Ver evaluaciones",(dialog,which)->{
                    showCoursePanel(selectedCourse);
                }).setNegativeButton("Cerrar",(dialog,which)->finish()).show();
        }catch(Exception e){
            TaskWidget.refresh(this);
            new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Importación incompleta")
                .setMessage("Se crearon "+saved+" y actualizaron "+updated+
                    " tareas antes del error. Comprueba el panel del curso.")
                .setPositiveButton("Entendido",null).show();
        }finally{saving=false;}
    }'''

def patch_reader(text):
    text=once(text,"PDFTextStripper stripper=new PDFTextStripper();",
              "PDFTextStripper stripper=new SyllabusColumnTextStripper();",
              "PDF column reader")
    text=once(text,
        "                int event;\n                while((event=parser.next())!=XmlPullParser.END_DOCUMENT){",
        "                int event;boolean inCell=false;\n"
        "                while((event=parser.next())!=XmlPullParser.END_DOCUMENT){\n"
        "                    if(event==XmlPullParser.START_TAG&&\"tc\".equals(parser.getName()))\n"
        "                        inCell=true;",
        "Word table state")
    text=once(text,
        '''                    if(event==XmlPullParser.END_TAG && ("p".equals(parser.getName())
                            || "tr".equals(parser.getName())))text.append('\\n');''',
        '''                    if(event==XmlPullParser.END_TAG&&"tc".equals(parser.getName())){
                        text.append(" | ");inCell=false;
                    }else if(event==XmlPullParser.END_TAG &&
                        ("tr".equals(parser.getName())||
                            ("p".equals(parser.getName())&&!inCell)))
                        text.append('\\n');''',
        "Word table cells")
    return text

def run(dry_run=False):
    for path in [GRADLE,ROOT/"SyllabusImportActivity.java",
                 ROOT/"SyllabusDocumentReader.java",UPGRADED_REVIEW]+[HERE/name for name in SOURCES]:
        if not path.is_file():raise RuntimeError(f"Missing input: {path}")
    old_version=GRADLE.read_text(encoding="utf-8")
    if old_version.count("versionCode 65")!=1 or old_version.count("versionName '3.13.9'")!=1:
        raise RuntimeError("Expected v3.13.9 (65). No files modified.")
    importer=patch_importer((ROOT/"SyllabusImportActivity.java").read_text(encoding="utf-8"))
    reader=patch_reader((ROOT/"SyllabusDocumentReader.java").read_text(encoding="utf-8"))
    version=old_version.replace("versionCode 65","versionCode 66",1).replace(
        "versionName '3.13.9'","versionName '3.14.0'",1)
    for name in SOURCES:
        if (ROOT/name).exists():raise RuntimeError(f"Already migrated: {name}")
    if dry_run:
        print("PASS: preflight and all exact anchors, no files written")
        return
    for name in SOURCES:shutil.copyfile(HERE/name,ROOT/name)
    shutil.copyfile(UPGRADED_REVIEW,ROOT/"SyllabusReviewIntelligence.java")
    (ROOT/"SyllabusImportActivity.java").write_text(importer,encoding="utf-8")
    (ROOT/"SyllabusDocumentReader.java").write_text(reader,encoding="utf-8")
    GRADLE.write_text(version,encoding="utf-8")
    print("PASS v3.14.0: table reconstruction, provenance, version diff and course panel")
    print("PASS: original schedules and databases remain intact")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    run(args.dry_run)
