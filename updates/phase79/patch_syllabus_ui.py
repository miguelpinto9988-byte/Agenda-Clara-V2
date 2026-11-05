#!/usr/bin/env python3
"""Source-safe UI integration of syllabus evaluation review/re-import and calendar panel."""
def one(s,old,new,label):
    count=s.count(old)
    if count!=1:raise RuntimeError(f"UI syllabus {label}: incompatible anchor ({count})")
    return s.replace(old,new,1)

def update(source):
    source=one(source,
'''        boolean selected=true;
        LocalDate date;
        LocalTime time=LocalTime.of(23,59);
        String title;
        Row(SyllabusEventParser.Event e){
            event=e;date=e.date;
            title="Registro manual".equals(e.sourceText)?"":e.title;
        }''',
'''        boolean selected=true,selectionTouched=false,createSeparate=false;
        LocalDate date,suggestedDay;
        LocalTime time=LocalTime.of(23,59);
        double weight=-1;
        String title;
        SyllabusReimportPlanner.Plan plan;
        SyllabusReimportPlanner.Existing updateTarget;
        Row(SyllabusEventParser.Event e){
            event=e;date=e.date;
            title="Registro manual".equals(e.sourceText)?"":e.title;
        }
        Row(SyllabusAssessmentExtractor.Finding f){
            this(f.event);weight=f.weight;suggestedDay=f.suggestedDay;
            // A rubric mention without date or academic week is uncertain.
            // Keep it visible, but do not import it without an explicit check.
            if(f.event.date==null&&f.event.week==0&&f.event.windowStart==null)
                selected=false;
        }''',"row model")
    source=one(source,
'''        manual.setOnClickListener(v->chooseCourseForManual());panel.addView(manual);
    }''',
'''        manual.setOnClickListener(v->chooseCourseForManual());panel.addView(manual);
        renderEvaluationOverview();
    }''',"dashboard summary")
    source=one(source,
'''                List<SyllabusEventParser.Event> events=SyllabusEventParser.extract(pages);''',
'''                List<SyllabusAssessmentExtractor.Finding> events=
                    SyllabusAssessmentExtractor.extract(pages);''',"extraction")
    source=one(source,
'''                    items.clear();for(SyllabusEventParser.Event e:events)items.add(new Row(e));''',
'''                    items.clear();for(SyllabusAssessmentExtractor.Finding f:events)
                        items.add(new Row(f));''',"extracted rows")
    source=one(source,
'''        review.addView(label("Corrige cualquier lectura dudosa. Los eventos que indican solo semanas pueden guardarse sin fecha exacta y sin alarmas.",13,false));
        for(Row row:items){
            gap(review,12);
            CheckBox check=new CheckBox(this);
            check.setChecked(row.selected);''',
'''        review.addView(label("Corrige lecturas dudosas y revisa cambios frente a versiones anteriores. "+
            "Las fechas inferidas nunca se activan sin confirmarlas.",13,false));
        final List<SyllabusReimportPlanner.Existing> existing=existingForCourse();
        for(Row row:items){
            row.plan=selectedCourse==null?null:SyllabusReimportPlanner.compare(
                row.title,row.event.type,dueMillis(row),documentTitle,existing);
            if(!row.selectionTouched&&row.plan!=null&&
                    row.plan.status!=SyllabusReimportPlanner.Status.NEW)
                row.selected=false;
            gap(review,12);
            CheckBox check=new CheckBox(this);
            check.setChecked(row.selected);''',"reconciliation rows")
    source=one(source,
'''            check.setOnCheckedChangeListener((v,checked)->row.selected=checked);''',
'''            check.setOnCheckedChangeListener((v,checked)->{
                row.selected=checked;row.selectionTouched=true;
            });''',"explicit review check")
    source=one(source,
'''            review.addView(label(row.event.page>0?"Fuente: página "+row.event.page:
                "Fuente: registro manual o texto del archivo",12,false));
            review.addView(label(row.event.scheduleDescription(),13,true));''',
'''            review.addView(label(row.event.page>0?"Fuente: página "+row.event.page:
                "Fuente: registro manual o texto del archivo",12,false));
            review.addView(label(row.event.scheduleDescription(),13,true));
            if(row.weight>=0)
                review.addView(label("Ponderación detectada: "+row.weight+" %",12,false));
            if(row.event.date==null&&row.event.week==0&&row.event.windowStart==null)
                review.addView(label("Sin fecha ni semana en el sílabo: propuesta sin marcar. "+
                    "Verifica si es una evaluación programada.",12,false));
            if(row.event.dateEvidence!=null&&!row.event.dateEvidence.isEmpty())
                review.addView(label("Referencia del documento: "+
                    row.event.dateEvidence,12,false));
            if(row.suggestedDay!=null&&row.date==null){
                review.addView(label("Posible fecha por día de semana: "+
                    row.suggestedDay+" (requiere confirmar)",12,false));
                Button acceptDay=button("Confirmar fecha sugerida: "+row.suggestedDay,false);
                acceptDay.setOnClickListener(v->{row.date=row.suggestedDay;showEvents();});
                review.addView(acceptDay);
            }
            renderReimportDecision(review,row);''',"display evidence and diff")
    source=one(source,
'''        int selected=0,undated=0;
        for(Row row:items){''',
'''        int selected=0,undated=0,changes=0,newCount=0;
        for(Row row:items){''',"confirm counters")
    source=one(source,
'''            if(row.date==null)undated++;
        }
        if(selected==0)return;
        final int count=selected,pending=undated;''',
'''            if(row.date==null)undated++;
            if(row.plan!=null&&row.plan.status==SyllabusReimportPlanner.Status.UNCHANGED){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setMessage("La evaluación «"+row.title+"» ya está guardada sin cambios. "+
                        "Desmárcala para continuar.")
                    .setPositiveButton("Entendido",null).show();return;
            }
            if(row.plan!=null&&row.plan.status!=SyllabusReimportPlanner.Status.NEW&&
                    row.updateTarget==null&&!row.createSeparate){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setMessage("Selecciona «Actualizar registro existente» o "+
                        "«Registrar como evento distinto» para «"+row.title+"».")
                    .setPositiveButton("Entendido",null).show();return;
            }
            if(row.updateTarget!=null)changes++;else newCount++;
        }
        if(selected==0)return;
        final int count=selected,pending=undated,updates=changes,created=newCount;''',
    "require explicit changes")
    source=one(source,
'''            .setMessage("Destino: "+selectedCourse.name+" · "+timetableName(selectedCourse)+
                ".\\n\\n"+(count-pending)+" con fecha exacta y "+pending+
                " pendientes de fecha. Las pendientes se guardarán en el curso sin alarmas; "+
                "podrás fijarles fecha más adelante.\\n\\nAvisos de las fechadas: "+''',
'''            .setMessage("Destino: "+selectedCourse.name+" · "+timetableName(selectedCourse)+
                ".\\n\\n"+created+" eventos nuevos y "+updates+
                " evaluaciones existentes que autorizas actualizar. "+
                (count-pending)+" con fecha exacta y "+pending+
                " pendientes de fecha. Las pendientes se guardarán sin alarmas. "+
                "No se sobrescribirá ningún otro registro.\\n\\nAvisos de las fechadas: "+''',
    "confirm update summary")
    before='''    private void saveSelected(int offset){'''
    extra='''    private long dueMillis(Row row){
        return row.date==null?0:row.date.atTime(row.time)
            .atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
    }
    private List<SyllabusReimportPlanner.Existing> existingForCourse(){
        ArrayList<SyllabusReimportPlanner.Existing> results=new ArrayList<>();
        if(selectedCourse==null)return results;
        for(Task task:Store.get(this).all()){
            if(task.source==null||!task.source.startsWith("Sílabo"))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(this).find(task.id);
            if(link==null||!link.profileId.equals(selectedCourse.profileId)||
                    !AcademicCourseMatcher.fold(link.course).equals(
                        AcademicCourseMatcher.fold(selectedCourse.name)))continue;
            String type=task.source.contains(" · ")?task.source.substring(
                task.source.indexOf(" · ")+3):"Examen";
            String document="";
            if(task.notes!=null)for(String line:task.notes.split("\\\\r?\\\\n"))
                if(line.startsWith("Sílabo: ")){
                    document=line.substring(8).trim();break;
                }
            results.add(new SyllabusReimportPlanner.Existing(
                task.id,task.title,type,task.due,document));
        }
        return results;
    }
    private void renderReimportDecision(LinearLayout review,Row row){
        if(row.plan==null||row.plan.status==SyllabusReimportPlanner.Status.NEW)return;
        if(row.plan.status==SyllabusReimportPlanner.Status.UNCHANGED){
            review.addView(label("Ya registrado · fecha sin cambios. Se omitirá.",12,true));
            return;
        }
        review.addView(label(row.plan.explanation,12,true));
        if(row.updateTarget!=null){
            review.addView(label("Actualización elegida: registro #"+
                row.updateTarget.id+" · se conserva su identidad",12,true));
        }else{
            Button update=button(row.plan.status==SyllabusReimportPlanner.Status.AMBIGUOUS?
                "Elegir evaluación existente para actualizar":
                "Actualizar evaluación existente",false);
            update.setOnClickListener(v->{
                if(row.plan.alternatives.size()==1){
                    row.updateTarget=row.plan.alternatives.get(0);
                    row.createSeparate=false;row.selected=true;
                    row.selectionTouched=true;showEvents();
                }else pickExisting(row);
            });review.addView(update);
            Button distinct=button("Registrar como evento distinto",false);
            distinct.setOnClickListener(v->{
                row.updateTarget=null;row.createSeparate=true;
                row.selectionTouched=true;row.selected=true;showEvents();
            });review.addView(distinct);
        }
    }
    private void pickExisting(Row row){
        LinearLayout list=column();
        list.setPadding(dp(16),dp(8),dp(16),dp(8));
        list.addView(label("Elige exactamente qué evaluación modificar.",13,false));
        ScrollView scroll=new ScrollView(this);scroll.addView(list);
        AlertDialog dialog=new AlertDialog.Builder(this,R.style.DialogTheme)
            .setTitle("Evaluaciones similares").setView(scroll)
            .setNegativeButton("Cancelar",null).create();
        for(SyllabusReimportPlanner.Existing old:row.plan.alternatives){
            String when=old.due==0?"Fecha pendiente":
                java.time.Instant.ofEpochMilli(old.due).atZone(ZoneId.systemDefault())
                    .toLocalDate().toString();
            Button option=button(old.title+" · "+when,false);
            option.setOnClickListener(v->{
                row.updateTarget=old;row.createSeparate=false;
                row.selectionTouched=true;row.selected=true;
                dialog.dismiss();showEvents();
            });
            list.addView(option);
        }
        dialog.show();
    }

'''
    source=one(source,before,extra+before,"extra methods")
    before='''    private void saveSelected(int offset){
        if(saving)return;saving=true;
        int saved=0,duplicate=0,pending=0;'''
    after='''    private void saveSelected(int offset){
        if(saving)return;saving=true;
        int saved=0,updated=0,duplicate=0,pending=0;'''
    source=one(source,before,after,"save counts")
    before='''                String identity="syllabus2:"+sha(selectedCourse.profileId+"|"+'''
    after='''                String identity="syllabus3:"+sha(selectedCourse.profileId+"|"+'''
    source=one(source,before,after,"identity version")
    before='''                if(Store.get(this).findOrigin(identity)!=null){duplicate++;continue;}
                Task task=new Task();task.title=row.title.trim();'''
    after='''                if(row.plan!=null&&
                        row.plan.status==SyllabusReimportPlanner.Status.UNCHANGED){
                    duplicate++;continue;
                }
                if(row.updateTarget==null&&
                        Store.get(this).findOrigin(identity)!=null){duplicate++;continue;}
                Task task=row.updateTarget==null?new Task():
                    Store.get(this).find(row.updateTarget.id);
                if(task==null){duplicate++;continue;}
                boolean updating=row.updateTarget!=null;
                task.title=row.title.trim();'''
    source=one(source,before,after,"reuse saved task")
    source=one(source,
'''                task.originKey=identity;''',
'''                if(!updating||task.originKey.isEmpty())task.originKey=identity;''',
    "retain identity on updates")
    source=one(source,
'''                notes.append(row.event.scheduleDescription()).append('\\n');''',
'''                notes.append(row.event.scheduleDescription()).append('\\n');
                if(row.weight>=0)
                    notes.append("Ponderación: ").append(row.weight).append(" %\\n");
                if(row.event.dateEvidence!=null)
                    notes.append("Contexto de la fecha: ").append(row.event.dateEvidence).append('\\n');''',
    "weight and evidence")
    source=one(source,
'''                Store.get(this).save(task);
                AcademicTaskLinks.get(this).assign(task.id,selectedCourse.profileId,
                        selectedCourse.name);
                if(task.due>0)Reminders.schedule(this,task);
                saved++;''',
'''                Store.get(this).save(task);
                AcademicTaskLinks.get(this).assign(task.id,selectedCourse.profileId,
                        selectedCourse.name);
                if(updating)Reminders.cancel(this,task.id);
                if(task.due>0&&!task.done)Reminders.schedule(this,task);
                if(updating)updated++;else saved++;''',
    "update reminders and tasks")
    source=one(source,
'''            final int count=saved,skipped=duplicate,toResolve=pending;''',
'''            final int count=saved,changed=updated,skipped=duplicate,toResolve=pending;''',
    "result counts")
    source=one(source,
'''                .setMessage(count+" creadas en «"+selectedCourse.name+"» · "+
                    skipped+" duplicadas omitidas · "+toResolve+''',
'''                .setMessage(count+" nuevas y "+changed+" actualizadas en «"+
                    selectedCourse.name+"» · "+skipped+" duplicadas omitidas · "+toResolve+''',
    "result text")
    return source

