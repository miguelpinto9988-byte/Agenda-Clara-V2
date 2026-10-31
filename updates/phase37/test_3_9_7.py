#!/usr/bin/env python3
"""Verify independent day editor, 12-hour inputs, AM/PM, persistence and color preservation."""
from pathlib import Path
S=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
code=(S/'ScheduleActivity.java').read_text(encoding='utf-8')
clock=(S/'ScheduleDayClock.java').read_text(encoding='utf-8')
gradle=Path('AgendaClara/app/build.gradle').read_text(encoding='utf-8')
assert 'Días y horarios' in code
assert 'Cada día de este curso puede tener una hora distinta' in code
assert 'new TreeMap<>()' in code
assert 'ScheduleCourseColors.same(current.course,existing.course)' in code
assert 'sessions.put(current.day,new ScheduleDayClock.Slot(current.day,current.start,current.end,current.id))' in code
assert 'final Runnable[] redraw' in code
assert 'Agregar otro día' in code
assert 'scheduleDialog().setTitle("Agregar día al curso")' in code
assert 'timeChoice(slot,true,redraw[0])' in code and 'timeChoice(slot,false,redraw[0])' in code
assert 'ScheduleDayClock.clock12(clock)' in code
assert 'TimePickerDialog(this,(dialog,h,m)->' in code
assert 'initial/60,initial%60,false).show()' in code
assert 'ScheduleDayClock.withMeridiem(prev,pm)' in code
assert 'txt(pm?"PM":"AM"' in code
assert 'slot.start=h*60+m' in code and 'slot.end=h*60+m' in code
assert 's.start=slot.start;s.end=slot.end;' in code
assert 's.id=slot.id;s.day=slot.day' in code
assert 'if(!ScheduleDayClock.validInterval(slot.start,slot.end))' in code
assert 'if(db.save(s))ScheduleReminders.schedule(this,s)' in code
assert 'ScheduleReminders.cancel(this,id);db.delete(id);' in code
assert 'setTitle("Quitar días del curso")' in code
assert 'ScheduleConflict.describe(additions,others)' in code
assert 'detected.candidates.add(' in code
assert 'Math.min(index,chosen.size())' in code
assert 'new TimePickerDialog(this' in code and 'TimePickerDialog(this,(p,h,m)->destination' not in code
assert 'private void colorCatalog(' in code and 'private void colorMixer(' in code
assert '72 tonos rápidos + 360 tonos en catálogo' in code
assert 'Explorar 360 colores · Pasteles, vivos, profundos y suaves' in code
assert 'El mismo curso conservará este color en todos sus días.' in code
assert 'btn("Más colores · Mezclador HSV"' in code
assert 'timeControl' not in code or 'timeChoice' in code
assert 'versionCode 38' in gradle and "versionName '3.9.7'" in gradle
assert 'toMinutes(int hour,int minute,boolean pm)' in clock
assert 'hour%12' in clock and 'pm?12:0' in clock
assert 'isPm(int minutes)' in clock
assert 'validInterval(int start,int end)' in clock
assert 'sideBySide=' in code and 'scale<=1.15f' in code
assert 'setSingleLine(true)' in code and 'dp(44)' in code
# These lines are the agreed navigation icons elsewhere in the app.
main=(S/'MainActivity.java').read_text(encoding='utf-8')
nav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
print('PASS phase37: independent 12h day/week editor, AM/PM, safe saves, existing color UI, bottom navigation untouched')
