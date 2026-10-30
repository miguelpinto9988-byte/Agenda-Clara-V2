#!/usr/bin/env python3
"""Agenda Clara 3.8.2 native redesign (post phase 20).

No Compose dependency, no new data store, no changes to reminder scheduling.
Fails closed if an expected source anchor has changed.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"AgendaClara/app/src/main/java/pe/agendaclara/app"
PHASE=Path(__file__).resolve().parent

def one(value, old, new, label):
    count=value.count(old)
    if count!=1: raise RuntimeError(f"redesign: {label}: expected one match, found {count}")
    return value.replace(old,new,1)

def section(value, start, end, replacement, label):
    if value.count(start)!=1 or end not in value:raise RuntimeError(f"redesign: anchor mismatch {label}")
    a=value.index(start);b=value.index(end,a)
    if b<=a:raise RuntimeError(f"redesign: bad ordering {label}")
    return value[:a]+replacement+value[b:]

def install():
    mainpath=SRC/"MainActivity.java"
    java=mainpath.read_text(encoding="utf-8")
    storepath=SRC/"Store.java"
    store=storepath.read_text(encoding="utf-8")
    organizationpath=SRC/"TaskOrganization.java"
    org=organizationpath.read_text(encoding="utf-8")
    for classname in ("CategoryRegistry","TaskPriority"):
        if (SRC/(classname+".java")).exists(): raise RuntimeError("Refusing overwriting "+classname)
    if "ComposeDayActivity" in java: raise RuntimeError("Phase 20 is not applied")

    # Keep historical fixed category labels as a compatibility alias for old
    # core tests and restored backups; new category choices come from the registry.
    org=one(org,'    return "General";\n  }\n  public static boolean validSubtask',
        '    String custom=value.trim().replaceAll("\\\\s+"," ");\n'
        '    return custom.isEmpty()?"General":custom.substring(0,Math.min(custom.length(),180));\n'
        '  }\n  public static boolean validSubtask',"support custom category names")
    store=one(store,"\n}",'''
    /** Reassign tasks before renaming or deleting a user-created category. */
    public synchronized int reassignCategory(String from,String to){
        android.content.ContentValues values=new android.content.ContentValues();
        values.put("category",TaskOrganization.category(to));
        return getWritableDatabase().update("tasks",values,"category=? COLLATE NOCASE",new String[]{from});
    }
}''',"DB category reassignment")

    # Responsive shell and consistent visual tokens.
    java=one(java,"static final int BG=0xfff6f8fc,INK=0xff162441,GREEN=0xff3957d7,MUTED=0xff60738b,RED=0xffd45063;",
        "static final int BG=0xfff5f8ff,INK=0xff142346,GREEN=0xff405be8,MUTED=0xff617494,RED=0xffd45063;","palette")
    java=one(java,"static final int VIOLET=0xff8466dc,SUCCESS=0xff0d8d83,SURFACE=0xffffffff,PALE=0xffedf0ff,STROKE=0xffdfe5f1;",
        "static final int VIOLET=0xff7159ed,SUCCESS=0xff0d9488,SURFACE=0xffffffff,PALE=0xffeef1ff,STROKE=0xffdce5f5;","palette-secondary")
    java=one(java,'String query="";','String query="",selectedCategory="";',"filter state")
    java=one(java,'query=state.getString("query","");',
        'query=state.getString("query","");selectedCategory=state.getString("selected_category","");',"restore category filter")
    java=one(java,'out.putString("query",query);',
        'out.putString("query",query);out.putString("selected_category",selectedCategory);',"save category filter")
    java=one(java,'header.addView(add,new LinearLayout.LayoutParams(dp(54),dp(54)));',
        'header.addView(add,new LinearLayout.LayoutParams(dp(108),dp(108)));',"2x header plus")
    java=one(java,'body.setPadding(dp(16),dp(6),dp(16),dp(20));',
        'body.setPadding(dp(18),dp(12),dp(18),dp(32));',"screen content safe margins")
    java=one(java,'header.setPadding(dp(20),dp(18),dp(18),dp(12));',
        'header.setPadding(dp(20),dp(16),dp(18),dp(18));',"header spacing")
    java=one(java,'nav.setPadding(dp(10),dp(8),dp(10),dp(9));',
        'nav.setPadding(dp(10),dp(10),dp(10),dp(14));',"bottom nav spacing")
    java=one(java,'item.setPadding(0,dp(7),0,dp(6));',
        'item.setPadding(dp(2),dp(10),dp(2),dp(10));',"nav item spacing")
    java=one(java,'dp(23),dp(23)', 'dp(26),dp(26)',"nav icons")
    java=one(java,'c.setPadding(dp(18),dp(17),dp(18),dp(17));c.setBackground(outlined(SURFACE,24,STROKE));c.setElevation(dp(3));',
        'c.setPadding(dp(18),dp(18),dp(18),dp(18));c.setBackground(outlined(SURFACE,22,STROKE));c.setElevation(dp(2));',"cards")
    java=one(java,'lp.bottomMargin=dp(12);parent.addView(c,lp);',
        'lp.bottomMargin=dp(16);parent.addView(c,lp);',"card gutter")
    java=one(java,'rounded(PALE,16),null));b.setElevation(0);',
        'outlined(0xffeef1ff,16,STROKE),null));b.setElevation(0);',"button outline")
    java=one(java,'e.setBackground(outlined(0xffffffff,16,STROKE));',
        'e.setBackground(outlined(0xffffffff,18,STROKE));',"input corners")

    # Remove the 7-row statistics chart; keep a useful compact progress summary.
    java=section(java,'        LinearLayout trend=card(body);','        if(!Reminders.canNotify(this)',
         '',"simplified agenda header")
    java=one(java,'text("Filtrar por categoría",12,MUTED,true)',
        'text("Mis categorías",16,INK,true)',"categories heading")
    java=section(java,'        HorizontalScrollView categoriesScroll=', '        taskList=column();',
'''        LinearLayout categoryActions=row();
        categoryActions.addView(button("Gestionar categorías ›",this::showCategories));
        body.addView(categoryActions);gap(body,8);
        HorizontalScrollView categoriesScroll=new HorizontalScrollView(this);
        categoriesScroll.setHorizontalScrollBarEnabled(false);
        LinearLayout categoryChips=row();String[] categories=CategoryRegistry.names(this);
        String[] choices=new String[categories.length+1];choices[0]="Todas";
        System.arraycopy(categories,0,choices,1,categories.length);
        for(String label:choices){
            final String chosen="Todas".equals(label)?"":label;
            Button chip=button(label,()->{selectedCategory=chosen;taskLimit=24;render();});
            boolean active=selectedCategory.equalsIgnoreCase(chosen);
            chip.setTextColor(active?0xffffffff:GREEN);
            chip.setBackground(rounded(active?GREEN:PALE,18));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(48));lp.rightMargin=dp(8);
            categoryChips.addView(chip,lp);
        }
        Button create=button("＋ Nueva",()->showCategoryEditor(null,null));
        categoryChips.addView(create);
        categoriesScroll.addView(categoryChips);body.addView(categoriesScroll);gap(body,12);
''',"dynamic categories chips")
    java=one(java,'if(!AgendaFilters.matches(t,filter,categoryFilter,query,date,now))continue;',
'''if(!AgendaFilters.matches(t,filter==1?0:filter,0,query,date,now))continue;
            if(filter==1&&!java.util.Arrays.asList("Vencida","Urgente").contains(TaskPriority.label(t,now)))continue;
            if(date==null&&!selectedCategory.isEmpty()&&!selectedCategory.equalsIgnoreCase(TaskOrganization.category(t.category)))continue;''',"dynamic category filter")
    java=one(java,'TextView guide=text("Urgente: hasta 48 h · Pendiente: hasta 7 días · Próxima: más de 7 días. La prioridad se actualiza con el tiempo.",11,MUTED,false);',
        'TextView guide=text("La prioridad se calcula sola según la fecha límite. Puedes personalizar tus categorías.",12,MUTED,false);',"priority legend")

    # Compact task cards with a single clear detail affordance.
    java=section(java,'    void taskCard(LinearLayout parent,Task t){',
        '    /** Local recycle bin:',
'''    void taskCard(LinearLayout parent,Task t){
        LinearLayout card=card(parent);card.setTag("task:"+t.id);
        LinearLayout top=row();
        CheckBox check=new CheckBox(this);check.setChecked(t.done);
        check.setButtonTintList(ColorStateList.valueOf(GREEN));
        check.setContentDescription((t.done?"Marcar pendiente: ":"Marcar completada: ")+t.title);
        top.addView(check,new LinearLayout.LayoutParams(dp(48),dp(52)));
        LinearLayout details=column();
        TextView name=text(t.title,16,t.done?MUTED:INK,true);
        name.setMaxLines(2);name.setEllipsize(android.text.TextUtils.TruncateAt.END);
        details.addView(name);
        String category=TaskOrganization.category(t.category);
        TextView when=text("◷ "+TaskLogic.when(t.due)+"     ◈ "+category,12,MUTED,false);
        when.setMaxLines(2);details.addView(when);
        top.addView(details,new LinearLayout.LayoutParams(0,-2,1));
        TextView chevron=text("›",28,GREEN,false);chevron.setGravity(Gravity.CENTER);
        top.addView(chevron,new LinearLayout.LayoutParams(dp(36),dp(48)));
        card.addView(top);
        String status=TaskPriority.label(t,System.currentTimeMillis());
        TextView priority=text(status+" · prioridad automática",11,TaskPriority.color(status),true);
        priority.setPadding(dp(10),dp(6),dp(10),dp(6));priority.setBackground(rounded(PALE,12));
        card.addView(priority);
        int[] progress=taskProgressCache.containsKey(t.id)?taskProgressCache.get(t.id):new int[]{0,0};
        if(progress[0]>0){gap(card,6);card.addView(text("Subtareas: "+progress[1]+" / "+progress[0],12,MUTED,false));}
        if(t.done&&t.completedAt>0){gap(card,6);card.addView(text("Completada · se retira automáticamente tras 1 hora",11,MUTED,false));}
        details.setOnClickListener(v->showTaskDetails(t.id));
        chevron.setOnClickListener(v->showTaskDetails(t.id));
        check.setOnCheckedChangeListener((button,checked)->{
            t.done=checked;Store.get(this).save(t);
            if(checked)Reminders.cancel(this,t.id);else Reminders.schedule(this,t);
            TaskWidget.refresh(this);render();
        });
    }
    void showTaskDetails(long id){
        Task task=Store.get(this).find(id);
        if(task==null){toast("La tarea ya no está disponible.");return;}
        LinearLayout pane=column();pane.setPadding(dp(18),dp(12),dp(18),dp(18));
        pane.addView(text(task.title,20,INK,true));gap(pane,14);
        pane.addView(text("◈  "+TaskOrganization.category(task.category),14,CategoryRegistry.color(this,task.category),true));gap(pane,12);
        pane.addView(text("▢  Fecha límite",13,MUTED,true));
        pane.addView(text(TaskLogic.when(task.due),16,INK,true));gap(pane,12);
        String priority=TaskPriority.label(task,System.currentTimeMillis());
        pane.addView(text("◷  Prioridad: "+priority+" (automática)",14,TaskPriority.color(priority),true));
        if(!task.notes.isEmpty()){gap(pane,12);pane.addView(text("Notas",13,MUTED,true));pane.addView(text(task.notes,14,INK,false));}
        gap(pane,14);
        pane.addView(primaryButton("✎  Editar tarea",()->{for(AlertDialog d:new ArrayList<>(dialogs))if(d.isShowing())d.dismiss();handler.post(()->openEditor(id,null,null));}));
        gap(pane,8);pane.addView(button("☑  Gestionar subtareas",()->{for(AlertDialog d:new ArrayList<>(dialogs))if(d.isShowing())d.dismiss();handler.post(()->openSubtasks(id));}));
        ScrollView scroll=new WindowLayout.DialogScroll(this);scroll.addView(pane);
        dialogBuilder().setTitle("Detalle de tarea").setView(scroll).setPositiveButton("Cerrar",null).show();
    }
''',"compact task cards and task detail")

    # Header on the calendar first, keeping the schedule activity available.
    java=one(java,'        LinearLayout schedule=card(body);\n        schedule.addView(text("▦  Horario de clases",20,INK,true));gap(schedule,6);\n        schedule.addView(text("Organiza tus cursos por semana, importa una foto y recibe avisos antes de cada clase.",13,MUTED,false));gap(schedule,12);\n        schedule.addView(primaryButton("Abrir mi horario  →",()->startActivity(new Intent(this,ScheduleActivity.class))));\n',
        '',"calendar top schedule")
    java=one(java,'        c.addView(grid);gap(c,10);c.addView(button("▣  Ir a hoy",()->{selectedDay=LocalDate.now();month=selectedDay.withDayOfMonth(1);render();}));',
'''        c.addView(grid);gap(c,10);c.addView(button("▣  Ir a hoy",()->{selectedDay=LocalDate.now();month=selectedDay.withDayOfMonth(1);render();}));
        LinearLayout schedule=card(body);
        schedule.addView(text("▦  Horario de clases",17,INK,true));gap(schedule,6);
        schedule.addView(text("Cursos, sesiones y avisos de clase",12,MUTED,false));gap(schedule,10);
        schedule.addView(primaryButton("Abrir mi horario  →",()->startActivity(new Intent(this,ScheduleActivity.class))));''',"calendar schedule moved")

    # Clear single due date and deadline time, preserving reminder recurrence.
    java=one(java,'LinearLayout box=column();box.setPadding(dp(18),dp(4),dp(18),dp(10));',
        'LinearLayout box=column();box.setPadding(dp(18),dp(12),dp(18),dp(24));',"editor margins")
    java=one(java,'title.setSingleLine(false);title.setMaxLines(3);box.addView(title);',
        'title.setSingleLine(false);title.setMaxLines(3);subtitle(box,"Nombre de la tarea");box.addView(title);',"editor title label")
    java=one(java,'CheckBox schedule=new CheckBox(this);schedule.setText("Con fecha y hora");',
        'CheckBox schedule=new CheckBox(this);schedule.setText("Establecer fecha y hora límite");',"due checkbox label")
    java=one(java,'ZonedDateTime def=ZonedDateTime.now().plusHours(1).withSecond(0).withNano(0);',
        'ZonedDateTime def=ZonedDateTime.now().withHour(23).withMinute(59).withSecond(0).withNano(0);',"editor 11:59 default")
    java=one(java,'LinearLayout dateSection=column();box.addView(dateSection);',
        'LinearLayout dateSection=card(box);dateSection.addView(text("▢  Fecha y hora de entrega",17,INK,true));gap(dateSection,10);',"editor date panel")
    java=one(java,'Button dateBtn=button("Otra fecha",()->{}),timeBtn=button("",()->{});',
        'Button dateBtn=button("Elegir fecha",()->{}),timeBtn=button("",()->{});',"editor date button")
    java=one(java,'timeBtn.setText(timeSet[0]?"Hora · "+time[0].format',
        'timeBtn.setText(timeSet[0]?"Hora límite · "+time[0].format',"deadline hour label")
    java=one(java,'        dateSection.addView(button("Fin del día · 11:59 p. m.",()->{time[0]=LocalTime.of(23,59);timeSet[0]=true;refresh.run();}));',
        '        dateSection.addView(text("La prioridad se calcula automáticamente según el tiempo restante.",12,MUTED,false));',"editor no redundant time action")
    java=one(java,'        subtitle(box,"Categoría");\n        Spinner categoryPicker=new Spinner(this);categoryPicker.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,TaskOrganization.CATEGORIES));',
'''        subtitle(box,"Categoría");
        Spinner categoryPicker=new Spinner(this);
        ArrayAdapter<String> categoriesAdapter=new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,new ArrayList<String>(java.util.Arrays.asList(CategoryRegistry.names(this))));
        categoryPicker.setAdapter(categoriesAdapter);''',"dynamic editor category adapter")
    java=one(java,'for(int i=0;i<TaskOrganization.CATEGORIES.length;i++)if(TaskOrganization.CATEGORIES[i].equals(TaskOrganization.category(currentCategory)))categoryPicker.setSelection(i);',
        'for(int i=0;i<categoriesAdapter.getCount();i++)if(categoriesAdapter.getItem(i).equalsIgnoreCase(TaskOrganization.category(currentCategory)))categoryPicker.setSelection(i);',"editor category selection")
    java=one(java,'        box.addView(categoryPicker);\n        CheckBox urgent=',
'''        box.addView(categoryPicker);gap(box,6);
        box.addView(button("＋  Crear nueva categoría",()->showCategoryEditor(null,newName->{
            categoriesAdapter.clear();categoriesAdapter.addAll(CategoryRegistry.names(this));
            categoriesAdapter.notifyDataSetChanged();
            for(int i=0;i<categoriesAdapter.getCount();i++)if(categoriesAdapter.getItem(i).equalsIgnoreCase(newName))categoryPicker.setSelection(i);
        })));
        CheckBox urgent=''', "editor add category")
    java=one(java,'advanced.addView(notes);advanced.addView(urgent);if(existing!=null)advanced.addView(done);',
        'advanced.addView(notes);if(existing!=null)advanced.addView(done);',"remove manual priority")
    java=one(java,'"Más opciones · notas, prioridad y repetición"',
        '"Más opciones · notas y repetición del aviso"',"advanced title")
    java=one(java,'b.putString("category",TaskOrganization.CATEGORIES[categoryPicker.getSelectedItemPosition()]);',
        'b.putString("category",String.valueOf(categoryPicker.getSelectedItem()));',"editor category draft")
    java=one(java,'t.category=TaskOrganization.CATEGORIES[categoryPicker.getSelectedItemPosition()];',
        't.category=String.valueOf(categoryPicker.getSelectedItem());',"editor category save")
    java=one(java,'t.urgent=urgent.isChecked();t.done=done.isChecked();',
        't.urgent=false;t.done=done.isChecked();',"automatic priority no manual toggle")
    java=one(java,'b.putBoolean("urgent",urgent.isChecked());',
        'b.putBoolean("urgent",false);',"automatic priority draft")

    # Dynamic category management lives in the same Activity (no new navigation route).
    marker='    String join(Collection<Integer> offsets){'
    methods='''    void showCategories(){
        LinearLayout pane=column();pane.setPadding(dp(16),dp(12),dp(16),dp(20));
        pane.addView(text("General es la única categoría predefinida.",13,MUTED,false));gap(pane,12);
        pane.addView(primaryButton("＋  Crear categoría",()->{
            for(AlertDialog d:new ArrayList<>(dialogs))if(d.isShowing())d.dismiss();
            handler.post(()->showCategoryEditor(null,name->showCategories()));
        }));gap(pane,14);
        for(CategoryRegistry.Entry entry:CategoryRegistry.all(this)){
            LinearLayout card=card(pane);LinearLayout row=row();
            TextView dot=text("●",22,entry.color,true);row.addView(dot);
            TextView name=text("  "+entry.name,16,INK,true);
            row.addView(name,new LinearLayout.LayoutParams(0,-2,1));
            if(!"General".equalsIgnoreCase(entry.name)){
                row.addView(button("Editar",()->{for(AlertDialog d:new ArrayList<>(dialogs))if(d.isShowing())d.dismiss();handler.post(()->showCategoryEditor(entry.name,edited->showCategories()));}));
                row.addView(button("×",()->dialogBuilder().setTitle("Eliminar "+entry.name)
                    .setMessage("Las tareas de esta categoría pasarán a General. Ninguna tarea será eliminada.")
                    .setNegativeButton("Cancelar",null)
                    .setPositiveButton("Eliminar",(dialog,which)->{
                        if(CategoryRegistry.delete(this,entry.name)){
                            if(selectedCategory.equalsIgnoreCase(entry.name))selectedCategory="";
                            for(AlertDialog open:new ArrayList<>(dialogs))if(open.isShowing())open.dismiss();
                            render();handler.post(this::showCategories);
                        }
                    }).show()));
            }else row.addView(text("  Fija",12,MUTED,false));
            card.addView(row);
        }
        ScrollView scroll=new WindowLayout.DialogScroll(this);scroll.addView(pane);
        dialogBuilder().setTitle("Mis categorías").setView(scroll).setPositiveButton("Listo",null).show();
    }
    void showCategoryEditor(String existing,java.util.function.Consumer<String> onSaved){
        LinearLayout pane=column();pane.setPadding(dp(18),dp(12),dp(18),dp(14));
        pane.addView(text("Nombre de categoría",14,INK,true));gap(pane,7);
        EditText name=input("Ej. Estudios, Salud, Proyectos",existing==null?"":existing,android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        name.setSingleLine(true);name.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(28)});
        pane.addView(name);gap(pane,16);pane.addView(text("Color",14,INK,true));gap(pane,7);
        Spinner colors=new Spinner(this);
        colors.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,CategoryRegistry.COLOR_NAMES));
        if(existing!=null){int current=CategoryRegistry.color(this,existing);for(int i=0;i<CategoryRegistry.COLORS.length;i++)if(current==CategoryRegistry.COLORS[i])colors.setSelection(i);}
        pane.addView(colors);
        AlertDialog dialog=dialogBuilder().setTitle(existing==null?"Crear categoría":"Editar categoría")
            .setView(pane).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(any->dialog.getButton(-1).setOnClickListener(v->{
            String desired=name.getText().toString().trim();
            if(desired.isEmpty()){name.setError("Escribe un nombre.");return;}
            if(!CategoryRegistry.save(this,existing,desired,CategoryRegistry.COLORS[colors.getSelectedItemPosition()])){
                name.setError("Nombre duplicado o no válido. Usa otro nombre.");return;
            }
            if(existing!=null&&selectedCategory.equalsIgnoreCase(existing))selectedCategory=desired;
            dialog.dismiss();render();
            if(onSaved!=null)onSaved.accept(desired);
        }));
        dialog.show();
    }
'''
    java=one(java,marker,methods+marker,"category manager methods")

    # Mobile QA: leave breathing room around filter chips and avoid cropped nav labels.
    java=one(java,'nav.addView(item,new LinearLayout.LayoutParams(0,dp(56),1));',
        'nav.addView(item,new LinearLayout.LayoutParams(0,dp(76),1));',"bottom bar label height")
    java=one(java,'chips.addView(b);',
        'LinearLayout.LayoutParams chipMargin=new LinearLayout.LayoutParams(-2,dp(48));chipMargin.rightMargin=dp(8);chips.addView(b,chipMargin);',
        "status filter chip gutters")
    java=one(java,'summary.addView(heading);gap(summary,8);summary.addView(text("Avance estimado = completadas últimos 7 días / (completadas últimos 7 días + pendientes actuales).",11,MUTED,false));gap(summary,12);',
        'summary.addView(heading);gap(summary,12);',"compact progress header")
    java=section(java,'        LinearLayout stats=row();',
        '        if(!Reminders.canNotify(this)', '',"remove redundant statistic tiles")
    java=one(java,'progress.setProgressTintList(ColorStateList.valueOf(GREEN));',
        'progress.setProgressTintList(ColorStateList.valueOf(VIOLET));',"progress palette")

    # Ensure modal windows never sit flush against screen edges or the IME.
    windowpath=SRC/"WindowLayout.java"
    window=windowpath.read_text(encoding="utf-8")
    window=one(window,"safe.width()-dp(a,32)","safe.width()-dp(a,48)","dialog horizontal insets")
    window=one(window,"safe.height()-dp(a,24)","safe.height()-dp(a,56)","dialog vertical insets")
    windowpath.write_text(window,encoding="utf-8")

    # All text remains within scrolling dialogs (including display cutouts/keyboard).
    mainpath.write_text(java,encoding="utf-8")
    storepath.write_text(store,encoding="utf-8")
    organizationpath.write_text(org,encoding="utf-8")
    for classname in ("CategoryRegistry","TaskPriority"):
        (SRC/(classname+".java")).write_text((PHASE/(classname+".java")).read_text(encoding="utf-8"),encoding="utf-8")
    print("PASS phase21: adaptive native redesign, category management, deadline editor, enlarged +")

if __name__=="__main__":
    install()
