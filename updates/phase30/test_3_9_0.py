#!/usr/bin/env python3
"""Source and resource regression tests for separate dated sticky notes and + menu."""
from pathlib import Path
import struct
src=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
draw=Path('AgendaClara/app/src/main/res/drawable-nodpi')
main=(src/'MainActivity.java').read_text(encoding='utf-8')
store=(src/'StickyNotesStore.java').read_text(encoding='utf-8')
ui=(src/'StickyNotesUi.java').read_text(encoding='utf-8')
menu=(src/'CreationChoices.java').read_text(encoding='utf-8')
category=(src/'CategoryRegistry.java').read_text(encoding='utf-8')
png=(src/'ApprovedPng.java').read_text(encoding='utf-8')
picker=(src/'ModernPickers.java').read_text(encoding='utf-8')
resize=(src/'ContentIconSizing.java').read_text(encoding='utf-8')
nav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
assert nav.count('new UiDesign.OutlineIcon(')==1
assert 'dp(26),dp(26)' in nav and 'UiDesign.polishTree(nav);' in nav
assert 'ContentIconSizing.apply(nav)' not in main
assert 'showCreationMenu()' in main and 'CreationChoices.show(this,add,' in main
assert '()->openEditor(-1,null,null)' in main and 'StickyNotesUi.showEditor(this,null)' in main
assert 'PopupWindow menu' in menu and 'Nueva tarea' in menu and 'Nueva nota' in menu
assert 'ValueAnimator.areAnimatorsEnabled()' in menu
assert 'content_png_icon' in png and 'iconDp+4' in png
assert 'rightMargin+=6*dp' in resize and 'apply(body);' in main
assert 'sticky_notes' in store and 'agenda-sticky-notes.db' in store
assert 'day TEXT NOT NULL' in store and 'CREATE INDEX sticky_notes_day_idx' in store
assert 'public synchronized void delete(long id)' in store
assert 'LocalDate.parse(' in store and 'void reassignCategory(' in store
assert 'daysInMonth(' in store and 'java.util.Set<LocalDate> noteDays=' in main
for absent in ('repeatMinutes','Reminders.schedule','public boolean done','public boolean urgent'):
    assert absent not in store, absent
assert 'StickyNotesStore.get(c).reassignCategory(' in category
assert 'StickyNotesUi.agenda(this,body,selectedCategory,query)' in main
assert 'StickyNotesUi.calendar(this,body,selectedDay)' in main
assert 'showDateForNote' in picker and 'Elige la fecha de tu nota adhesiva' in picker
assert 'FrameLayout preview' in ui and 'refreshPreview[0].run()' in ui
assert 'android.text.TextUtils.TruncateAt.END' in ui
assert 'UiDesign.text(' in ui or 'a.text(' in ui
assert '"Notas"' in ui and 'COLORS.length' in ui
assert 'new ImageView(a)' in ui and 'ImageView.ScaleType.FIT_XY' in ui
assert 'Guardar' in ui and 'Eliminar' in ui
assert 'button("＋  Nueva categoría"' in ui
for name in ['yellow','pink','blue','green','purple','peach']:
    p=draw/f'sticky_{name}.png'; b=p.read_bytes()
    assert b.startswith(b'\x89PNG\r\n\x1a\n')
    width,height=struct.unpack('>II',b[16:24]);assert width>=300 and height>=250
assert (draw/'ic_ref_sticky_note.png').read_bytes().startswith(b'\x89PNG')
assert '"sticky_note"' in (src/'CategorySymbolChooser.java').read_text(encoding='utf-8')
gradle=Path('AgendaClara/app/build.gradle').read_text(encoding='utf-8')
assert 'versionCode 31' in gradle and "versionName '3.9.0'" in gradle
print('PASS 3.9.0: bold live PNG preview, standalone date-only notes, categories/colors, original nav unchanged')
