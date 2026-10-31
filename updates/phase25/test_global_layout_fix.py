#!/usr/bin/env python3
"""Phase25 regression: bold typography across pages and untruncated dialog layouts."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
u=(p/"UiDesign.java").read_text(encoding="utf-8")
m=(p/"MainActivity.java").read_text(encoding="utf-8")
s=(p/"ScheduleActivity.java").read_text(encoding="utf-8")
w=(p/"WindowLayout.java").read_text(encoding="utf-8")
photo=(p/"PhotoConfigActivity.java").read_text(encoding="utf-8")
assert 't.setTypeface(Typeface.create("sans-serif",Typeface.BOLD))' in u
assert 'public static void polishTree(View root)' in u
assert 'if(root instanceof TextView && !"new_task_button".equals(root.getTag()))' in u
assert 'params.topMargin=minGap' in u
assert 'beforeInteractive&&(afterInteractive||afterText)' in u
assert 'getOrientation()==android.widget.LinearLayout.HORIZONTAL' in u, 'Adjacent horizontal buttons require gutters'
assert 'if(left&&params.leftMargin<gutter)' in u and 'if(right&&params.rightMargin<gutter)' in u
assert 'tabs.addView(b,new LinearLayout.LayoutParams(0,dp(64),1))' in m, 'Bold Connections tab titles must not clip'
assert 'UiDesign.polishTree(body);UiDesign.polishTree(nav);' in m
assert 'body.setPadding(dp(22),dp(18),dp(22),dp(40))' in m
assert 'c.setPadding(dp(20),dp(20),dp(20),dp(20))' in m
assert 'lp.bottomMargin=dp(20)' in m
assert 'contentScroll.setClipToPadding(true)' in m
assert 'contentScroll.setVerticalFadingEdgeEnabled(true)' in m
assert 'scroll.requestFocus();scroll.post(()->scroll.scrollTo(0,0));' in m
assert 'scroll.setDescendantFocusability(ViewGroup.FOCUS_BEFORE_DESCENDANTS)' in m
assert 'v.post(()->UiDesign.polishTree(v))' in m
assert 'WindowLayout.DialogScroll wrapper=new WindowLayout.DialogScroll(MainActivity.this)' in m
assert 'WindowLayout.DialogScroll wrapper=new WindowLayout.DialogScroll(ScheduleActivity.this)' in s
assert 'v.post(()->UiDesign.polishTree(v))' in s
assert 'root.post(()->UiDesign.polishTree(root))' in s
assert 'params.bottomMargin=dp(20)' in s
assert 'Math.max(8,height)' in s
assert 'setClipToPadding(true)' in w and 'setFocusableInTouchMode(true)' in w
assert 'setDescendantFocusability(FOCUS_BEFORE_DESCENDANTS)' in w
assert 'height()-dp(a,196)' in w
assert 'body.post(()->UiDesign.polishTree(body))' in photo

# All user-requested behavior and previous visual design must remain.
assert 'UiDesign.tintedBackground(this,entry.color,19,17)' in m
assert 'UiDesign.tintedBackground(this,categoryColor,20,14)' in m
assert 'UiDesign.categoryChip(chip,CategoryRegistry.color(this,label),active)' in m
assert 't.repeatMinutes=repeatMinutes[0]' in m
assert 'Reminders.schedule(this,t)' in m and 'Reminders.cancel(this,t.id)' in m
assert 'selectedCategory="General"' in m
assert '"Duración del evento"' not in m
approved=[line for line in m.splitlines() if 'setTag("new_task_button")' in line]
assert len(approved)==1 and 'new LinearLayout.LayoutParams(dp(108),dp(108))' in approved[0]
assert '()->openEditor(-1,null,null)' in approved[0]
assert 'TopPlusButtonMotion.install(this)' in m
assert (p/"TopPlusButtonMotion.java").is_file()
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").is_file()
print("PASS: global bold, all-screen gutters, keyboard-safe dialogs, + and task/alarms unchanged")
