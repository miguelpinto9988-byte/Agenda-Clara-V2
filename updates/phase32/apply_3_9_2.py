#!/usr/bin/env python3
"""Show each category's saved PNG on its chip; never draw a generic folder."""
from pathlib import Path
SRC=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
def one(src,old,new,name):
    if src.count(old)!=1:raise RuntimeError(f"phase32 {name}: expected one anchor, got {src.count(old)}")
    return src.replace(old,new,1)
def apply():
    main=(SRC/"MainActivity.java").read_text(encoding="utf-8")
    design=(SRC/"UiDesign.java").read_text(encoding="utf-8")
    registry=(SRC/"CategoryRegistry.java").read_text(encoding="utf-8")
    grad=GRADLE.read_text(encoding="utf-8")
    nav_before=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
    main=one(main,
        '''            UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(48));lp.rightMargin=dp(8);''',
        '''            UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active);
            ApprovedPng.button(chip,CategoryRegistry.icon(this,label),24);
            chip.setCompoundDrawablePadding(dp(11));
            chip.setSingleLine(true);
            chip.setEllipsize(android.text.TextUtils.TruncateAt.END);
            chip.setMinHeight(dp(54));
            chip.setPadding(dp(14),dp(8),dp(16),dp(8));
            chip.setContentDescription("Categoría "+label+(active?", seleccionada":""));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(54));lp.rightMargin=dp(10);''',
        "saved symbol on category chips")
    main=one(main,
        '''            ImageView categoryIcon=ApprovedPng.view(this,entry.icon,26);
            row.addView(categoryIcon,new LinearLayout.LayoutParams(dp(26),dp(26)));''',
        '''            ImageView categoryIcon=ApprovedPng.view(this,entry.icon,28);
            LinearLayout.LayoutParams iconSpace=new LinearLayout.LayoutParams(dp(32),dp(32));
            iconSpace.rightMargin=dp(12);
            row.addView(categoryIcon,iconSpace);''',
        "category manager icon size and separation")
    main=one(main,
        '''categoryHeading.addView(ModernGlyph.view(this,"folder",ModernGlyph.AMBER,24),new LinearLayout.LayoutParams(dp(24),dp(24)));''',
        '''ImageView categoryHeadingIcon=ApprovedPng.view(this,CategoryRegistry.icon(this,currentCategory),26);
        LinearLayout.LayoutParams categoryHeadingSpace=new LinearLayout.LayoutParams(dp(30),dp(30));
        categoryHeadingSpace.rightMargin=dp(10);
        categoryHeading.addView(categoryHeadingIcon,categoryHeadingSpace);''',
        "category editor title icon")
    main=one(main,
        '''                ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,selected),24);''',
        '''                ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,selected),24);
                categoryHeadingIcon.setImageDrawable(ApprovedPng.drawable(this,CategoryRegistry.icon(this,selected)));''',
        "change title icon after picking a category")
    main=one(main,
        '''            ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,newName),24);''',
        '''            ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,newName),24);
            categoryHeadingIcon.setImageDrawable(ApprovedPng.drawable(this,CategoryRegistry.icon(this,newName)));''',
        "change title icon after creating a category")
    main=one(main,
        '''        categoryRow.addView(categoryIcon,new LinearLayout.LayoutParams(dp(24),dp(24)));''',
        '''        LinearLayout.LayoutParams detailIconSpace=new LinearLayout.LayoutParams(dp(28),dp(28));
        detailIconSpace.rightMargin=dp(10);
        categoryRow.addView(categoryIcon,detailIconSpace);''',
        "task detail icon margin")
    main=one(main,
        '''categoryRow.addView(text("  "+TaskOrganization.category(task.category),14,''',
        '''categoryRow.addView(text(TaskOrganization.category(task.category),14,''',
        "remove artificial spaces in category label")
    design=one(design,
        '''        OutlineIcon icon=new OutlineIcon("folder",accentInk(accent));
        icon.setBounds(0,0,dp(chip.getContext(),18),dp(chip.getContext(),18));
        chip.setCompoundDrawables(icon,null,null,null);
        chip.setCompoundDrawablePadding(dp(chip.getContext(),7));
''',
        '''        // Saved category PNG assigned by caller; never draw a fixed folder.
''',
        "remove generic folder code in category chip")
    design=one(design,
        '    /** Category chip has the same tint/icon/outline as its full-size card. */',
        '    /** Category chip style and outline only; saved PNG comes from CategoryRegistry. */',
        "category style comment")
    registry=one(registry,
        '''        Entry(String name,int color){this(name,color,"folder");}
        Entry(String name,int color,String icon){this.name=name;this.color=color;this.icon=icon==null||icon.isEmpty()?"folder":icon;}''',
        '''        Entry(String name,int color){this(name,color,"other");}
        Entry(String name,int color,String icon){this.name=name;this.color=color;this.icon=safeIcon(name,icon);}
        private static String safeIcon(String category,String symbol){
            if(symbol==null||symbol.trim().isEmpty()||"folder".equalsIgnoreCase(symbol.trim()))
                return "Notas".equalsIgnoreCase(category)?"sticky_note":"other";
            return symbol.trim();
        }''',
        "old categories without icons use neutral other, not folder")
    registry=one(registry,
        'record.optString("icon","folder")',
        'record.optString("icon","other")',
        "legacy JSON icon fallback")
    registry=one(registry,
        '''        return "folder";
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color){''',
        '''        return "other";
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color){''',
        "unknown category fallback")
    nav_after=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
    if nav_after!=nav_before:raise RuntimeError("Bottom navigation unexpectedly changed")
    if 'new OutlineIcon("folder",accentInk(accent))' in design:raise RuntimeError("Legacy chip icon remains")
    grad=one(grad,"versionCode 32","versionCode 33","versionCode")
    grad=one(grad,"versionName '3.9.1'","versionName '3.9.2'","versionName")
    for name,text in [("MainActivity.java",main),("UiDesign.java",design),("CategoryRegistry.java",registry)]:
        (SRC/name).write_text(text,encoding="utf-8")
    GRADLE.write_text(grad,encoding="utf-8")
    print("PASS phase32: saved PNG in each category, 11dp icon/text gap, no generic folder, navigation untouched, 3.9.2")
if __name__=="__main__":apply()
