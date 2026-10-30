#!/usr/bin/env python3
"""Phase 22: apply the approved Agenda Clara visual system throughout the native app.

Runs after the category-only phase21. Never edits TopPlusButtonMotion or its PNG.
All edits are guarded: a source mismatch aborts instead of making partial guesses.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]/"AgendaClara"
SRC=ROOT/"app/src/main/java/pe/agendaclara/app"
RES=ROOT/"app/src/main/res"
PHASE=Path(__file__).resolve().parent

def one(s,old,new,label):
    count=s.count(old)
    if count!=1:raise RuntimeError(f"phase22 {label}: found {count}, expected 1")
    return s.replace(old,new,1)

def between(s,start,end,replacement,label):
    if s.count(start)!=1 or s.count(end)!=1:raise RuntimeError("phase22 "+label+": missing/ambiguous bounds")
    a=s.index(start);b=s.index(end,a+len(start))
    if b<a:raise RuntimeError("phase22 "+label+": bounds reversed")
    return s[:a]+replacement+s[b:]

def apply():
    mainpath=SRC/"MainActivity.java"
    java=mainpath.read_text(encoding="utf-8")
    original_plus=next(line for line in java.splitlines() if 'setTag("new_task_button")' in line)
    if "ComposeDayActivity" in java:raise RuntimeError("Removed Compose card unexpectedly returned")
    if 'String query="",selectedCategory="General";' not in java:raise RuntimeError("phase21 category-only UI missing")
    if (SRC/"UiDesign.java").exists():raise RuntimeError("UiDesign already installed")

    # Consistent colors, typography and central native controls.
    java=one(java,'static final int BG=0xfff5f8ff,INK=0xff142346,GREEN=0xff405be8,MUTED=0xff617494,RED=0xffd45063;',
       'static final int BG=UiDesign.BG,INK=UiDesign.INK,GREEN=UiDesign.BLUE,MUTED=UiDesign.MUTED,RED=UiDesign.ERROR;',"main colors")
    java=one(java,'static final int VIOLET=0xff7159ed,SUCCESS=0xff0d9488,SURFACE=0xffffffff,PALE=0xffeef1ff,STROKE=0xffdce5f5;',
       'static final int VIOLET=UiDesign.BLUE2,SUCCESS=UiDesign.SUCCESS,SURFACE=UiDesign.SURFACE,PALE=UiDesign.PALE,STROKE=UiDesign.BORDER;',"secondary colors")
    java=one(java,'if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);',
       'UiDesign.text(t,bold);',"shared typography")
    java=one(java,
       'Button button=button(label,action);button.setTextColor(0xffffffff);button.setTypeface(Typeface.DEFAULT,Typeface.BOLD);\n        button.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x30ffffff),gradient(GREEN,0xff7465ec,17),null));',
       'Button button=button(label,action);UiDesign.button(button,true);UiDesign.actionIcon(button,label);',"primary button style")
    java=one(java,
       'b.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x203957d7),outlined(0xffeef1ff,16,STROKE),null));b.setElevation(0);',
       'UiDesign.button(b,false);UiDesign.actionIcon(b,label);',"secondary button style")
    java=one(java,'e.setBackground(outlined(0xffffffff,18,STROKE));',
       'UiDesign.input(e);',"input style")
    java=one(java,'c.setBackground(outlined(SURFACE,22,STROKE));c.setElevation(dp(2));',
       'UiDesign.card(c);',"card style")
    java=one(java,'TextView label=text(labels[n],11,MUTED,false);',
       'TextView label=text(labels[n],11,MUTED,false);',"nav label anchor")

    # Keep header's 108dp image button, PNG, tags and motion *byte-identical*.
    java=one(java,
       'ImageView icon=new ImageView(this);icon.setImageResource(icons[n]);item.addView(icon,new LinearLayout.LayoutParams(dp(26),dp(26)));',
       'ImageView icon=UiDesign.icon(this,UiDesign.statusIcon(labels[n]),MUTED,26);item.addView(icon,new LinearLayout.LayoutParams(dp(26),dp(26)));',
       "matching outline navigation icons")
    java=one(java,'item.setBackground(rounded(page==n?PALE:0xfffcfdff,18));',
       'item.setBackground(rounded(page==n?PALE:0xfffcfdff,17));',
       "navigation active state")
    java=one(java,'nav.setBackgroundColor(0xfffcfdff);','nav.setBackgroundColor(0xffffffff);',"navigation surface")
    java=one(java,'headerDate=text("",10,MUTED,true);headerTitle=text("",28,INK,true);',
       'headerDate=text("",11,MUTED,true);headerTitle=text("",28,INK,true);',"heading type")
    java=one(java,'headerTitle.setText(new String[]{"Mi agenda","Calendario","Por revisar","Conexiones"}[page]);',
       'headerTitle.setText(new String[]{"Mi agenda","Calendario","Revisión","Conexiones"}[page]);',
       "review page label")

    # Agenda: a concise summary and a single combined category header.
    java=one(java,'summary.setBackground(gradient(0xffffffff,0xfff0f5ff,19));',
       'summary.setBackground(outlined(0xffffffff,21,STROKE));',"summary card")
    java=one(java,'title.addView(text("Pendientes: "+pending+" · Completadas en 7 días: "+weekDone,12,MUTED,false));',
       'title.addView(text(pending+" pendientes · "+weekDone+" completadas esta semana",12,MUTED,false));',"summary statistic wording")
    java=one(java,'percent.setBackground(outlined(PALE,40,0xffd2e1fe));',
       'percent.setBackground(outlined(0xfff1f4ff,40,STROKE));',"summary badge")
    java=one(java,
       '''        TextView categoriesLabel=text("Mis categorías",16,INK,true);body.addView(categoriesLabel);gap(body,4);
        LinearLayout categoryActions=row();
        categoryActions.addView(button("Gestionar categorías ›",this::showCategories));
        body.addView(categoryActions);gap(body,8);''',
       '''        LinearLayout categoryActions=row();
        TextView categoriesLabel=text("Mis categorías",17,INK,true);
        categoryActions.addView(categoriesLabel,new LinearLayout.LayoutParams(0,-2,1));
        Button manage=button("Gestionar  ›",this::showCategories);
        manage.setContentDescription("Gestionar categorías personalizadas");
        manage.setMinWidth(dp(112));categoryActions.addView(manage);
        body.addView(categoryActions);gap(body,10);''',
       "single category heading row")

    # Category selector icon and color tokens, still only user-defined names.
    java=one(java,'chip.setTextColor(active?0xffffffff:GREEN);\n            chip.setBackground(rounded(active?GREEN:PALE,18));',
       '''chip.setTextColor(active?0xffffffff:CategoryRegistry.color(this,label));
            chip.setBackground(outlined(active?GREEN:PALE,17,active?GREEN:STROKE));''',
       "category chip tints")
    java=one(java,'categoriesScroll.addView(categoryChips);body.addView(categoriesScroll);gap(body,12);',
       'categoriesScroll.addView(categoryChips);body.addView(categoriesScroll);gap(body,18);',
       "category and task separation")
    java=one(java,'taskList=column();body.addView(taskList);fillTasks(all,null);',
       '''LinearLayout listHeader=row();TextView upcoming=text("Próximas tareas",17,INK,true);
        listHeader.addView(upcoming);body.addView(listHeader);gap(body,10);
        taskList=column();body.addView(taskList);fillTasks(all,null);''',
       "tasks heading")

    # Cards: a readable, soft-colored due badge with high-contrast status.
    java=one(java,'priority.setPadding(dp(10),dp(6),dp(10),dp(6));priority.setBackground(rounded(PALE,12));',
       '''priority.setPadding(dp(10),dp(8),dp(10),dp(8));
        int badgeColor="Urgente".equals(status)||"Vencida".equals(status)?0xffffe9ed:
           "Alta".equals(status)?0xfffff1e7:"Media".equals(status)?0xffeaf1ff:
           "Baja".equals(status)?0xffe5f8ec:PALE;
        priority.setBackground(rounded(badgeColor,12));''',
       "automatic priority badges")
    java=one(java,'TextView when=text("◷ "+TaskLogic.when(t.due)+"     ◈ "+category,12,MUTED,false);',
       'TextView when=text("▢ "+TaskLogic.when(t.due)+"   ·   "+category,12,MUTED,false);',
       "task details type")
    java=one(java,
       'pane.addView(text("◈  "+TaskOrganization.category(task.category),14,CategoryRegistry.color(this,task.category),true));gap(pane,12);',
       '''LinearLayout categoryRow=row();
        ImageView categoryIcon=UiDesign.icon(this,"folder",CategoryRegistry.color(this,task.category),22);
        categoryRow.addView(categoryIcon,new LinearLayout.LayoutParams(dp(24),dp(24)));
        categoryRow.addView(text("  "+TaskOrganization.category(task.category),14,CategoryRegistry.color(this,task.category),true));
        pane.addView(categoryRow);gap(pane,16);''',
       "detail category icon")
    java=one(java,'pane.addView(text("▢  Fecha límite",13,MUTED,true));',
       'pane.addView(text("Fecha y hora límite",14,MUTED,true));',
       "detail due label")
    java=one(java,
       'pane.addView(text("◷  Prioridad: "+priority+" (automática)",14,TaskPriority.color(priority),true));',
       '''pane.addView(text("Prioridad automática · "+priority,14,TaskPriority.color(priority),true));
        gap(pane,14);
        pane.addView(text("Recordatorios",14,INK,true));gap(pane,6);
        java.util.SortedSet<Integer> alerts=TaskLogic.offsets(task.offsets);
        StringBuilder offsetsLabel=new StringBuilder();
        for(int minutes:alerts){if(offsetsLabel.length()>0)offsetsLabel.append(" · ");offsetsLabel.append(TaskLogic.offsetName(minutes));}
        pane.addView(text(offsetsLabel.length()==0?"Sin avisos programados":offsetsLabel.toString(),13,MUTED,false));gap(pane,12);
        pane.addView(text("Repetición del aviso",14,INK,true));gap(pane,5);
        pane.addView(text(task.repeatMinutes==0?"No se repite":"Cada "+TaskLogic.offsetName(task.repeatMinutes).toLowerCase(new Locale("es","PE")),13,MUTED,false));''',
       "detail notice and repeat rows")

    # Calendar: month prominently ahead of weekly strip, with existing hours intact.
    java=one(java,'        LinearLayout week=card(body);week.addView(text("Mi semana",20,INK,true));',
       '        LinearLayout week=card(body);week.addView(text("Mi semana",18,INK,true));',
       "week label")
    java=one(java,'        c.addView(grid);gap(c,10);',
       '''        body.removeView(week);body.addView(week);
        c.addView(grid);gap(c,10);''',
       "month above week")
    java=one(java,'label=text(month.format(DateTimeFormatter.ofPattern("MMMM yyyy",new Locale("es","PE"))),19,INK,true);',
       'label=text(month.format(DateTimeFormatter.ofPattern("MMMM yyyy",new Locale("es","PE"))),21,INK,true);',
       "month title")
    java=one(java,'TextView d=text(n+(has?"\\n•":""),14,date.equals(selectedDay)?0xffffffff:INK,date.equals(LocalDate.now()));',
       'TextView d=text(n+(has?"\\n•":""),14,date.equals(selectedDay)?0xffffffff:INK,date.equals(LocalDate.now()));',
       "date label stable")
    java=one(java,'d.setBackground(rounded(date.equals(selectedDay)?GREEN:date.equals(LocalDate.now())?PALE:0xffffffff,12));',
       'd.setBackground(rounded(date.equals(selectedDay)?GREEN:date.equals(LocalDate.now())?PALE:0xffffffff,22));',
       "calendar day selection")
    java=one(java,'TextView guide=text("La prioridad se calcula sola según la fecha límite. Puedes personalizar tus categorías.",12,MUTED,false);',
       'TextView guide=text("La prioridad cambia automáticamente según la fecha límite.",12,MUTED,false);',
       "remove redundant guide")

    # Review panel: summary based on actual inbox data; never fake a percentage.
    java=one(java,'List<Store.Inbox> inbox=Store.get(this).inbox();\n        reviewCount=',
       '''List<Store.Inbox> inbox=Store.get(this).inbox();
        LinearLayout reviewSummary=card(body);
        reviewSummary.addView(text("Propuestas por revisar",18,INK,true));gap(reviewSummary,8);
        reviewSummary.addView(text(inbox.size()+" propuestas pendientes",15,GREEN,true));
        reviewSummary.addView(text("Selecciona una propuesta para confirmar si debe entrar en tu agenda.",12,MUTED,false));
        reviewCount=''', "review summary")
    java=one(java,'info.addView(text("▤  Tú decides qué entra en tu agenda",19,INK,true));',
       'info.addView(text("Revisa antes de guardar",19,INK,true));',
       "review header")

    # Editor and all its embedded modal controls share the same typography/spacing.
    java=one(java,'CheckBox schedule=new CheckBox(this);schedule.setText("Establecer fecha y hora límite");',
       'CheckBox schedule=new CheckBox(this);schedule.setButtonTintList(ColorStateList.valueOf(GREEN));schedule.setTextColor(INK);schedule.setText("Establecer fecha y hora límite");',
       "schedule checkbox style")
    java=one(java,'LinearLayout dateSection=card(box);dateSection.addView(text("▢  Fecha y hora de entrega",17,INK,true));',
       '''LinearLayout dateSection=card(box);
        LinearLayout dateHeading=row();dateHeading.addView(UiDesign.icon(this,"calendar",GREEN,24),new LinearLayout.LayoutParams(dp(24),dp(24)));
        dateHeading.addView(text("  Fecha y hora de entrega",17,INK,true));
        dateSection.addView(dateHeading);''',
       "date panel icon")
    java=one(java,'subtitle(box,"Avisarme antes");',
       '''LinearLayout remindersHeader=row();remindersHeader.addView(UiDesign.icon(this,"bell",GREEN,24),new LinearLayout.LayoutParams(dp(24),dp(24)));
        remindersHeader.addView(text("  Avisarme antes",17,INK,true));gap(box,12);box.addView(remindersHeader);gap(box,8);''',
       "reminder header icon")
    java=one(java,'box.addView(button("Más opciones · notas y repetición del aviso",()->advanced.setVisibility(advanced.getVisibility()==View.GONE?View.VISIBLE:View.GONE)));box.addView(advanced);',
       '''box.addView(button("Más opciones · notas y repetición del aviso  ›",()->{
          boolean visible=advanced.getVisibility()!=View.VISIBLE;
          advanced.setVisibility(visible?View.VISIBLE:View.GONE);
          if(visible)UiMotion.reveal(advanced);
        }));gap(box,10);box.addView(advanced);''',
       "expandable advanced options")
    java=one(java,'Spinner repeat=new Spinner(this);String[] repetitions=',
       'Spinner repeat=new Spinner(this);String[] repetitions=',"repeat choices remain")
    java=one(java,'        box.addView(categoryPicker);gap(box,6);',
       '''        categoryPicker.setBackground(outlined(PALE,15,STROKE));
        categoryPicker.setPadding(dp(12),dp(8),dp(10),dp(8));
        box.addView(categoryPicker);gap(box,8);''',
       "category selector spacing")
    java=one(java,'subtitle(box,"Categoría");',
       '''LinearLayout categoryHeading=row();categoryHeading.addView(UiDesign.icon(this,"folder",GREEN,24),new LinearLayout.LayoutParams(dp(24),dp(24)));
        categoryHeading.addView(text("  Categoría",17,INK,true));gap(box,12);box.addView(categoryHeading);gap(box,8);''',
       "category section icon")
    java=one(java,'box.addView(google);',
       'gap(box,16);box.addView(google);',
       "calendar linkage safe margin")
    java=one(java,'editor=dialogBuilder().setTitle(existing==null?"Nueva tarea":"Editar tarea")',
       'editor=dialogBuilder().setTitle(existing==null?"Nueva tarea":"Editar tarea")',
       "editor dialog contract")

    # Category manager: color-coded rows, actual counts and a nonremovable General.
    java=one(java,'TextView dot=text("●",22,entry.color,true);row.addView(dot);',
       '''ImageView categoryIcon=UiDesign.icon(this,"folder",entry.color,26);
            row.addView(categoryIcon,new LinearLayout.LayoutParams(dp(26),dp(26)));''',
       "category row icons")
    java=one(java,'TextView name=text("  "+entry.name,16,INK,true);',
       '''int count=0;for(Task task:Store.get(this).all())if(entry.name.equalsIgnoreCase(TaskOrganization.category(task.category)))count++;
            LinearLayout categoryInfo=column();categoryInfo.addView(text(entry.name,15,INK,true));
            categoryInfo.addView(text(count+(count==1?" tarea":" tareas"),12,MUTED,false));
            TextView name=text("  ",1,INK,false);''',
       "category counts")
    java=one(java,'row.addView(name,new LinearLayout.LayoutParams(0,-2,1));',
       'row.addView(categoryInfo,new LinearLayout.LayoutParams(0,-2,1));',
       "category information layout")
    java=one(java,'            card.addView(row);\n        }\n        ScrollView scroll=',
       '''            card.addView(row);
            card.setBackground(outlined(entry.color==CategoryRegistry.COLORS[0]?0xfff1f4ff:
                (0xfff6f8ff),19,STROKE));
        }
        ScrollView scroll=''', "category card tint")
    java=one(java,'dialogBuilder().setTitle("Mis categorías").setView(scroll)',
       'dialogBuilder().setTitle("Gestión de categorías").setView(scroll)',
       "category dialog title")

    # A single palette for all dialogs, including nested pickers.
    main_styles=RES/"values/styles.xml"
    xml=main_styles.read_text(encoding="utf-8")
    xml=xml.replace("#3957D7","#3B5FF1").replace("#F6F8FC","#F5F8FF")
    xml=xml.replace('<item name="android:fontFamily">sans</item>',
                    '<item name="android:fontFamily">sans-serif</item>')
    xml=one(xml,'<item name="android:windowBackground">@drawable/dialog_background</item>',
       '<item name="android:windowBackground">@drawable/dialog_background</item>\n'
       '        <item name="android:windowAnimationStyle">@style/AgendaDialogMotion</item>',"dialog entrance/exit")
    xml=one(xml,'    <style name="PhotoTapTheme"',
       '''    <style name="AgendaDialogMotion">
        <item name="android:windowEnterAnimation">@android:anim/fade_in</item>
        <item name="android:windowExitAnimation">@android:anim/fade_out</item>
    </style>
    <style name="PhotoTapTheme"''',"window animation style")
    v31=RES/"values-v31/styles.xml";xml31=v31.read_text(encoding="utf-8")
    xml31=xml31.replace("#3957D7","#3B5FF1").replace("#F6F8FC","#F5F8FF")
    xml31=xml31.replace('<item name="android:fontFamily">sans</item>',
                   '<item name="android:fontFamily">sans-serif</item>')
    dialogpath=RES/"drawable/dialog_background.xml"
    dialog=dialogpath.read_text(encoding="utf-8")
    dialog=dialog.replace("#E0E8F8","#DCE5F5").replace('android:radius="24dp"','android:radius="26dp"')
    dialog=dialog.replace('android:left="8dp" android:top="8dp" android:right="8dp" android:bottom="8dp"',
                          'android:left="12dp" android:top="12dp" android:right="12dp" android:bottom="12dp"')

    # Nav menu icons are vector-drawn by UiDesign but its drawable resources and
    # the approved top-right + drawable are retained without modification.
    if next(line for line in java.splitlines() if 'setTag("new_task_button")' in line)!=original_plus:
        raise RuntimeError("Approved top-right plus was modified")
    if "TopPlusButtonMotion.install(this)" not in java:raise RuntimeError("TopPlusButtonMotion lost")
    mainpath.write_text(java,encoding="utf-8")
    main_styles.write_text(xml,encoding="utf-8")
    v31.write_text(xml31,encoding="utf-8")
    dialogpath.write_text(dialog,encoding="utf-8")
    (SRC/"UiDesign.java").write_text((PHASE/"UiDesign.java").read_text(encoding="utf-8"),encoding="utf-8")
    print("PASS: shared fonts, icons, cards, category list, task details, calendar, review and modal system")

if __name__=="__main__":apply()
