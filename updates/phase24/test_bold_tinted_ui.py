#!/usr/bin/env python3
"""Regression checks for category-based colors and bolder UI presentation."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(p/"MainActivity.java").read_text(encoding="utf-8")
ui=(p/"UiDesign.java").read_text(encoding="utf-8")
schedule=(p/"ScheduleActivity.java").read_text(encoding="utf-8")
registry=(p/"CategoryRegistry.java").read_text(encoding="utf-8")

# Visual semantics: matching category color on the entire card, icon and label.
assert 't.setTypeface(Typeface.create("sans-serif",Typeface.BOLD))' in ui
assert 'b.setTypeface(Typeface.create("sans-serif",Typeface.BOLD))' in ui
assert "paint.setStrokeWidth(2.65f)" in ui
for visual in ("tintedBackground(", "accentInk(", "categoryChip(", "case \"folder\"", "case \"calendar\"", "case \"bell\""):
    assert visual in ui, visual
assert 'UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active)' in main
assert 'card.setBackground(UiDesign.tintedBackground(this,entry.color,19,17))' in main
assert 'card.setBackground(UiDesign.tintedBackground(this,categoryColor,20,14))' in main
assert 'UiDesign.icon(this,"folder",UiDesign.accentInk(categoryColor),17)' in main
assert 'pane.setBackground(UiDesign.tintedBackground(this,CategoryRegistry.color(this,task.category),20,11))' in main
assert 'categoryPicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener()' in main
assert 'colorIcon.setImageDrawable(new UiDesign.OutlineIcon("folder",UiDesign.accentInk(selected)))' in main
assert 'preview.setBackground(UiDesign.tintedBackground(MainActivity.this,selected,16,24))' in main
assert 'UiDesign.tintedBackground(this,s.color,20,16)' in schedule
assert 'UiDesign.tintedBackground(this,s.color,20,14)' in schedule
assert 'UiDesign.tintedBackground(this,primary.color,20,14)' in schedule

# No changes to user data, historical task colors, alarms or approved top-right +.
assert 'for(Entry e:all(c))if(e.name.equalsIgnoreCase(name))return e.color;' in registry
assert 'selectedCategory="General"' in main
assert 't.repeatMinutes=repeatMinutes[0]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert '"Duración del evento"' not in main
assert 'new LinearLayout.LayoutParams(dp(108),dp(108))' in main
assert 'setTag("new_task_button")' in main
assert 'TopPlusButtonMotion.install(this)' in main
assert "TopPlusButtonMotion.java" not in str(Path("updates/phase24"))
assert (p/"TopPlusButtonMotion.java").is_file()
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").is_file()
print("PASS phase24: readable category color fills, bold fonts/icons, school schedule and data preservation")
