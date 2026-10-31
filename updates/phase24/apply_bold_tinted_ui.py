#!/usr/bin/env python3
"""Phase24: category-coordinated cards, stronger type and outline icon weights.

Only presentation changes. Existing colors, tasks, alarm state and the approved
top-right plus drawable, size, click handler and animations are untouched.
"""
from pathlib import Path

SRC=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/java/pe/agendaclara/app"

def replace_one(source,old,new,label):
    count=source.count(old)
    if count!=1: raise RuntimeError(f"phase24 {label}: expected 1 source match, found {count}")
    return source.replace(old,new,1)

def apply():
    uipath=SRC/"UiDesign.java"
    mainpath=SRC/"MainActivity.java"
    schedulepath=SRC/"ScheduleActivity.java"
    ui=uipath.read_text(encoding="utf-8")
    main=mainpath.read_text(encoding="utf-8")
    schedule=schedulepath.read_text(encoding="utf-8")
    plus=next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)
    if not plus:raise RuntimeError("Approved header plus missing")
    if "Duración del evento" in main:raise RuntimeError("Phase23 field removal missing")

    ui=replace_one(ui,
        't.setTypeface(Typeface.create(heavy?"sans-serif-medium":"sans-serif",Typeface.NORMAL));',
        't.setTypeface(Typeface.create(heavy?"sans-serif":"sans-serif-medium",heavy?Typeface.BOLD:Typeface.NORMAL));',
        "strong but hierarchical typography")
    ui=replace_one(ui,
        'b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));',
        'b.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));',
        "strong button typography")
    ui=replace_one(ui,
        'paint.setStrokeWidth(1.85f);',
        'paint.setStrokeWidth(2.65f);',
        "heavier consistent outline glyphs")
    marker='    public static void card(View v){'
    helpers='''    /** White-mixed category hues keep dark text readable across user colors. */
    public static int blend(int base,int accent,float alpha){
        float a=Math.max(0f,Math.min(1f,alpha));
        int r=Math.round(android.graphics.Color.red(base)*(1f-a)+android.graphics.Color.red(accent)*a);
        int g=Math.round(android.graphics.Color.green(base)*(1f-a)+android.graphics.Color.green(accent)*a);
        int b=Math.round(android.graphics.Color.blue(base)*(1f-a)+android.graphics.Color.blue(accent)*a);
        return android.graphics.Color.rgb(r,g,b);
    }
    public static int accentInk(int color){
        return blend(INK,color,0.60f);
    }
    public static GradientDrawable tintedBackground(android.content.Context c,int accent,int radius,int intensity){
        float amount=Math.max(0.05f,Math.min(0.30f,intensity/100f));
        GradientDrawable background=shape(c,blend(SURFACE,accent,amount),radius,0);
        background.setStroke(dp(c,1),blend(BORDER,accent,0.34f));
        return background;
    }
    /** Category chip has the same tint/icon/outline as its full-size card. */
    public static void categoryChip(Button chip,int accent,boolean active){
        chip.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));
        chip.setTextColor(accentInk(accent));
        GradientDrawable surface=tintedBackground(chip.getContext(),accent,17,active?25:13);
        if(active)surface.setStroke(dp(chip.getContext(),2),accentInk(accent));
        chip.setBackground(new RippleDrawable(ColorStateList.valueOf((accent&0x00ffffff)|0x18000000),surface,null));
        OutlineIcon icon=new OutlineIcon("folder",accentInk(accent));
        icon.setBounds(0,0,dp(chip.getContext(),18),dp(chip.getContext(),18));
        chip.setCompoundDrawables(icon,null,null,null);
        chip.setCompoundDrawablePadding(dp(chip.getContext(),7));
    }
'''
    ui=replace_one(ui,marker,helpers+marker,"shared tinted category surfaces")

    # Category tabs and cards: complete card changes hue, not just its icon.
    main=replace_one(main,
        '''chip.setTextColor(active?0xffffffff:CategoryRegistry.color(this,label));
            chip.setBackground(outlined(active?GREEN:PALE,17,active?GREEN:STROKE));''',
        '''UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active);''',
        "category tabs")
    main=replace_one(main,
        '''card.setBackground(outlined(entry.color==CategoryRegistry.COLORS[0]?0xfff1f4ff:
                (0xfff6f8ff),19,STROKE));''',
        '''card.setBackground(UiDesign.tintedBackground(this,entry.color,19,17));''',
        "full category manager cards")
    main=replace_one(main,
        'ImageView categoryIcon=UiDesign.icon(this,"folder",entry.color,26);',
        'ImageView categoryIcon=UiDesign.icon(this,"folder",UiDesign.accentInk(entry.color),26);',
        "category manager icon contrast")
    main=replace_one(main,
        'categoryInfo.addView(text(entry.name,15,INK,true));',
        'categoryInfo.addView(text(entry.name,16,UiDesign.accentInk(entry.color),true));',
        "category name emphasis")
    main=replace_one(main,
        'categoryInfo.addView(text(count+(count==1?" tarea":" tareas"),12,MUTED,false));',
        'categoryInfo.addView(text(count+(count==1?" tarea":" tareas"),13,INK,false));',
        "category count emphasis")

    # A task's entire card follows its category, including the completion control.
    main=replace_one(main,
        'String category=TaskOrganization.category(t.category);\n        TextView when=',
        '''String category=TaskOrganization.category(t.category);
        int categoryColor=CategoryRegistry.color(this,category);
        card.setBackground(UiDesign.tintedBackground(this,categoryColor,20,14));
        check.setButtonTintList(ColorStateList.valueOf(UiDesign.accentInk(categoryColor)));
        TextView when=''',
        "category tinted task card")
    main=replace_one(main,
        'when.setMaxLines(2);details.addView(when);',
        '''when.setMaxLines(2);
        LinearLayout meta=row();
        meta.addView(UiDesign.icon(this,"folder",UiDesign.accentInk(categoryColor),17),
                     new LinearLayout.LayoutParams(dp(19),dp(19)));
        meta.addView(when,new LinearLayout.LayoutParams(0,-2,1));
        details.addView(meta);''',
        "task metadata icon")
    main=replace_one(main,
        'TextView chevron=text("›",28,GREEN,false);',
        'TextView chevron=text("›",28,UiDesign.accentInk(categoryColor),true);',
        "category task chevron")
    main=replace_one(main,
        'LinearLayout pane=column();pane.setPadding(dp(18),dp(12),dp(18),dp(18));\n        pane.addView(text(task.title,20,INK,true));',
        '''LinearLayout pane=column();pane.setPadding(dp(18),dp(12),dp(18),dp(18));
        pane.setBackground(UiDesign.tintedBackground(this,CategoryRegistry.color(this,task.category),20,11));
        pane.addView(text(task.title,20,INK,true));''',
        "tinted task detail panel")
    main=replace_one(main,
        'UiDesign.icon(this,"folder",CategoryRegistry.color(this,task.category),22)',
        'UiDesign.icon(this,"folder",UiDesign.accentInk(CategoryRegistry.color(this,task.category)),22)',
        "task detail category icon")
    main=replace_one(main,
        'text("  "+TaskOrganization.category(task.category),14,CategoryRegistry.color(this,task.category),true)',
        'text("  "+TaskOrganization.category(task.category),14,UiDesign.accentInk(CategoryRegistry.color(this,task.category)),true)',
        "task detail category text")

    # Editor category chooser reflects the selected category even before save.
    main=replace_one(main,
        '''categoryPicker.setBackground(outlined(PALE,15,STROKE));
        categoryPicker.setPadding(dp(12),dp(8),dp(10),dp(8));''',
        '''categoryPicker.setBackground(UiDesign.tintedBackground(this,CategoryRegistry.color(this,currentCategory),15,18));
        categoryPicker.setPadding(dp(12),dp(8),dp(10),dp(8));
        categoryPicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            public void onItemSelected(AdapterView<?> parent,View view,int position,long id){
                String category=String.valueOf(categoryPicker.getSelectedItem());
                categoryPicker.setBackground(UiDesign.tintedBackground(MainActivity.this,
                    CategoryRegistry.color(MainActivity.this,category),15,18));
                if(view instanceof TextView)UiDesign.text((TextView)view,true);
            }
            public void onNothingSelected(AdapterView<?> parent){}
        });''',
        "category picker live colors")

    # Editing category color also recolors the full floating editor and icon.
    main=replace_one(main,
        '''        pane.addView(colors);
        AlertDialog dialog=dialogBuilder().setTitle(existing==null?"Crear categoría":"Editar categoría")''',
        '''        pane.addView(colors);gap(pane,12);
        LinearLayout preview=row();preview.setPadding(dp(12),dp(12),dp(12),dp(12));
        ImageView colorIcon=UiDesign.icon(this,"folder",UiDesign.accentInk(CategoryRegistry.COLORS[colors.getSelectedItemPosition()]),28);
        preview.addView(colorIcon,new LinearLayout.LayoutParams(dp(30),dp(30)));
        TextView colorLabel=text("  Vista previa del color",14,INK,true);
        preview.addView(colorLabel);pane.addView(preview);
        colors.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            public void onItemSelected(AdapterView<?> parent,View view,int position,long id){
                int selected=CategoryRegistry.COLORS[position];
                pane.setBackground(UiDesign.tintedBackground(MainActivity.this,selected,20,12));
                preview.setBackground(UiDesign.tintedBackground(MainActivity.this,selected,16,24));
                colorIcon.setImageDrawable(new UiDesign.OutlineIcon("folder",UiDesign.accentInk(selected)));
                colorLabel.setTextColor(UiDesign.accentInk(selected));
                if(view instanceof TextView)UiDesign.text((TextView)view,true);
            }
            public void onNothingSelected(AdapterView<?> parent){}
        });
        AlertDialog dialog=dialogBuilder().setTitle(existing==null?"Crear categoría":"Editar categoría")''',
        "live tinted category editor modal")

    # Academic subject cards honor the course color, not just the side strip.
    schedule=replace_one(schedule,
        'LinearLayout c=card();c.setPadding(dp(12),dp(14),dp(12),dp(14));LinearLayout r=row();',
        '''LinearLayout c=card();c.setPadding(dp(12),dp(14),dp(12),dp(14));
            c.setBackground(UiDesign.tintedBackground(this,s.color,20,14));LinearLayout r=row();''',
        "academic subject cards")
    schedule=replace_one(schedule,
        'LinearLayout item=card();LinearLayout r=row();View strip=new View(this);',
        'LinearLayout item=card();item.setBackground(UiDesign.tintedBackground(this,s.color,20,16));LinearLayout r=row();View strip=new View(this);',
        "academic week/list cards")
    schedule=replace_one(schedule,
        'LinearLayout banner=card();View colorBand=new View(this);',
        'LinearLayout banner=card();banner.setBackground(UiDesign.tintedBackground(this,primary.color,20,14));View colorBand=new View(this);',
        "academic session banner")
    schedule=replace_one(schedule,
        'content.addView(txt(s.course,18,INK,true));',
        'content.addView(txt(s.course,18,UiDesign.accentInk(s.color),true));',
        "academic course color heading")
    schedule=replace_one(schedule,
        'details.addView(txt(s.course,17,INK,true));',
        'details.addView(txt(s.course,17,UiDesign.accentInk(s.color),true));',
        "academic saved class heading")
    schedule=replace_one(schedule,
        'circle.setStroke(dp(1),LINE);swatch.setBackground(circle);',
        'circle.setStroke(dp(2),UiDesign.accentInk(shade));swatch.setBackground(circle);',
        "strong course color swatches")

    if plus not in main or "TopPlusButtonMotion.install(this)" not in main:
        raise RuntimeError("Approved upper + artwork/button handler unexpectedly changed")
    uipath.write_text(ui,encoding="utf-8")
    mainpath.write_text(main,encoding="utf-8")
    schedulepath.write_text(schedule,encoding="utf-8")
    print("PASS phase24: stronger text/icons, colored category cards, task cards and class sessions; plus unchanged")

if __name__=="__main__":
    apply()
