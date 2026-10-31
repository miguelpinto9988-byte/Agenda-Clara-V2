#!/usr/bin/env python3
"""Phase28 compatibility/performance regressions for Agenda Clara 3.8.2."""
from pathlib import Path
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(src/"MainActivity.java").read_text(encoding="utf-8")
ui=(src/"UiDesign.java").read_text(encoding="utf-8")
png=(src/"ApprovedPng.java").read_text(encoding="utf-8")
pickers=(src/"ModernPickers.java").read_text(encoding="utf-8")
registry=(src/"CategoryRegistry.java").read_text(encoding="utf-8")
# Four nav icons use the ORIGINAL check/calendar/inbox/link outline renderers.
assert 'String[] labels={"Agenda","Calendario","Revisar","Conexiones"};' in main
assert 'new UiDesign.OutlineIcon(' in main
assert 'UiDesign.statusIcon(labels[n]),page==n?GREEN:MUTED' in main
assert 'String[] iconTypes={"notes","date","check","backup"}' not in main
nav=main[main.index('    void createShell(){'):main.index('    void tasksPage(){')]
assert nav.count('new UiDesign.OutlineIcon(')==1
assert 'ModernGlyph.view(this,iconTypes[n]' not in nav
assert 'item.setContentDescription(labels[n])' in nav
assert 'item.setOnClickListener(v->{if(page!=index)' in nav
assert '((ImageView)item.getChildAt(0)).setImageTintList(' in main
for label,name in (("Agenda","check"),("Calendario","calendar"),("Revisar","inbox"),("Conexiones","link")):
    assert f'case "{name}":' in ui
    assert f'case "{label}":return "{name}";' in ui
assert 'paint.setStrokeWidth(2.65f)' in ui
# PNG in other areas remains intentionally unchanged.
assert 'ApprovedPng.view(context,name,sizeDp)' in (src/"ModernGlyph.java").read_text()
assert 'ApprovedPng.view(a,CategoryRegistry.icon(a,chosen),28)' in pickers
assert 'CategorySymbolChooser.show(this,existing,name->' in main
assert 'ApprovedPng.button(b,name,accent,20)' not in ui  # delegated to ModernGlyph for non-nav actions
assert (src/"CategorySymbolChooser.java").is_file()
assert (src/"ModernRepeat.java").is_file()
assert len(list(Path("AgendaClara/app/src/main/res/drawable-nodpi").glob("ic_ref_*.png")))>=35
# Cut redundant main-thread work and keep lifecycle safety.
assert 'TopPlusButtonMotion.install(this);' in main
assert main.count('TopPlusButtonMotion.install(this)')==1
assert 'body.post(() -> TopPlusButtonMotion.install(this));' not in main
assert main.count('UiDesign.polishTree(nav);')==1
assert 'UiDesign.polishTree(body);' in main
assert 'UiDesign.polishTree(body);UiDesign.polishTree(nav);' not in main
assert 'private static final Typeface SHARED_BOLD=' in ui
assert 'label.setTypeface(SHARED_BOLD)' in ui
assert 't.setTypeface(SHARED_BOLD)' in ui
assert 'ConcurrentHashMap<String,Integer> IDS' in png
assert 'IDS.computeIfAbsent(resource,' in png
assert 'getDrawable(id)' in png and 'return d.mutate()' in png
assert 'new java.util.HashMap<>()' in pickers
assert 'dayCells.put(selectedDate,cell)' in pickers
assert 'LocalDate previous=chosen[0];chosen[0]=selectedDate' in pickers
assert 'cell.setOnClickListener(v->{chosen[0]=selectedDate;render[0].run();});' not in pickers
assert 'month[0].plusMonths(1);render[0].run();' in pickers
# Core behavior, data model and original top + are byte-stable.
plus=[line for line in main.splitlines() if 'setTag("new_task_button")' in line]
assert len(plus)==1
assert 'new LinearLayout.LayoutParams(dp(108),dp(108))' in plus[0]
assert '()->openEditor(-1,null,null)' in plus[0]
assert (src/"TopPlusButtonMotion.java").exists()
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").exists()
assert 't.repeatMinutes=repeatMinutes[0]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert 'selectedCategory="General"' in main
assert 'public final String icon;' in registry and 'object.put("icon",e.icon)' in registry
assert '"Duración del evento"' not in main
print("PASS phase28: original nav outlines, maintained PNGs and all task/reminder data, cached resources, faster UI")
