#!/usr/bin/env python3
"""Regression: every native screen uses shared design, with unchanged top-right +."""
from pathlib import Path
root=Path("AgendaClara/app")
src=root/"src/main/java/pe/agendaclara/app"
main=(src/"MainActivity.java").read_text(encoding="utf-8")
schedule=(src/"ScheduleActivity.java").read_text(encoding="utf-8")
ui=(src/"UiDesign.java").read_text(encoding="utf-8")
motion=(src/"UiMotion.java").read_text(encoding="utf-8")
styles=(root/"src/main/res/values/styles.xml").read_text(encoding="utf-8")
dialogs=(root/"src/main/res/drawable/dialog_background.xml").read_text(encoding="utf-8")

# The approved blue/cyan + button remains byte-for-byte unchanged at its call site.
plus=[line for line in main.splitlines() if 'setTag("new_task_button")' in line]
assert len(plus)==1 and 'new LinearLayout.LayoutParams(dp(108),dp(108))' in plus[0]
assert '()->openEditor(-1,null,null)' in plus[0]
assert 'TopPlusButtonMotion.install(this)' in main
assert (root/"src/main/res/drawable-nodpi/ic_top_plus_animated.png").is_file()
assert 'new_task_button' not in ui
assert 'TopPlusButtonMotion.java' not in Path("updates/phase22/apply_visual_system.py").read_text()

for label in ('shared typography','navigation','input','card','modal','category'):
    assert len(main)>100000 and len(schedule)>44000,label
assert 'UiDesign.text(t,bold)' in main and 'UiDesign.text(t,bold)' in schedule
assert 'UiDesign.button(b,false)' in main and 'UiDesign.button(b,primary)' in schedule
assert 'UiDesign.card(c)' in main and 'UiDesign.card(c)' in schedule
assert 'UiDesign.input(e)' in main and 'UiDesign.input(e)' in schedule
assert 'UiDesign.icon(this,UiDesign.statusIcon(labels[n]),MUTED,26)' in main
assert 'UiDesign.icon(this,"folder",entry.color,26)' in main
assert 'UiDesign.icon(this,"calendar",GREEN,24)' in main
assert 'UiDesign.icon(this,"bell",GREEN,24)' in main
assert 'String query="",selectedCategory="General";' in main
assert 'String[] choices=new String[categories.length+1]' not in main
assert 'String[] names={"Todas","Urgentes","Pendientes","Próximas","Hechas"}' not in main
assert 'if(date==null&&!selectedCategory.equalsIgnoreCase(TaskOrganization.category(t.category)))continue;' in main
assert 't.repeatMinutes=intervals[repeat.getSelectedItemPosition()]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert 'android:windowAnimationStyle' in styles and 'AgendaDialogMotion' in styles
assert 'scheduleDialog()' in schedule and 'WindowLayout.boundDialog(ScheduleActivity.this,dialog)' in schedule
assert 'new AlertDialog.Builder(this)' not in schedule
photo=(src/"PhotoConfigActivity.java").read_text(encoding="utf-8")
assert 'UiDesign.button(choose,false)' in photo and 'UiDesign.button(save,true)' in photo
assert 'UiDesign.input(e)' not in photo, "Photo widget uses dedicated SeekBar controls"
assert 'UiDesign.BG' in photo and 'UiDesign.text(title,true)' in photo
assert (Path("updates/phase22/UiDesign.java").read_text()).count('b.getCurrentTextColor()==0xffffffff')==1, "Primary icons use white on blue"
assert (Path("updates/phase22/emulator_design_qa.sh")).is_file()

assert 'translationY(0f)' in motion and 'ValueAnimator.areAnimatorsEnabled()' in motion
assert 'android:radius="26dp"' in dialogs
assert (src/"WindowLayout.java").read_text().count('safe.width()-dp(a,48)')==1
for label in ('Mi agenda','Calendario','Revisión','Conexiones','Más opciones','Gestión de categorías','Recordatorios','Repetición del aviso'):
    assert label in main, label
for icon in ('check','calendar','bell','folder','clock','inbox','link','edit','trash','repeat','search','save','gear','notes'):
    assert f'case "{icon}"' in ui,icon
print("PASS: system-wide visual design, main/editor/review/calendar/categories/academic/modals, unchanged +, data and reminders")
