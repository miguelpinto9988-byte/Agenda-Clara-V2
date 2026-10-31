#!/usr/bin/env python3
"""Phase26 regression: approved art installed, existing data handlers untouched."""
from pathlib import Path
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(src/"MainActivity.java").read_text(encoding="utf-8")
glyph=(src/"ModernGlyph.java").read_text(encoding="utf-8")
pickers=(src/"ModernPickers.java").read_text(encoding="utf-8")
ui=(src/"UiDesign.java").read_text(encoding="utf-8")
schedule=(src/"ScheduleActivity.java").read_text(encoding="utf-8")
assert "ModernPickers.showDate(this,date[0]" in main
assert "ModernPickers.showTime(this,time[0]" in main
assert "new DatePickerDialog(this" not in main
assert "new TimePickerDialog(this" not in main
assert "categoryPicker.setVisibility(View.GONE)" in main
assert "ModernPickers.showCategory(this" in main
assert 'if(button.getContentDescription()==null)button.setContentDescription(button.getText());' in glyph, "Never overwrite custom accessibility labels"
assert "categoryDisplay.setText(newName" in main
assert "LinearLayout palette=column();LinearLayout paletteRow=null;" in main and "colors.setVisibility(View.GONE)" in main
assert "CategoryRegistry.COLORS.length" in main
assert "colors.setSelection(index)" in main
assert "CategoryRegistry.save(this,existing,desired,CategoryRegistry.COLORS[colors.getSelectedItemPosition()])" in main
assert 'ModernGlyph.button(dateBtn,"date"' in main
assert 'ModernGlyph.button(timeBtn,"time"' in main
assert 'new String[]{"whatsapp","google-calendar","widgets"}' in main
assert "ModernGlyph.button(b,name,accent,20)" in ui
assert 'ModernGlyph.view(this,"folder"' in main
assert "new ModernGlyph(\"back\"" in schedule and "new ModernGlyph(\"help\"" in schedule
for key in ("folder","date","clock","bell","repeat","notes","whatsapp","google-calendar","backup","widgets","settings","photo","manual","help","back"):
    assert f'case "{key}"' in glyph,key
assert "FrameLayout dial=new FrameLayout(a)" in pickers
assert "minutes.setMinValue(0);minutes.setMaxValue(59)" in pickers
assert "private static ScrollView scroll" in pickers and "WindowLayout.boundDialog(a,result)" in pickers
assert "month[0].lengthOfMonth()" in pickers
assert "n>=1&&n<=days" in pickers and "week.addView(cell,lp)" in pickers
assert 'callback.accept(chosen[0])' in pickers
assert 'callback.accept(LocalTime.of(h,minute[0]))' in pickers
assert "CategoryRegistry.all(a)" in pickers
assert 't.repeatMinutes=repeatMinutes[0]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert 't.calendarEnabled=google.isChecked()&&schedule.isChecked()' in main
assert '"Duración del evento"' not in main
assert 'selectedCategory="General"' in main
plus=[x for x in main.splitlines() if 'setTag("new_task_button")' in x]
assert len(plus)==1 and "new LinearLayout.LayoutParams(dp(108),dp(108))" in plus[0]
assert "TopPlusButtonMotion.install(this)" in main
assert (src/"TopPlusButtonMotion.java").exists()
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").exists()
print("PASS phase26: modern pickers, persistent multicolor icons, callbacks, data and existing plus preserved")
