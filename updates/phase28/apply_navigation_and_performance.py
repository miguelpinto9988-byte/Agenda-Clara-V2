#!/usr/bin/env python3
"""Phase28: restore the previously approved outline bottom navigation + safe UI tuning.

The bottom row alone returns to the earlier 3.8.2 outlined check/calendar/inbox/link
glyphs. Other approved PNG artwork, category symbols, colors, saved tasks, reminders,
and the original top-right plus button remain unchanged.

Performance changes avoid redundant main-thread work without changing state logic.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/java/pe/agendaclara/app"

def once(s,old,new,label):
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f"phase28 {label}: expected one anchor, got {count}")
    return s.replace(old,new,1)

def apply():
    main_path=ROOT/"MainActivity.java"
    ui_path=ROOT/"UiDesign.java"
    png_path=ROOT/"ApprovedPng.java"
    pick_path=ROOT/"ModernPickers.java"
    main=main_path.read_text(encoding="utf-8")
    ui=ui_path.read_text(encoding="utf-8")
    png=png_path.read_text(encoding="utf-8")
    pickers=pick_path.read_text(encoding="utf-8")

    original_plus=next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)
    if original_plus is None or "TopPlusButtonMotion.install(this)" not in main:
        raise RuntimeError("The already-approved header + must remain intact")

    # 1) Original 3.8.2 iconography on BOTTOM NAVIGATION ONLY.
    # UiDesign.icon() was globally changed to PNG in phase27; construct the old
    # OutlineIcon explicitly so the four nav controls are not affected.
    main=once(main,
        '''String[] iconTypes={"notes","date","check","backup"};
        ImageView icon=ModernGlyph.view(this,iconTypes[n],page==n?ModernGlyph.BLUE:ModernGlyph.CYAN,26);''',
        '''ImageView icon=new ImageView(this);
        icon.setImageDrawable(new UiDesign.OutlineIcon(
            UiDesign.statusIcon(labels[n]),page==n?GREEN:MUTED));
        icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
        icon.setPadding(dp(2),dp(2),dp(2),dp(2));''',
        "restore four original outline nav icons")
    main=once(main,
        '''String[] labels={"Agenda","Calendario","Revisar","Conexiones"};int[] icons={R.drawable.ic_nav_tasks,R.drawable.ic_nav_calendar,R.drawable.ic_nav_inbox,R.drawable.ic_nav_link};''',
        '''String[] labels={"Agenda","Calendario","Revisar","Conexiones"};''',
        "remove unused obsolete navigation resource array")

    # 2) Top-right + never changes; install its background/animation once when
    # the shell is constructed instead of scheduling two posts on every render.
    main=once(main,
        '        body.post(() -> TopPlusButtonMotion.install(this));\n',
        '',"avoid repeated plus installation traversal")
    main=once(main,
        'root.addView(nav);setContentView(root);WindowLayout.apply(this,root);',
        'root.addView(nav);setContentView(root);WindowLayout.apply(this,root);'
        'TopPlusButtonMotion.install(this);',
        "install approved plus once after shell creation")

    # 3) The nav views are persistent across renders; stop recursively
    # re-styling them every time tasks, calendar or chats refresh.
    main=once(main,
        '        UiDesign.polishTree(body);UiDesign.polishTree(nav);',
        '        UiDesign.polishTree(body);',
        "skip repeat bottom nav style walk")
    main=once(main,
        'nav.addView(item,new LinearLayout.LayoutParams(0,dp(76),1));}\n        View line=',
        'nav.addView(item,new LinearLayout.LayoutParams(0,dp(76),1));}'
        'UiDesign.polishTree(nav);\n        View line=',
        "polish persistent navigation just once")

    # 4) Reuse a stable Typeface rather than allocating a font on every label
    # of every screen redraw and dialog. The same bold style is retained.
    ui=once(ui,
        'public final class UiDesign {',
        '''public final class UiDesign {
    private static final Typeface SHARED_BOLD=Typeface.create("sans-serif",Typeface.BOLD);''',
        "single reusable bold font")
    ui=once(ui,
        't.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));',
        't.setTypeface(SHARED_BOLD);',
        "font used in normal text builder")
    ui=once(ui,
        'label.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));',
        'label.setTypeface(SHARED_BOLD);',
        "font used in global text pass")

    # 5) Resource-name lookup for a PNG is repeated on each icon. Cache only
    # the immutable Android drawable ID, not a Drawable/view; per-widget
    # drawables and independent pressed states stay untouched.
    png=once(png,
        'public final class ApprovedPng {\n    private ApprovedPng(){}',
        '''public final class ApprovedPng {
    private static final java.util.concurrent.ConcurrentHashMap<String,Integer> IDS=
        new java.util.concurrent.ConcurrentHashMap<>();
    private ApprovedPng(){}''',
        "resource lookup cache")
    png=once(png,
        '''        int id=c.getResources().getIdentifier(resource,"drawable",c.getPackageName());''',
        '''        int id=IDS.computeIfAbsent(resource,
            key->c.getResources().getIdentifier(key,"drawable",c.getPackageName()));''',
        "lookup each PNG only once")

    # 6) Day selection used to destroy/recreate the entire calendar grid
    # (35-42 TextViews) on every single tap. Only update the two affected
    # cells and the selected-date label instead, retaining redraw for months.
    pickers=once(pickers,
        '        final Runnable[] render={null};',
        '''        final java.util.Map<LocalDate,TextView> dayCells=new java.util.HashMap<>();
        final Runnable[] render={null};''',
        "reuse monthly calendar day views")
    pickers=once(pickers,
        'grid.removeAllViews();String[] weekdays=',
        'grid.removeAllViews();dayCells.clear();String[] weekdays=',
        "clear old month day references")
    pickers=once(pickers,
        '''                        cell.setContentDescription(selectedDate.format(DateTimeFormatter.ofPattern("EEEE d 'de' MMMM",ES)));
                        cell.setOnClickListener(v->{chosen[0]=selectedDate;render[0].run();});''',
        '''                        cell.setContentDescription(selectedDate.format(DateTimeFormatter.ofPattern("EEEE d 'de' MMMM",ES)));
                        dayCells.put(selectedDate,cell);
                        cell.setOnClickListener(v->{
                            if(selectedDate.equals(chosen[0]))return;
                            LocalDate previous=chosen[0];chosen[0]=selectedDate;
                            TextView oldCell=dayCells.get(previous);
                            if(oldCell!=null){
                                oldCell.setTextColor(INK);
                                oldCell.setBackground(previous.equals(LocalDate.now())
                                    ?ModernGlyph.rounded(a,0xffe8efff,UiDesign.BORDER,22)
                                    :null);
                            }
                            cell.setTextColor(0xffffffff);
                            cell.setBackground(ModernGlyph.rounded(a,BLUE,0,22));
                            chosenText.setText(chosen[0].format(
                                DateTimeFormatter.ofPattern("EEEE, d 'de' MMMM 'de' yyyy",ES)));
                        });''',
        "date selection updates cells instead of regenerating month")

    # 7) A click on the active page is handled without redundant rendering.
    # Existing tab navigation already checks page!=index: preserve it exactly.
    if 'if(page!=index)' not in main:raise RuntimeError("Tab route guard was lost")
    if not all(fragment in main for fragment in ('UiDesign.statusIcon(labels[n])','new UiDesign.OutlineIcon(')):
        raise RuntimeError("Original bottom-nav outlined glyphs not installed")
    if next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)!=original_plus:
        raise RuntimeError("The top-right plus was modified")
    for f,v in ((main_path,main),(ui_path,ui),(png_path,png),(pick_path,pickers)):
        f.write_text(v,encoding="utf-8")
    print("PASS phase28: prior outline bottom navigation restored; redundant UI work optimized; all user data and + kept")

if __name__=="__main__":
    apply()
