#!/usr/bin/env python3
"""Phase27: transparent PNG icon atlas, independent category symbol/color selection,
month-aware notification repeats, and faster consistent native pickers.

Applies after phase26 without altering top plus, tasks, existing alarm offsets or
database format. Categories are backed up by existing prefs with optional icon.
"""
from pathlib import Path
P=Path(__file__).resolve().parents[2]/"AgendaClara/app"
SRC=P/"src/main/java/pe/agendaclara/app"
STAGE=Path(__file__).resolve().parent
def replace(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"phase27 {label}: expected 1 match, got {n}")
    return s.replace(old,new,1)
def section(s,start,end,content,label):
    if s.count(start)!=1:raise RuntimeError(f"phase27 {label} start {s.count(start)}")
    i=s.index(start);j=s.find(end,i+len(start))
    if j<0:raise RuntimeError("phase27 "+label+" end missing")
    return s[:i]+content+s[j:]
def run():
    mainpath=SRC/"MainActivity.java";catpath=SRC/"CategoryRegistry.java"
    logicpath=SRC/"TaskLogic.java";sp=SRC/"ScheduleActivity.java"
    ui=SRC/"UiDesign.java";pickerpath=SRC/"ModernPickers.java"
    m=mainpath.read_text();c=catpath.read_text();logic=logicpath.read_text()
    schedule=sp.read_text();design=ui.read_text();pick=pickerpath.read_text()
    header=next((x for x in m.splitlines() if 'setTag("new_task_button")' in x),None)
    if not header or 'TopPlusButtonMotion.install(this)' not in m:raise RuntimeError("Approved + missing")
    if 'ModernPickers.showDate(this' not in m:raise RuntimeError("Phase26 missing")
    for cls in ("PngIcons","CategoryDesigner","RepeatPicker","ReminderSelector"):
        if (SRC/(cls+".java")).exists():raise RuntimeError("Phase27 already applied")
    # Preserve prior prefs; new icon key is optional, defaults to folder.
    c=replace(c,'        public final int color;\n        Entry(String name,int color){this.name=name;this.color=color;}',
      '''        public final int color;
        public final String icon;
        Entry(String name,int color){this(name,color,"folder");}
        Entry(String name,int color,String icon){
            this.name=name;this.color=color;this.icon=PngIcons.safe(icon);
        }''',"category entry icon")
    c=replace(c,'object.put("color",e.color);array.put(object);',
              'object.put("color",e.color);object.put("icon",e.icon);array.put(object);',
              "persist category icon")
    c=replace(c,'items.add(new Entry(name,record.optInt("color",COLORS[items.size()%COLORS.length])));',
              'items.add(new Entry(name,record.optInt("color",COLORS[items.size()%COLORS.length]),record.optString("icon","folder")));',
              "backward compatible icon parse")
    c=replace(c,'    public static synchronized boolean save(Context c,String previous,String desired,int color){',
       '''    public static synchronized String icon(Context c,String name){
        for(Entry e:all(c))if(e.name.equalsIgnoreCase(name))return e.icon;
        return "folder";
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color){
        return save(c,previous,desired,color,previous==null?"folder":icon(c,previous));
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color,String symbol){''',
       "independent icon persist API")
    c=replace(c,'entries.set(oldIndex,new Entry(name,color));','entries.set(oldIndex,new Entry(name,color,symbol));',"edit icon")
    c=replace(c,'}else entries.add(new Entry(name,color));','}else entries.add(new Entry(name,color,symbol));',"new icon")
    # Months in repeat mode are actual calendar months, not a deceptive 30-day approximation.
    logic=replace(logic,
       '        if(t.repeatMinutes>0&&!offsets.isEmpty()) {',
       '''        if(t.repeatMinutes==-1&&!offsets.isEmpty()){
            long start=t.due-offsets.first()*60000L;
            java.time.ZonedDateTime first=java.time.Instant.ofEpochMilli(start)
                .atZone(java.time.ZoneId.systemDefault());
            for(int i=0;i<1800;i++){
                long at=first.plusMonths(i).toInstant().toEpochMilli();
                if(at>t.due)break;
                if(at>after&&at<best){best=at;break;}
            }
        }
        if(t.repeatMinutes>0&&!offsets.isEmpty()) {''',
       "exact calendar monthly recurrence")
    # Icons must be PNG bitmaps rather than Canvas strokes.
    for old,new in (("ModernGlyph.view(","PngIcons.view("),("ModernGlyph.button(","PngIcons.button(")):
        m=m.replace(old,new)
        schedule=schedule.replace(old,new)
        design=design.replace(old,new)
        pick=pick.replace(old,new)
    # Also route every existing shared OutlineIcon view to a permanent PNG;
    # old screens not pictured in the reference must use the same icon system.
    design=section(design,
       '    public static ImageView icon(Activity a,String name,int color,int size){',
       '    public static String statusIcon',
       '''    public static ImageView icon(Activity a,String name,int color,int size){
        return PngIcons.view(a,name,color,size);
    }
''',
       "global icon facade")
    # Existing category manager and all task tiles inherit saved symbol.
    m=replace(m,
       'PngIcons.view(this,"folder",UiDesign.accentInk(entry.color),26)',
       'PngIcons.view(this,CategoryRegistry.icon(this,entry.name),26)',
       "saved category icons in manager")
    m=replace(m,
       'PngIcons.view(this,"folder",UiDesign.accentInk(CategoryRegistry.color(this,task.category)),22)',
       'PngIcons.view(this,CategoryRegistry.icon(this,task.category),22)',
       "saved category icons in task detail")
    m=replace(m,
       'UiDesign.icon(this,"folder",UiDesign.accentInk(categoryColor),17)',
       'PngIcons.view(this,CategoryRegistry.icon(this,category),17)',
       "saved category icon in task card")
    m=replace(m,
       'UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active);',
       '''UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active);
            PngIcons.button(chip,CategoryRegistry.icon(this,label),18);''',
       "saved category icon in filter chips")
    m=replace(m,
       'PngIcons.button(categoryDisplay,"folder",CategoryRegistry.color(this,currentCategory),24);',
       'PngIcons.button(categoryDisplay,CategoryRegistry.icon(this,currentCategory),24);',
       "visible editor category symbol")
    m=replace(m,
       'PngIcons.button(categoryDisplay,"folder",CategoryRegistry.color(this,selected),24);',
       'PngIcons.button(categoryDisplay,CategoryRegistry.icon(this,selected),24);',
       "selected editor category symbol")
    m=replace(m,
       'PngIcons.button(categoryDisplay,"folder",CategoryRegistry.color(this,newName),24);',
       'PngIcons.button(categoryDisplay,CategoryRegistry.icon(this,newName),24);',
       "new editor category symbol")
    pick=replace(pick,
       'PngIcons.view(a,"folder",color,28)',
       'PngIcons.view(a,entry.icon,28)',
       "category popup saved icons")
    # Remove large embedded category-spinner/color grid; new picker separates
    # symbol from colour and previews the combination without giant dropdowns.
    m=section(m,
       '    void showCategoryEditor(String existing,java.util.function.Consumer<String> onSaved){',
       '    String join(Collection<Integer> offsets)',
       '''    void showCategoryEditor(String existing,java.util.function.Consumer<String> onSaved){
        CategoryDesigner.show(this,existing,onSaved);
    }
''',
       "category editor delegation")
    # Keep legacy spinner as an invisible persistence model. Repetition values
    # may be month-aware (-1) or custom arbitrary-minute intervals.
    m=replace(m,
       'advanced.addView(repeat);',
       '''repeat.setVisibility(View.GONE);advanced.addView(repeat);
        final int[] repeatValue={rv};
        boolean known=false;
        for(int j=0;j<intervals.length;j++)if(rv==intervals[j])known=true;
        if(!known){intervals[0]=rv;repeat.setSelection(0);}
        Button repeatButton=button(RepeatPicker.label(rv)+"  ›",()->{});
        PngIcons.button(repeatButton,"repeat",21);
        repeatButton.setContentDescription("Repetir aviso: "+RepeatPicker.label(rv));
        repeatButton.setOnClickListener(v->RepeatPicker.show(this,repeatValue[0],value->{
            repeatValue[0]=value;intervals[0]=value;repeat.setSelection(0);
            repeatButton.setText(RepeatPicker.label(value)+"  ›");
            repeatButton.setContentDescription("Repetir aviso: "+RepeatPicker.label(value));
        }));
        advanced.addView(repeatButton,new LinearLayout.LayoutParams(-1,dp(54)));''',
       "notification recurrence native popup")
    m=replace(m,
       'task.repeatMinutes==0?"No se repite":"Cada "+TaskLogic.offsetName(task.repeatMinutes).toLowerCase(new Locale("es","PE"))',
       'RepeatPicker.label(task.repeatMinutes)',
       "detail recurrence friendly labels")
    # A new custom reminder list keeps the original SortedSet and save callback.
    m=section(m,
       '        reminderButton.setOnClickListener(v->{',
       '        LinearLayout advanced=column();',
       '''        PngIcons.button(reminderButton,"bell",20);
        reminderButton.setOnClickListener(v->ReminderSelector.show(this,offsets,selected->{
            offsets.clear();offsets.addAll(selected);redraw.run();
        }));
''',
       "reminder options popup")
    # Keep actual saved icon when the user renames a category; no symbol reset.
    # Navigation icons and header icons already point to PNG calls above.
    # For the academic back/help control, compound drawables must be PNG too.
    schedule=replace(schedule,
       'ModernGlyph backIcon=new ModernGlyph("back",ModernGlyph.BLUE);',
       'android.graphics.drawable.Drawable backIcon=getDrawable(PngIcons.id(this,"back"));',
       "back button PNG")
    schedule=replace(schedule,
       'ModernGlyph helpIcon=new ModernGlyph("help",ModernGlyph.BLUE);',
       'android.graphics.drawable.Drawable helpIcon=getDrawable(PngIcons.id(this,"help"));',
       "help button PNG")
    # Native calendar/clock modals are already branded. Removing the costly
    # recursive font pass reduces latency and helps prevent a visible frozen UI.
    pick=replace(pick,
       '            root.post(()->UiDesign.polishTree(root));',
       '''            // Components already have explicit fonts; avoid an expensive
            // recursive relayout while a picker is opening.''',
       "picker startup performance")
    # Reuse dial labels on a time change rather than rebuilding twelve views.
    pick=replace(pick,
       '            dial.removeAllViews();\n            for(int j=1;j<=12;j++){',
       '''            if(dial.getChildCount()==0)for(int j=1;j<=12;j++){''',
       "clock lazy initial dial")
    pick=replace(pick,
       '                cell.setOnClickListener(v->{hour[0]=value;hours.setValue(value);redraw[0].run();});\n            }\n        };',
       '''                cell.setOnClickListener(v->{hour[0]=value;hours.setValue(value);redraw[0].run();});
            }
            for(int j=0;j<dial.getChildCount();j++){
                TextView cell=(TextView)dial.getChildAt(j);
                boolean active=j+1==hour[0];
                cell.setTextColor(active?0xffffffff:INK);
                cell.setBackground(active?ModernGlyph.rounded(a,BLUE,0,22):null);
            }
        };''',
       "fast dial recolour without rebuilding")
    # The approved blue header icon and click callback remain byte-identical.
    if next((x for x in m.splitlines() if 'setTag("new_task_button")' in x),None)!=header:
        raise RuntimeError("Header plus unexpectedly changed")
    for clazz in ("PngIcons","CategoryDesigner","RepeatPicker","ReminderSelector"):
        (SRC/(clazz+".java")).write_text((STAGE/(clazz+".java")).read_text())
    for file,content in ((mainpath,m),(catpath,c),(logicpath,logic),
                         (sp,schedule),(ui,design),(pickerpath,pick)):
        file.write_text(content)
    print("PASS phase27: PNG icons, saved category symbol+color, fast date/time UI, monthly and custom repeats")
if __name__=="__main__":run()
