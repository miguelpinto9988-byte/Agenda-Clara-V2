#!/usr/bin/env python3
"""Install transparent approved PNG artwork and wire accessible symbol/color pickers.

Runs after phase26 on the reconstructed Android source. All changes are
guarded, reversible through feature branch, and preserve the approved top +.
"""
import base64,io,zipfile
from pathlib import Path

STAGE=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main"
SRC=ROOT/"java/pe/agendaclara/app"
DRAWABLE=ROOT/"res/drawable-nodpi"

def one(s,old,new,label):
    count=s.count(old)
    if count!=1:raise RuntimeError(f"phase27 {label}: expected one match, got {count}")
    return s.replace(old,new,1)

def install_png(zip_path,prefix):
    raw=base64.b64decode(zip_path.read_text(encoding="utf-8"))
    with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
        for item in bundle.infolist():
            if "/" in item.filename or not item.filename.endswith(".png"):raise RuntimeError("Invalid PNG archive path")
            data=bundle.read(item.filename)
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):raise RuntimeError("Invalid PNG "+item.filename)
            output=DRAWABLE/(prefix+item.filename)
            if output.exists():raise RuntimeError("Overwriting existing artwork "+str(output))
            output.write_bytes(data)
    return len(bundle.namelist())

def apply():
    DRAWABLE.mkdir(parents=True,exist_ok=True)
    count=install_png(STAGE/"reference_png_icons_zip.b64","ic_ref_")
    count+=install_png(STAGE/"category_png_icons_zip.b64","")
    mainpath=SRC/"MainActivity.java"
    uipath=SRC/"UiDesign.java"
    glyphpath=SRC/"ModernGlyph.java"
    pickerpath=SRC/"ModernPickers.java"
    registryfile=SRC/"CategoryRegistry.java"
    schedulefile=SRC/"ScheduleActivity.java"
    main=mainpath.read_text(encoding="utf-8")
    ui=uipath.read_text(encoding="utf-8")
    glyph=glyphpath.read_text(encoding="utf-8")
    pickers=pickerpath.read_text(encoding="utf-8")
    registry=registryfile.read_text(encoding="utf-8")
    schedule=schedulefile.read_text(encoding="utf-8")
    plus=next((x for x in main.splitlines() if 'setTag("new_task_button")' in x),None)
    if plus is None or "TopPlusButtonMotion.install(this)" not in main:
        raise RuntimeError("Approved plus button is missing")

    # Never tint these user-approved PNG images when a button is pressed.
    glyph=one(glyph,
      '''        ImageView iv=new ImageView(context);
        iv.setImageDrawable(new ModernGlyph(name,color));''',
      '''        ImageView iv=ApprovedPng.view(context,name,sizeDp);''',
      "stable PNG image views")
    glyph=one(glyph,
      '''        ModernGlyph glyph=new ModernGlyph(name,color);
        int size=UiDesign.dp(button.getContext(),iconDp);
        glyph.setBounds(0,0,size,size);
        button.setCompoundDrawables(glyph,null,null,null);
        button.setCompoundDrawablePadding(UiDesign.dp(button.getContext(),8));''',
      '''        ApprovedPng.button(button,name,iconDp);''',
      "stable PNG button icons")
    ui=one(ui,
      '''ImageView view=new ImageView(a);view.setImageDrawable(new OutlineIcon(name,color));''',
      '''ImageView view=ApprovedPng.view(a,name,size);''',
      "cross-screen PNG iconography")
    # Academic back and help actions should be PNG images, not text/Canvas only.
    schedule=one(schedule,'ModernGlyph backIcon=new ModernGlyph("back",ModernGlyph.BLUE);',
      'android.graphics.drawable.Drawable backIcon=ApprovedPng.drawable(this,"back");',"back PNG")
    schedule=one(schedule,'ModernGlyph helpIcon=new ModernGlyph("help",ModernGlyph.BLUE);',
      'android.graphics.drawable.Drawable helpIcon=ApprovedPng.drawable(this,"help");',"help PNG")

    # Categories persist the chosen image separately from the chosen color.
    registry=one(registry,
      '''        public final int color;
        Entry(String name,int color){this.name=name;this.color=color;}''',
      '''        public final int color;
        public final String icon;
        Entry(String name,int color){this(name,color,"folder");}
        Entry(String name,int color,String icon){this.name=name;this.color=color;this.icon=icon==null||icon.isEmpty()?"folder":icon;}''',
      "category icon model")
    registry=one(registry,
      'object.put("name",e.name);object.put("color",e.color);array.put(object);',
      'object.put("name",e.name);object.put("color",e.color);object.put("icon",e.icon);array.put(object);',
      "persist custom icon")
    registry=one(registry,
      'items.add(new Entry(name,record.optInt("color",COLORS[items.size()%COLORS.length])));',
      'items.add(new Entry(name,record.optInt("color",COLORS[items.size()%COLORS.length]),record.optString("icon","folder")));',
      "migrate preexisting categories safely")
    registry=one(registry,
      '    public static synchronized boolean save(Context c,String previous,String desired,int color){',
      '''    public static synchronized String icon(Context c,String name){
        for(Entry e:all(c))if(e.name.equalsIgnoreCase(name))return e.icon;
        return "folder";
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color){
        return save(c,previous,desired,color,icon(c,previous));
    }
    public static synchronized boolean save(Context c,String previous,String desired,int color,String icon){''',
      "API for separately editable symbols")
    registry=one(registry,
      'entries.set(oldIndex,new Entry(name,color));',
      'entries.set(oldIndex,new Entry(name,color,icon));',
      "rename keeps symbol")
    registry=one(registry,
      'else entries.add(new Entry(name,color));',
      'else entries.add(new Entry(name,color,icon));',
      "new categories store symbol")
    # Preserve historical category name, task assignment, color and current selection.
    a=main.index("    void showCategoryEditor(String existing,java.util.function.Consumer<String> onSaved){")
    b=main.index("    String join(Collection<Integer> offsets)",a)
    main=main[:a]+'''    void showCategoryEditor(String existing,java.util.function.Consumer<String> onSaved){
        CategorySymbolChooser.show(this,existing,name->{
            if(existing!=null&&selectedCategory.equalsIgnoreCase(existing))selectedCategory=name;
            render();
            if(onSaved!=null)onSaved.accept(name);
        });
    }
'''+main[b:]
    main=one(main,
      'ModernGlyph.view(this,"folder",UiDesign.accentInk(entry.color),26)',
      'ApprovedPng.view(this,entry.icon,26)',
      "category manager pictograms")
    main=one(main,
      'ModernGlyph.view(this,"folder",UiDesign.accentInk(CategoryRegistry.color(this,task.category)),22)',
      'ApprovedPng.view(this,CategoryRegistry.icon(this,task.category),22)',
      "task detail pictograms")
    main=one(main,
      'UiDesign.icon(this,"folder",UiDesign.accentInk(categoryColor),17)',
      'ApprovedPng.view(this,CategoryRegistry.icon(this,category),17)',
      "task card pictograms")
    # User-created icon is shown on the category selection card and its modal.
    main=one(main,
      'ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,currentCategory),24);',
      'ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,currentCategory),24);',
      "category selection icon")
    main=one(main,
      'ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,selected),24);',
      'ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,selected),24);',
      "category selection callback")
    main=one(main,
      'ModernGlyph.button(categoryDisplay,"folder",CategoryRegistry.color(this,newName),24);',
      'ApprovedPng.button(categoryDisplay,CategoryRegistry.icon(this,newName),24);',
      "new category PNG")
    pickers=one(pickers,
      'card.addView(ModernGlyph.view(a,"folder",color,28),new LinearLayout.LayoutParams(dp(a,32),dp(a,32)));',
      'card.addView(ApprovedPng.view(a,CategoryRegistry.icon(a,chosen),28),new LinearLayout.LayoutParams(dp(a,32),dp(a,32)));',
      "category picker symbols")
    # Date and time selection avoids expensive recursive layout passes on every opening.
    pickers=one(pickers,
      '''            View root=result.getWindow().getDecorView();
            root.post(()->UiDesign.polishTree(root));''',
      '''            // Picker controls are pre-styled; re-walking the entire tree caused jank.''',
      "no redundant picker traversal")
    pickers=one(pickers,
      'minutes.setOnValueChangedListener((picker,oldValue,newValue)->{minute[0]=newValue;redraw[0].run();});',
      '''minutes.setOnValueChangedListener((picker,oldValue,newValue)->{
            minute[0]=newValue;
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));
        });''',
      "smooth minute input without rebuilding the clock dial")
    # Progressive, accessible repeat modal; every option maps to a real minute interval.
    old='''        Spinner repeat=new Spinner(this);String[] repetitions={"Solo en los avisos elegidos","Cada 30 minutos","Cada hora","Cada 3 horas","Cada 6 horas","Cada 12 horas","Cada día","Cada 2 días","Cada semana"};int[] intervals={0,30,60,180,360,720,1440,2880,10080};repeat.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,repetitions));int rv=draft!=null?draft.getInt("repeat"):t.repeatMinutes;for(int j=0;j<intervals.length;j++)if(intervals[j]==rv)repeat.setSelection(j);advanced.addView(repeat);'''
    new='''        int rv=draft!=null?draft.getInt("repeat"):t.repeatMinutes;
        final int[] repeatMinutes={rv};
        Button repeatButton=button(ModernRepeat.title(rv)+"  ›",()->{});
        ApprovedPng.button(repeatButton,"repeat",22);
        repeatButton.setOnClickListener(v->ModernRepeat.show(this,repeatMinutes[0],chosenValue->{
            repeatMinutes[0]=chosenValue;
            repeatButton.setText(ModernRepeat.title(chosenValue)+"  ›");
        }));
        advanced.addView(repeatButton);'''
    main=one(main,old,new,"modern recurrence selector")
    main=one(main,'b.putInt("repeat",intervals[repeat.getSelectedItemPosition()]);',
      'b.putInt("repeat",repeatMinutes[0]);',"persist repeat draft")
    main=one(main,'t.repeatMinutes=intervals[repeat.getSelectedItemPosition()];',
      't.repeatMinutes=repeatMinutes[0];',"save custom repeat interval")
    # The system PNG file/top-right plus, its 108dp layout and click stay identical.
    if plus!=next((x for x in main.splitlines() if 'setTag("new_task_button")' in x),None):
        raise RuntimeError("Approved top-right plus was changed")
    for cls in ("ApprovedPng","CategorySymbolChooser","ModernRepeat"):
        target=SRC/(cls+".java")
        if target.exists():raise RuntimeError("Refusing to overwrite "+str(target))
        target.write_text((STAGE/(cls+".java")).read_text(encoding="utf-8"),encoding="utf-8")
    for file,data in ((mainpath,main),(uipath,ui),(glyphpath,glyph),(pickerpath,pickers),
                     (registryfile,registry),(schedulefile,schedule)):
        file.write_text(data,encoding="utf-8")
    print(f"PASS phase27: {count} transparent PNG icons, separate category symbol and color, native pickers and repetition")

if __name__=="__main__":apply()