def overview(source):
    # This panel is accessible without importing anything.
    hook='''    private void openDocument(){'''
    impl='''    private void renderEvaluationOverview(){
        LinearLayout panel=card();
        panel.addView(label("Mis evaluaciones académicas",18,true));
        int count=0,pending=0,shown=0;
        for(Task task:Store.get(this).all()){
            if(task.source==null||!task.source.startsWith("Sílabo"))continue;
            AcademicTaskLinks.Link link=AcademicTaskLinks.get(this).find(task.id);
            if(link==null)continue;
            count++;if(task.due==0&&!task.done)pending++;
            if(shown++>=15)continue;
            String status=task.done?"Completado":
                task.due==0?"Fecha pendiente":"Programado";
            panel.addView(label(task.title+" · "+link.course,13,true));
            panel.addView(label(status+" · "+task.category,12,false));
            if(task.due==0&&!task.done){
                Button setDate=button("Definir fecha para "+task.title,false);
                setDate.setOnClickListener(v->dateExisting(task));
                panel.addView(setDate);
            }
            gap(panel,7);
        }
        if(count==0)panel.addView(label(
            "Al confirmar un sílabo, sus exámenes aparecerán aquí por curso.",13,false));
        else panel.addView(label("Total: "+count+" · "+pending+
            " pendientes de fecha. Se muestran hasta 15.",12,false));
    }
    private void dateExisting(Task task){
        LocalDate today=LocalDate.now();
        DatePickerDialog picker=new DatePickerDialog(this,(v,year,month,day)->{
            LocalDate chosen=LocalDate.of(year,month+1,day);
            new TimePickerDialog(this,(pick,hour,minute)->{
                long when=chosen.atTime(hour,minute).atZone(ZoneId.systemDefault())
                    .toInstant().toEpochMilli();
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setTitle("Confirmar fecha del examen")
                    .setMessage(task.title+"\\nNueva fecha: "+chosen+
                        " "+String.format(Locale.ROOT,"%02d:%02d",hour,minute)+
                        "\\nSe activarán los recordatorios disponibles.")
                    .setNegativeButton("Revisar",null)
                    .setPositiveButton("Guardar fecha",(d,w)->{
                        Task current=Store.get(this).find(task.id);
                        if(current==null)return;
                        current.due=when;
                        current.offsets="15120";
                        current.notes=current.notes.replace(
                            "FECHA PENDIENTE: confirmar día y hora cuando se publique. "+
                            "No hay recordatorios automáticos mientras no tenga fecha.",
                            "Fecha confirmada posteriormente: "+chosen);
                        Store.get(this).save(current);
                        Reminders.cancel(this,current.id);
                        if(!current.done)Reminders.schedule(this,current);
                        TaskWidget.refresh(this);landing();
                    }).show();
            },23,59,true).show();
        },today.getYear(),today.getMonthValue()-1,today.getDayOfMonth());
        picker.show();
    }

'''
    return one(source,hook,impl+hook,"overview methods")

