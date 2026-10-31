#!/usr/bin/env python3
"""Regression of the approved UI baseline, now backed by permanent PNG resources."""
from pathlib import Path
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(src/"MainActivity.java").read_text()
pickers=(src/"ModernPickers.java").read_text()
schedule=(src/"ScheduleActivity.java").read_text()
ui=(src/"UiDesign.java").read_text()
cat=(src/"CategoryRegistry.java").read_text()
assert 'ModernPickers.showDate(this,date[0]' in main
assert 'ModernPickers.showTime(this,time[0]' in main
assert 'new DatePickerDialog(this' not in main and 'new TimePickerDialog(this' not in main
assert 'categoryPicker.setVisibility(View.GONE)' in main
assert 'ModernPickers.showCategory(this' in main
assert 'PngIcons.button(dateBtn,"date"' in main and 'PngIcons.button(timeBtn,"time"' in main
assert 'PngIcons.button(b,name,accent,20)' in ui
assert 'PngIcons.view(this,CategoryRegistry.icon(this,entry.name),26)' in main
assert 'PngIcons.id(this,"back")' in schedule and 'PngIcons.id(this,"help")' in schedule
assert 'PngIcons.view(a,entry.icon,28)' in pickers
assert 'CategoryDesigner.show(this,existing,onSaved)' in main
assert 'boolean save(Context c,String previous,String desired,int color,String symbol)' in cat
assert 'FrameLayout dial=new FrameLayout(a)' in pickers
assert 'minutes.setMinValue(0);minutes.setMaxValue(59)' in pickers
assert 'private static ScrollView scroll' in pickers
assert 'month[0].lengthOfMonth()' in pickers
assert 'callback.accept(chosen[0])' in pickers
assert 'callback.accept(LocalTime.of(h,minute[0]))' in pickers
assert 'CategoryRegistry.all(a)' in pickers
assert 't.repeatMinutes=intervals[repeat.getSelectedItemPosition()]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert 't.calendarEnabled=google.isChecked()&&schedule.isChecked()' in main
assert '"Duración del evento"' not in main
assert 'selectedCategory="General"' in main
plus=[x for x in main.splitlines() if 'setTag("new_task_button")' in x]
assert len(plus)==1 and 'new LinearLayout.LayoutParams(dp(108),dp(108))' in plus[0]
assert 'TopPlusButtonMotion.install(this)' in main
assert (src/"TopPlusButtonMotion.java").exists()
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").exists()
print("PASS phase26 baseline upgraded to PNG icons and independent category symbols")
