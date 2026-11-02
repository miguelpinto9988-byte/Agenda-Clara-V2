#!/usr/bin/env python3
"""Static regression guards for 3.10.9; JVM transitions tested independently."""
from pathlib import Path
r=Path('AgendaClara');java=r/'app/src/main/java/pe/agendaclara/app'
main=(java/'MainActivity.java').read_text(encoding='utf-8')
window=(java/'WindowLayout.java').read_text(encoding='utf-8')
policy=(java/'DialogResizePolicy.java').read_text(encoding='utf-8')
calendar=main[main.index('    void calendarPage(){'):main.index('    void addCell(',main.index('    void calendarPage(){'))]
assert 'Mi semana' not in calendar and 'WeeklyPlanner.pendingByDay' not in calendar
for expected in ('CalendarVisuals.month(this,body,all)','CalendarVisuals.selectedDate(this,body,all)',
        'StickyNotesUi.calendar(this,body,selectedDay)','LinearLayout schedule=card(body)',
        'Abrir mi horario'):
    assert expected in calendar,expected
assert 'DialogResizePolicy.height(' in window
assert 'keyboardClosed=previousIme[0]==1&&!ime' in window
assert 'getRootWindowInsets()' in window
assert 'available(a,this).height()' in window
assert 'available(a,a.getWindow().getDecorView())' not in window
assert 'maximum>priorMaximum||keyboardClosed' in policy
assert "versionCode 50" in (r/'app/build.gradle').read_text()
assert "versionName '3.10.9'" in (r/'app/build.gradle').read_text()
print('PASS: calendar-only removal, shared keyboard-restore policy, signed version 3.10.9 targets')