def safeguards(source):
    source=one(source,
'''        double weight=-1;
        String title;''',
'''        double weight=-1;
        int reminderOffset=0;
        String title;''',"row-specific reminders")
    source=one(source,
'''    /** Explicit, scrollable destination buttons; never silently select one profile. */''',
'''    private void assignCourse(AcademicCourseMatcher.Course course){
        selectedCourse=course;
        // A change of profile MUST invalidate old task update targets.
        for(Row row:items){
            row.updateTarget=null;row.createSeparate=false;row.plan=null;
            row.selected=true;row.selectionTouched=false;
        }
        showEvents();
    }
    /** Explicit, scrollable destination buttons; never silently select one profile. */''',
    "course selection reset")
    source=one(source,
'''                selectedCourse=match;dialog.dismiss();showEvents();''',
'''                dialog.dismiss();assignCourse(match);''',"header course selection")
    source=one(source,
'''            pick.setOnClickListener(v->{selectedCourse=course;dialog.dismiss();showEvents();});''',
'''            pick.setOnClickListener(v->{dialog.dismiss();assignCourse(course);});''',
    "catalog course selection")
    source=one(source,
'''                review.addView(timeButton);
                Button clearDate=button("Dejar fecha pendiente",false);''',
'''                review.addView(timeButton);
                Button perAlert=button("Aviso de esta evaluación: "+
                    (row.reminderOffset==15120?"10 días y 12 horas":
                     row.reminderOffset==10080?"7 días":"usar opción general"),false);
                perAlert.setOnClickListener(v->chooseReminder(row));
                review.addView(perAlert);
                Button clearDate=button("Dejar fecha pendiente",false);''',
    "individual reminder")
    source=one(source,
'''    private long dueMillis(Row row){''',
'''    private void chooseReminder(Row row){
        LinearLayout options=column();
        options.setPadding(dp(16),dp(8),dp(16),dp(8));
        ScrollView scroll=new ScrollView(this);scroll.addView(options);
        AlertDialog dialog=new AlertDialog.Builder(this,R.style.DialogTheme)
            .setTitle("Recordatorio de esta evaluación")
            .setView(scroll).setNegativeButton("Cancelar",null).create();
        int[] values={0,15120,10080};
        String[] labels={"Utilizar aviso general","10 días y 12 horas antes",
            "7 días antes"};
        for(int i=0;i<values.length;i++){
            final int value=values[i];
            Button b=button(labels[i],false);
            b.setOnClickListener(v->{
                row.reminderOffset=value;
                dialog.dismiss();showEvents();
            });
            options.addView(b);gap(options,8);
        }
        dialog.show();
    }
    private long dueMillis(Row row){''',"reminder chooser method")
    source=one(source,
'''        int selected=0,undated=0,changes=0,newCount=0;
        for(Row row:items){''',
'''        int selected=0,undated=0,changes=0,newCount=0;
        // Titles and dates may have been edited since the last render:
        // never rely on a stale reconciliation plan at save time.
        final List<SyllabusReimportPlanner.Existing> latest=existingForCourse();
        for(Row row:items){
            row.plan=SyllabusReimportPlanner.compare(row.title,row.event.type,
                dueMillis(row),documentTitle,latest);''',
    "refresh reconciliation before save")
    source=one(source,
'''                    task.offsets=String.valueOf(offset);
                    notes.append("Fecha confirmada por el usuario: ")''',
'''                    task.offsets=String.valueOf(
                        row.reminderOffset>0?row.reminderOffset:offset);
                    notes.append("Fecha confirmada por el usuario: ")''',
    "save per evaluation reminder")
    return source

def run(source):
    return safeguards(overview(update(source)))
