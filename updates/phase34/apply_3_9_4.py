#!/usr/bin/env python3
"""3.9.4: preserve title/date in compact widget and larger-font note preview."""
from pathlib import Path
S=Path("AgendaClara/app/src/main");J=S/"java/pe/agendaclara/app"
P=Path(__file__).resolve().parent
def change(src,old,new,label):
    if src.count(old)!=1:raise RuntimeError(f"phase34 {label}: expected unique anchor, found {src.count(old)}")
    return src.replace(old,new)
def run():
    u=(J/"StickyNotesUi.java").read_text()
    w=(J/"StickyNotesWidget.java").read_text()
    s=(J/"StickyNotesWidgetService.java").read_text()
    g=Path("AgendaClara/app/build.gradle").read_text()
    u=change(u,"    private static void ensureDefaultCategory(MainActivity a){",
      """    private static int noteHeight(MainActivity a,boolean large){
        float fontScale=a.getResources().getConfiguration().fontScale;
        float extra=Math.max(0f,Math.min(2f,fontScale)-1f);
        return dp(a,(large?235:185)+Math.round(extra*(large?125:100)));
    }
    private static void ensureDefaultCategory(MainActivity a){""","card scale helper")
    u=change(u,"frame.setMinimumHeight(dp(a,large?235:185));","frame.setMinimumHeight(noteHeight(a,large));","card min height")
    u=change(u,"LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,185));",
        "LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,noteHeight(a,false));","list height")
    u=change(u,"form.addView(preview,new LinearLayout.LayoutParams(-1,dp(a,238)));",
        "form.addView(preview,new LinearLayout.LayoutParams(-1,noteHeight(a,true)+dp(a,3)));","editor preview height")
    w=change(w,"""    public static RemoteViews row(Context c,StickyNotesStore.Note note){
        RemoteViews view=new RemoteViews(c.getPackageName(),R.layout.widget_sticky_row);""",
        """    public static RemoteViews row(Context c,StickyNotesStore.Note note){
        return row(c,note,false);
    }
    public static RemoteViews row(Context c,StickyNotesStore.Note note,boolean compact){
        RemoteViews view=new RemoteViews(c.getPackageName(),
            compact?R.layout.widget_sticky_row_compact:R.layout.widget_sticky_row);""","widget compact row")
    w=change(w,"""        int width=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,250);
        boolean compact=width>0&&width<220;""",
        """        int width=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,250);
        int height=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,160);
        float scale=context.getResources().getConfiguration().fontScale;
        boolean compact=(width>0&&width<235)||(height>0&&height<170)||scale>=1.3f;
        view=new RemoteViews(context.getPackageName(),
            compact?R.layout.widget_sticky_notes_compact:R.layout.widget_sticky_notes);""","widget options")
    w=change(w,"for(StickyNotesStore.Note note:notes)items.addItem(note.id,row(context,note));",
        "for(StickyNotesStore.Note note:notes)items.addItem(note.id,row(context,note,compact));","modern collection")
    w=change(w,"""                    .setData(Uri.parse("agenda://sticky/service/"+widgetId));""",
        """                    .putExtra("sticky_compact",compact)
                    .setData(Uri.parse("agenda://sticky/service/"+widgetId+"/"+(compact?1:0)));""","legacy adapter refresh")
    s=change(s,"return new Factory(getApplicationContext());",
        'return new Factory(getApplicationContext(),intent.getBooleanExtra("sticky_compact",false));',"service factory")
    s=change(s,"""        private final Context context;
        private List<StickyNotesStore.Note> notes=new ArrayList<>();
        Factory(Context context){this.context=context;}""",
        """        private final Context context;
        private final boolean compact;
        private List<StickyNotesStore.Note> notes=new ArrayList<>();
        Factory(Context context,boolean compact){this.context=context;this.compact=compact;}""","service mode")
    s=change(s,"?StickyNotesWidget.row(context,notes.get(position)):null;",
        "?StickyNotesWidget.row(context,notes.get(position),compact):null;","service rows")
    g=change(g,"versionCode 34","versionCode 35","versionCode")
    g=change(g,"versionName '3.9.3'","versionName '3.9.4'","versionName")
    new={"widget_sticky_row_compact.xml":S/"res/layout/widget_sticky_row_compact.xml",
         "widget_sticky_notes_compact.xml":S/"res/layout/widget_sticky_notes_compact.xml"}
    for name,dest in new.items():
        if dest.exists():raise RuntimeError("Refuse to overwrite existing "+name)
        if not (P/name).is_file():raise RuntimeError("Missing template "+name)
    for file,src in (("StickyNotesUi.java",u),("StickyNotesWidget.java",w),
                     ("StickyNotesWidgetService.java",s)):(J/file).write_text(src)
    Path("AgendaClara/app/build.gradle").write_text(g)
    for name,dest in new.items():dest.write_bytes((P/name).read_bytes())
    print("PASS phase34 responsive sticky notes and compact bold widget")
if __name__=="__main__":run()
