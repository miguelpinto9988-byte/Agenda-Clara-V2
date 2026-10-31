#!/usr/bin/env python3
"""Regression checks for the task editor after removing duration input."""
from pathlib import Path
SRC=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
java=(SRC/"MainActivity.java").read_text(encoding="utf-8")
task=(SRC/"Task.java").read_text(encoding="utf-8")
calendar=(SRC/"CalendarBridge.java").read_text(encoding="utf-8")
store=(SRC/"Store.java").read_text(encoding="utf-8")
for removed in (
    'Duración del evento', 'Duración en minutos', 'advanced.addView(duration)',
    'duration.getText()', 'duration.setError(', 't.duration=minutes',
    'b.putInt("duration"',
):
    assert removed not in java, f"Old duration form remains: {removed}"
for preserved in (
    'TopPlusButtonMotion.install(this)',
    'setTag("new_task_button")',
    'new LinearLayout.LayoutParams(dp(108),dp(108))',
    '"Hora límite · "',
    'Repetir el aviso',
    't.repeatMinutes=repeatMinutes[0]',
    'Reminders.schedule(this,t)',
    'Reminders.cancel(this,t.id)',
    't.calendarEnabled=google.isChecked()&&schedule.isChecked()',
    'CategoryRegistry.names(this)',
    'selectedCategory="General"',
):
    assert preserved in java, f"Existing behavior was lost: {preserved}"
assert "public int duration=60" in task, "New calendar events require a safe internal default"
assert "t.due+t.duration*60000L" in calendar, "Previously saved calendar duration must still work"
assert 'v.put("duration",t.duration)' in store, "Preserve existing persisted task durations"
assert 't.duration=c.getInt(c.getColumnIndexOrThrow("duration"))' in store
print("PASS phase23: duration UI absent; calendar default, old task data, plus, deadline and reminder rules preserved")
