#!/usr/bin/env python3
"""Structural regression for the 3.8.2 native redesign and safe category changes."""
from pathlib import Path
import importlib.util
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
java=(p/"MainActivity.java").read_text(encoding="utf-8")
org=(p/"TaskOrganization.java").read_text(encoding="utf-8")
store=(p/"Store.java").read_text(encoding="utf-8")
registry=(p/"CategoryRegistry.java").read_text(encoding="utf-8")
priority=(p/"TaskPriority.java").read_text(encoding="utf-8")
assert 'new LinearLayout.LayoutParams(dp(108),dp(108))' in java, "The + must be 2x 54dp"
assert 'setTag("new_task_button")' in java and '()->openEditor(-1,null,null)' in java
assert 'TopPlusButtonMotion.install(this)' in java
assert 'CategoryRegistry.names(this)' in java
assert 'this::showCategories' in java and 'showCategoryEditor(' in java
assert "TaskPriority.label(t,System.currentTimeMillis())" in java
assert 't.urgent=false;' in java and 'advanced.addView(urgent)' not in java
assert '"Hora límite · "' in java and '"Repetir el aviso"' in java
assert '"Cada día"' in java and '"Cada semana"' in java, "Original alarm recurrence must remain"
assert 't.repeatMinutes=intervals[repeat.getSelectedItemPosition()]' in java
assert 'Reminders.schedule(this,t)' in java and 'Reminders.cancel(this,t.id)' in java
assert 'new WindowLayout.DialogScroll(this)' in java, "Dialogs must scroll on small displays"
window=(p/"WindowLayout.java").read_text(encoding="utf-8")
assert "safe.width()-dp(a,48)" in window and "safe.height()-dp(a,56)" in window, "Modal safety insets"

assert 'lp.bottomMargin=dp(20)' in java and 'body.setPadding(dp(22),dp(18),dp(22),dp(40))' in java
assert "nav.addView(item,new LinearLayout.LayoutParams(0,dp(76),1))" in java, "Navigation labels must not be clipped"
assert 'lp.rightMargin=dp(8)' in java, "Category chips must have spacing"
assert 'String[] names={"Todas","Urgentes","Pendientes","Próximas","Hechas"}' not in java, "Legacy status row must not render"
assert 'HorizontalScrollView horizontal=new HorizontalScrollView(this)' not in java, "Legacy status scroller must be removed"
assert 'String[] choices=new String[categories.length+1]' not in java, "Duplicate Todas category must not render"
assert 'Button create=button("＋ Nueva"' not in java, "Keep category creation in the manager only"
assert 'for(String label:categories)' in java, "Only persisted categories become chips"
assert 'String query="",selectedCategory="General";' in java, "General must be selected by default"
assert 'selectedCategory=state.getString("selected_category","General")' in java, "Restore General safely"
assert 'if(selectedCategory.equalsIgnoreCase(entry.name))selectedCategory="General";' in java, "Deleted active category falls back"
assert 'if(!AgendaFilters.matches(t,0,0,query,date,now))continue;' in java, "No hidden status filters"
assert 'if(date==null&&!selectedCategory.equalsIgnoreCase(TaskOrganization.category(t.category)))continue;' in java, "Categories still actually filter tasks"
assert '"No hay tareas en "+selectedCategory' in java, "Category empty state should be clear"
assert "Avance estimado =" not in java, "Avoid redundant lengthy formula in the header"
assert 'ComposeDayActivity' not in java and not (p/"ComposeDayActivity.kt").exists()
assert 'getWritableDatabase().update("tasks",values,"category=? COLLATE NOCASE"' in store
assert 'if(oldIndex==0)return false' in registry, "General cannot be renamed"
assert 'for(int i=1;i<entries.size();i++)' in registry, "General cannot be deleted"
assert 'if(!prefs.contains(KEY))' not in registry or "migration" in registry
assert 'for(Task task:Store.get(context).all())' in registry, "Existing categories must be migrated"
assert 'items.add(new Entry("General",COLORS[0]))' in registry
assert 'return custom.isEmpty()?"General"' in org, "Custom names cannot be erased"
for text in ('"Urgente"','"Alta"','"Media"','"Baja"','"Vencida"','"Sin fecha"'):
    assert text in priority,text
print("PASS: General-only initial chip, no status filters or duplicate Todos, category filtering and data preservation")
