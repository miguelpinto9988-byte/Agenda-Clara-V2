#!/usr/bin/env python3
"""3.9.0: date-only sticky notes, two-action +, subtle non-nav icon scaling.

Apply exactly once after updates/phase18/apply_3_8_2.py. Each replacement is
anchored to the 3.8.2 generated Java sources. No task database migration, no
changes to the four previously approved bottom-nav icons or their labels.
"""
import base64
import io
from pathlib import Path
import zipfile

BASE=Path('AgendaClara/app/src/main')
SRC=BASE/'java/pe/agendaclara/app'
DRAW=BASE/'res/drawable-nodpi'
STAGE=Path(__file__).resolve().parent


def replace(value,old,new,description):
    count=value.count(old)
    if count!=1:
        raise RuntimeError(f'phase30 {description}: expected one anchor, found {count}')
    return value.replace(old,new,1)


def apply():
    paths={name:SRC/name for name in ('MainActivity.java','ModernPickers.java',
           'ApprovedPng.java','CategoryRegistry.java')}
    data={k:p.read_text(encoding='utf-8') for k,p in paths.items()}
    main=data['MainActivity.java']
    navbar=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
    assert 'new UiDesign.OutlineIcon(' in navbar
    assert 'dp(26),dp(26)' in navbar
    main=replace(main,'Button add=button("＋",()->openEditor(-1,null,null));',
                 'Button add=button("＋",()->showCreationMenu());',
                 'top + opens two floating choices')
    main=replace(main,'add.setContentDescription("Crear una tarea");header.addView(add,',
                 'add.setContentDescription("Crear una tarea o nota");header.addView(add,',
                 'accessible top + description')
    main=replace(main,'    void tasksPage(){',
                 '''    void showCreationMenu(){
        View add=root==null?null:root.findViewWithTag("new_task_button");
        CreationChoices.show(this,add,()->openEditor(-1,null,null),
            ()->StickyNotesUi.showEditor(this,null));
    }
    void tasksPage(){''',
                 'creation menu callback')
    main=replace(main,'taskList=column();body.addView(taskList);fillTasks(all,null);',
                 'taskList=column();body.addView(taskList);fillTasks(all,null);\n'
                 '        StickyNotesUi.agenda(this,body,selectedCategory,query);',
                 'sticky notes in active category')
    main=replace(main,'if(count==0){LinearLayout c=card(taskList);',
                 'if(count==0 && !(date==null && !StickyNotesStore.get(this).inCategory(selectedCategory).isEmpty())){LinearLayout c=card(taskList);',
                 'avoid misleading empty task notice over notes category')
    main=replace(main,'        int offset=month.getDayOfWeek().getValue()-1;',
                 '        java.util.Set<LocalDate> noteDays=StickyNotesStore.get(this).daysInMonth(\n'
                 '            java.time.YearMonth.from(month));\n'
                 '        int offset=month.getDayOfWeek().getValue()-1;',
                 'read note dates once per month for calendar markers')
    main=replace(main,'TextView d=text(n+(has?"\\n•":""),14,',
                 'TextView d=text(n+(has?"\\n•":noteDays.contains(date)?"\\n◦":""),14,',
                 'mark date with note when there is no task dot')
    main=replace(main,'d.setContentDescription(date.toString()+(has?", con tareas":""));',
                 'd.setContentDescription(date.toString()+(has?", con tareas":"")+\n'
                 '                (noteDays.contains(date)?", con notas adhesivas":""));',
                 'expose calendar note dates to accessibility')
    main=replace(main,'taskList=column();body.addView(taskList);fillTasks(all,selectedDay);',
                 'taskList=column();body.addView(taskList);fillTasks(all,selectedDay);\n'
                 '        StickyNotesUi.calendar(this,body,selectedDay);',
                 'sticky notes on selected calendar date')
    main=replace(main,'        UiDesign.polishTree(body);\n',
                 '        UiDesign.polishTree(body);ContentIconSizing.apply(body);\n',
                 'resize only page-content icons')
    main=replace(main,'v.post(()->UiDesign.polishTree(v));',
                 'v.post(()->{UiDesign.polishTree(v);ContentIconSizing.apply(v);});',
                 'resize modal icons after styling')
    # Note cards are retained when the user switches back from task modal; task
    # scheduling/completion and inbox code deliberately unchanged.
    if main[main.index('        nav=row();'):main.index('        View line=new View(this);')]!=navbar:
        raise RuntimeError('Bottom navigation visual layout was modified')
    data['MainActivity.java']=main

    png=data['ApprovedPng.java']
    png=replace(png,'        iv.setContentDescription(name);',
                '        iv.setContentDescription(name);iv.setTag("content_png_icon");',
                'tag approved non-nav PNG icons')
    png=replace(png,'        int size=UiDesign.dp(b.getContext(),iconDp);',
                '        int size=UiDesign.dp(b.getContext(),iconDp+4);',
                'subtly enlarge compound PNG buttons')
    png=replace(png,'b.setCompoundDrawablePadding(UiDesign.dp(b.getContext(),8));',
                'b.setCompoundDrawablePadding(UiDesign.dp(b.getContext(),10));',
                'preserve space between enlarged icon and button text')
    data['ApprovedPng.java']=png

    pick=data['ModernPickers.java']
    pick=replace(pick,
        '''    public static void showDate(Activity a,LocalDate initial,Consumer<LocalDate> callback){
        final LocalDate[] chosen={initial==null?LocalDate.now():initial};''',
        '''    public static void showDate(Activity a,LocalDate initial,Consumer<LocalDate> callback){
        showDate(a,initial,callback,"Elige la fecha límite de entrega");
    }
    /** Same approved calendar, with date-only wording for sticky notes. */
    public static void showDateForNote(Activity a,LocalDate initial,Consumer<LocalDate> callback){
        showDate(a,initial,callback,"Elige la fecha de tu nota adhesiva");
    }
    private static void showDate(Activity a,LocalDate initial,Consumer<LocalDate> callback,String hint){
        final LocalDate[] chosen={initial==null?LocalDate.now():initial};''',
        'reuse branded calendar with note-specific copy')
    pick=replace(pick,'content.addView(label(a,"Elige la fecha límite de entrega",13,MUTED));',
                 'content.addView(label(a,hint,13,MUTED));','date picker heading')
    data['ModernPickers.java']=pick

    categories=data['CategoryRegistry.java']
    categories=replace(categories,
        '            Store.get(c).reassignCategory(entries.get(oldIndex).name,name);',
        '            Store.get(c).reassignCategory(entries.get(oldIndex).name,name);\n'
        '            StickyNotesStore.get(c).reassignCategory(entries.get(oldIndex).name,name);',
        'renaming a category retains its sticky notes')
    categories=replace(categories,
        '            Store.get(c).reassignCategory(entries.get(i).name,"General");',
        '            Store.get(c).reassignCategory(entries.get(i).name,"General");\n'
        '            StickyNotesStore.get(c).reassignCategory(entries.get(i).name,"General");',
        'deleting a category retains sticky notes as General')
    data['CategoryRegistry.java']=categories

    icons=SRC/'CategorySymbolChooser.java'
    symbols=icons.read_text(encoding='utf-8')
    symbols=replace(symbols,
        '"finance","sport","leisure","food","family","other"};',
        '"finance","sport","leisure","food","family","other","sticky_note"};',
        'add sticky note PNG to category symbols')
    symbols=replace(symbols,
        '"Finanzas","Deporte","Ocio","Comida","Familia","Otro"};',
        '"Finanzas","Deporte","Ocio","Comida","Familia","Otro","Notas"};',
        'accessible new icon label')

    archive=base64.b64decode(''.join(p.read_text(encoding='ascii').strip() for p in sorted(STAGE.glob('sticky_assets.part*'))))
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        assets={name:z.read(name) for name in z.namelist()}
    for name,blob in assets.items():
        if '/' in name or not name.endswith('.png') or not blob.startswith(b'\x89PNG\r\n\x1a\n'):
            raise RuntimeError('Invalid note PNG asset '+name)
        if (DRAW/name).exists():
            raise RuntimeError('Refusing to overwrite existing Android drawable '+name)
    for cls in ('StickyNotesStore.java','StickyNotesUi.java','CreationChoices.java','ContentIconSizing.java'):
        if (SRC/cls).exists():raise RuntimeError('Note module already exists '+cls)
    grad=Path('AgendaClara/app/build.gradle')
    build=grad.read_text(encoding='utf-8')
    build=replace(build,"versionCode 30","versionCode 31",'new Android build code')
    build=replace(build,"versionName '3.8.2'","versionName '3.9.0'",'new Android version')
    for k,p in paths.items():p.write_text(data[k],encoding='utf-8')
    icons.write_text(symbols,encoding='utf-8')
    DRAW.mkdir(parents=True,exist_ok=True)
    for name,blob in assets.items():(DRAW/name).write_bytes(blob)
    for cls in ('StickyNotesStore.java','StickyNotesUi.java','CreationChoices.java','ContentIconSizing.java'):
        (SRC/cls).write_bytes((STAGE/cls).read_bytes())
    grad.write_text(build,encoding='utf-8')
    print('PASS phase30: sticky PNGs, date-only notes/category/color/editor, bold UI, floating +, navigation unchanged, version 3.9.0')

if __name__=='__main__':apply()
