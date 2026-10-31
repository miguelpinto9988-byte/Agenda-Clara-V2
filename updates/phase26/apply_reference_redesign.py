#!/usr/bin/env python3
"""Apply approved modern colourful iconography and native date/time/category pickers.

Runs after phase25. Layout/callbacks remain Android Java and existing user data is
not touched. In particular the approved 108dp top-right + PNG and motion remain.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/java/pe/agendaclara/app"
stage=Path(__file__).resolve().parent

def one(text,old,new,label):
    n=text.count(old)
    if n!=1:raise RuntimeError(f"phase26 {label}: expected one anchor, got {n}")
    return text.replace(old,new,1)

def apply():
    mp=root/"MainActivity.java"
    ui=root/"UiDesign.java"
    sp=root/"ScheduleActivity.java"
    main=mp.read_text(encoding="utf-8")
    designs=ui.read_text(encoding="utf-8")
    schedule=sp.read_text(encoding="utf-8")
    plus=next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)
    if not plus or "TopPlusButtonMotion.install(this)" not in main:
        raise RuntimeError("Approved plus button missing")
    if "selectedCategory=\"General\"" not in main:raise RuntimeError("Latest category base missing")
    if (root/"ModernGlyph.java").exists() or (root/"ModernPickers.java").exists():
        raise RuntimeError("Phase26 classes already installed")

    # Date and time now open branded, fully native pickers rather than the
    # device's oversized system calendar/green clock.
    main=one(main,
      'DatePickerDialog picker=new DatePickerDialog(this,(p,y,m,d)->{date[0]=LocalDate.of(y,m+1,d);dateSet[0]=true;refresh.run();},date[0].getYear(),date[0].getMonthValue()-1,date[0].getDayOfMonth());picker.getDatePicker().setFirstDayOfWeek(Calendar.MONDAY);trackDialog(picker);picker.show();',
      'ModernPickers.showDate(this,date[0],chosenDate->{date[0]=chosenDate;dateSet[0]=true;refresh.run();});',
      "date dialog")
    main=one(main,
      'TimePickerDialog picker=new TimePickerDialog(this,android.R.style.Theme_Material_Light_Dialog_Alert,(p,h,m)->{time[0]=LocalTime.of(h,m);timeSet[0]=true;refresh.run();},time[0].getHour(),time[0].getMinute(),false);picker.setTitle("Hora · 12 horas");trackDialog(picker);picker.show();',
      'ModernPickers.showTime(this,time[0],chosenTime->{time[0]=chosenTime;timeSet[0]=true;refresh.run();});',
      "time dialog")
    main=one(main,
      'dateSection.addView(timeBtn);',
      '''ModernGlyph.button(dateBtn,"date",ModernGlyph.BLUE,19);
        ModernGlyph.button(timeBtn,"time",ModernGlyph.VIOLET,20);
        dateSection.addView(timeBtn);''',
      "always visible picker icons")
    main=one(main,
      'categoryHeading.addView(UiDesign.icon(this,"folder",GREEN,24),',
      'categoryHeading.addView(ModernGlyph.view(this,"folder",ModernGlyph.AMBER,24),',
      "category heading icon")
    main=one(main,
      'dateHeading.addView(UiDesign.icon(this,"calendar",GREEN,24),',
      'dateHeading.addView(ModernGlyph.view(this,"date",ModernGlyph.BLUE,24),',
      "date heading icon")
    main=one(main,
      'remindersHeader.addView(UiDesign.icon(this,"bell",GREEN,24),',
      'remindersHeader.addView(ModernGlyph.view(this,"bell",ModernGlyph.AMBER,24),',
      "reminder heading icon")

    # Keep the hidden Spinner only as a backwards-compatible selection model
    # for existing save/draft and category-creation callbacks.
    main=one(main,
      'box.addView(categoryPicker);gap(box,8);',
      '''box.addView(categoryPicker,new LinearLayout.LayoutParams(dp(1),dp(1)));
        categoryPicker.setVisibility(View.GONE);
        Button categoryDisplay=button(TaskOrganization.category(currentCategory)+"  ›",()->{});
        categoryDisplay.setGravity(Gravity.CENTER_VERTICAL|Gravity.START);
        categoryDisplay.setContentDescription("Seleccionar categoría: "+TaskOrganization.category(currentCategory));
        categoryDisplay.setMinHeight(dp(58));
        categoryDisplay.setBackground(UiDesign.tintedBackground(this,
            CategoryRegistry.color(this,currentCategory),16,18));
        ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,currentCategory),24);
        categoryDisplay.setOnClickListener(v->ModernPickers.showCategory(this,
            String.valueOf(categoryPicker.getSelectedItem()),selected->{
                for(int i=0;i<categoriesAdapter.getCount();i++)
                    if(selected.equalsIgnoreCase(categoriesAdapter.getItem(i)))categoryPicker.setSelection(i);
                categoryDisplay.setText(selected+"  ›");
                categoryDisplay.setContentDescription("Seleccionar categoría: "+selected);
                categoryDisplay.setBackground(UiDesign.tintedBackground(this,
                    CategoryRegistry.color(this,selected),16,18));
                ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,selected),24);
            }));
        box.addView(categoryDisplay,new LinearLayout.LayoutParams(-1,dp(60)));gap(box,9);''',
      "colored category selection card")
    main=one(main,
      'for(int i=0;i<categoriesAdapter.getCount();i++)if(categoriesAdapter.getItem(i).equalsIgnoreCase(newName))categoryPicker.setSelection(i);',
      '''for(int i=0;i<categoriesAdapter.getCount();i++)
                if(categoriesAdapter.getItem(i).equalsIgnoreCase(newName))categoryPicker.setSelection(i);
            categoryDisplay.setText(newName+"  ›");
            categoryDisplay.setContentDescription("Seleccionar categoría: "+newName);
            categoryDisplay.setBackground(UiDesign.tintedBackground(this,
                CategoryRegistry.color(this,newName),16,18));
            ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,newName),24);''',
      "newly created category keeps visible selection")

    # The colour chooser becomes a non-dismissable visual grid; users see the
    # same colours and corresponding icon as their final category cards.
    main=one(main,
      'pane.addView(colors);gap(pane,12);',
      '''pane.addView(colors,new LinearLayout.LayoutParams(dp(1),dp(1)));
        colors.setVisibility(View.GONE);
        GridLayout palette=new GridLayout(this);palette.setColumnCount(3);
        java.util.ArrayList<LinearLayout> tiles=new java.util.ArrayList<>();
        final Runnable[] repaintTiles={null};
        repaintTiles[0]=()->{
            for(int i=0;i<tiles.size();i++){
                int tone=CategoryRegistry.COLORS[i];boolean active=i==colors.getSelectedItemPosition();
                LinearLayout tile=tiles.get(i);
                tile.setBackground(UiDesign.tintedBackground(this,tone,16,active?24:11));
                tile.setElevation(active?dp(3):dp(1));
                if(active)tile.setContentDescription(CategoryRegistry.COLOR_NAMES[i]+", color elegido");
                else tile.setContentDescription(CategoryRegistry.COLOR_NAMES[i]);
            }
        };
        for(int i=0;i<CategoryRegistry.COLORS.length;i++){
            final int index=i;int tone=CategoryRegistry.COLORS[i];
            LinearLayout tile=column();tile.setGravity(Gravity.CENTER);
            tile.setPadding(dp(4),dp(10),dp(4),dp(10));
            tile.addView(ModernGlyph.view(this,i%3==0?"folder":i%3==1?"check":"bell",
                            UiDesign.accentInk(tone),32),
                         new LinearLayout.LayoutParams(dp(36),dp(36)));
            TextView nameLabel=text(CategoryRegistry.COLOR_NAMES[i],12,UiDesign.accentInk(tone),true);
            nameLabel.setGravity(Gravity.CENTER);tile.addView(nameLabel);
            GridLayout.LayoutParams lp=new GridLayout.LayoutParams(
                GridLayout.spec(i/3),GridLayout.spec(i%3,1f));
            lp.width=0;lp.height=dp(90);lp.setMargins(dp(3),dp(3),dp(3),dp(3));
            palette.addView(tile,lp);tiles.add(tile);
            tile.setOnClickListener(v->{colors.setSelection(index);repaintTiles[0].run();});
        }
        repaintTiles[0].run();pane.addView(palette);gap(pane,12);''',
      "replace popup palette with colored icon tiles")

    # Actual two/three-colour strokes in task, navigation and category rows.
    main=one(main,
      'ImageView icon=UiDesign.icon(this,UiDesign.statusIcon(labels[n]),MUTED,26);',
      '''String[] iconTypes={"notes","date","check","backup"};
        ImageView icon=ModernGlyph.view(this,iconTypes[n],page==n?ModernGlyph.BLUE:ModernGlyph.CYAN,26);''',
      "navigation iconography")
    main=one(main,
      'ImageView categoryIcon=UiDesign.icon(this,"folder",UiDesign.accentInk(entry.color),26);',
      'ImageView categoryIcon=ModernGlyph.view(this,"folder",UiDesign.accentInk(entry.color),26);',
      "category manager iconography")
    main=one(main,
      'ImageView categoryIcon=UiDesign.icon(this,"folder",UiDesign.accentInk(CategoryRegistry.color(this,task.category)),22);',
      'ImageView categoryIcon=ModernGlyph.view(this,"folder",UiDesign.accentInk(CategoryRegistry.color(this,task.category)),22);',
      "task detail iconography")

    # Connections tabs are recognizable branded objects, not plain text tabs.
    main=one(main,
      'String[] labels={"WhatsApp","Calendar","Avisos y widgets"};',
      'String[] labels={"WhatsApp","Calendario","Opciones"};',
      "tabs labels")
    main=one(main,
      'b.setTextSize(12);b.setPadding(dp(3),0,dp(3),0);b.setMinWidth(0);',
      '''b.setTextSize(11);b.setPadding(dp(4),0,dp(4),0);b.setMinWidth(0);
            ModernGlyph.button(b,new String[]{"whatsapp","google-calendar","widgets"}[n],
                               new int[]{ModernGlyph.GREEN,ModernGlyph.BLUE,ModernGlyph.VIOLET}[n],20);''',
      "connections branded persistent tabs")
    # An action's icon is independent from the pressed background drawable.
    designs=one(designs,
      'if(name==null)return;\n        OutlineIcon icon=new OutlineIcon(name,b.getCurrentTextColor()==0xffffffff?0xffffffff:BLUE);\n        icon.setBounds(0,0,dp(b.getContext(),18),dp(b.getContext(),18));\n        b.setCompoundDrawables(icon,null,null,null);b.setCompoundDrawablePadding(dp(b.getContext(),7));',
      '''if(s.contains("whatsapp"))name="whatsapp";
        else if(s.contains("google calendar"))name="google-calendar";
        else if(s.contains("copia")||s.contains("exportar")||s.contains("restaurar"))name="backup";
        else if(s.contains("widget"))name="widgets";
        else if(s.contains("notificac"))name="bell";
        else if(s.contains("preferencia"))name="settings";
        else if(s.contains("foto"))name="photo";
        else if(s.contains("clase"))name="manual";
        if(name==null)return;
        int accent="whatsapp".equals(name)?ModernGlyph.GREEN:
                   "bell".equals(name)?ModernGlyph.AMBER:
                   "folder".equals(name)?ModernGlyph.AMBER:
                   "repeat".equals(name)?ModernGlyph.GREEN:
                   "settings".equals(name)?ModernGlyph.VIOLET:ModernGlyph.BLUE;
        ModernGlyph.button(b,name,accent,20);''',
      "branded action icons don't vanish on press")

    # Upgrade native academic-header actions and course/photo sections.
    schedule=one(schedule,
      'bar.addView(back,new LinearLayout.LayoutParams(dp(48),dp(48)));',
      '''back.setText("");back.setContentDescription("Volver");
        ModernGlyph backIcon=new ModernGlyph("back",ModernGlyph.BLUE);
        backIcon.setBounds(0,0,dp(23),dp(23));
        back.setCompoundDrawables(null,backIcon,null,null);
        back.setGravity(Gravity.CENTER);
        bar.addView(back,new LinearLayout.LayoutParams(dp(48),dp(48)));''',
      "academic back icon")
    schedule=one(schedule,
      'bar.addView(help,new LinearLayout.LayoutParams(dp(46),dp(48)));',
      '''help.setText("");help.setContentDescription("Ayuda del horario");
        ModernGlyph helpIcon=new ModernGlyph("help",ModernGlyph.BLUE);
        helpIcon.setBounds(0,0,dp(23),dp(23));
        help.setCompoundDrawables(null,helpIcon,null,null);
        help.setGravity(Gravity.CENTER);
        bar.addView(help,new LinearLayout.LayoutParams(dp(46),dp(48)));''',
      "academic help icon")
    schedule=one(schedule,
      'private void head(LinearLayout parent,String heading,String description){parent.addView(txt(heading,18,INK,true));space(parent,7);parent.addView(txt(description,13,MUTED,false));}',
      '''private void head(LinearLayout parent,String heading,String description){
        LinearLayout titleRow=row();
        String icon=heading.contains("foto")?"photo":
                    heading.contains("manual")?"manual":
                    heading.contains("recordatorio")?"bell":
                    heading.contains("curso")?"notes":"date";
        titleRow.addView(ModernGlyph.view(this,icon,ModernGlyph.BLUE,28),
            new LinearLayout.LayoutParams(dp(29),dp(29)));
        TextView headingText=txt(heading.replace("▣  ","").replace("✎  ",""),18,INK,true);
        LinearLayout.LayoutParams textParams=new LinearLayout.LayoutParams(0,-2,1);
        textParams.leftMargin=dp(10);titleRow.addView(headingText,textParams);
        parent.addView(titleRow);space(parent,10);
        parent.addView(txt(description,13,MUTED,false));
    }''',
      "academic image/manual/course headings")

    if next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)!=plus:
        raise RuntimeError("Top-right plus call site changed")
    for name in ("ModernGlyph","ModernPickers"):
        (root/(name+".java")).write_text((stage/(name+".java")).read_text(encoding="utf-8"),encoding="utf-8")
    mp.write_text(main,encoding="utf-8")
    ui.write_text(designs,encoding="utf-8")
    sp.write_text(schedule,encoding="utf-8")
    print("PASS phase26: stable multicolour icons and fully branded date, clock, category and colour dialogs")

if __name__=="__main__":apply()
