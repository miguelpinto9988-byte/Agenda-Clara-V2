#!/usr/bin/env python3
from pathlib import Path
import struct
r=Path("AgendaClara")
j=(r/"app/src/main/java/pe/agendaclara/app/MainActivity.java").read_text()
ui=(r/"app/src/main/java/pe/agendaclara/app/CalendarVisuals.java").read_text()
sum_code=(r/"app/src/main/java/pe/agendaclara/app/CalendarDaySummary.java").read_text()
grad=(r/"app/build.gradle").read_text()
assert "CalendarVisuals.month(this,body,all)" in j
assert "CalendarVisuals.selectedDate(this,body,all)" in j
assert "StickyNotesUi.calendar(this,body,selectedDay)" in j
assert "if((kind&CalendarDaySummary.TASK)!=0)" in ui
assert "if((kind&CalendarDaySummary.NOTE)!=0)" in ui
assert 'if("calendar_both".equals(icon))' in ui
assert 'calendar-day-' in ui and 'setContentDescription(' in ui
assert 'YearMonth.from(day).equals(month)' in sum_code
assert "versionCode 48" in grad and "versionName '3.10.7'" in grad
for name in ("task","note"):
    png=(r/"app/src/main/res/drawable-nodpi"/f"ic_ref_calendar_{name}.png").read_bytes()
    assert png[:8]==b"\x89PNG\r\n\x1a\n"
    width,height=struct.unpack(">II",png[16:24])
    assert 128<=width<=256 and 128<=height<=256 and png[25]==6
print("PASS: dual calendar indicators and original transparent RGBA PNG resources")
