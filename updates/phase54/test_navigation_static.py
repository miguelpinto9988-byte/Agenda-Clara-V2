#!/usr/bin/env python3
"""Static navigation tests; deliberately do not compile or start the emulator."""
from pathlib import Path

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main = (CODE / "MainActivity.java").read_text(encoding="utf-8")
ui = (CODE / "UiDesign.java").read_text(encoding="utf-8")
nav = (CODE / "MiDiaNavigation.java").read_text(encoding="utf-8")
study = (CODE / "MiDiaStudyPage.java").read_text(encoding="utf-8")
more = (CODE / "MiDiaMorePage.java").read_text(encoding="utf-8")

assert 'TAB_LABELS = {"Inicio", "Tareas", "Estudio", "Calendario", "Más"}' in nav
assert "MiDiaNavigation.selectedTab(this)" in main
assert "MiDiaNavigation.open(this,index)" in main
assert "new LinearLayout.LayoutParams(0,dp(67),1)" in main
assert "homeSection=Math.max(0,Math.min(2," in main
assert 'out.putInt("mi_dia_home_section",homeSection)' in main
assert "page=Math.max(0,Math.min(4" in main
assert "if(homeSection==1){" in main and "tasksPage();" in main
assert "MiDiaStudyPage.render(this)" in main
assert "MiDiaMorePage.render(this)" in main
assert "else if(page==1)calendarPage()" in main
assert "else if(page==2)messagesPage()" in main
assert "else settingsPage()" in main
assert 'case "Inicio":return "home";' in ui
assert 'case "Tareas":case "Agenda":return "check";' in ui
assert 'case "Estudio":return "graduation";' in ui
assert 'case "Más":return "grid";' in ui
for method in ("void tasksPage()", "void calendarPage()", "void messagesPage()",
               "void settingsPage()", "void showCreationMenu()", "void taskCard(",
               "void showTaskDetails(", "void chooseCalendar()"):
    assert method in main, "Lost legacy functionality: " + method
assert 'page=0;homeSection=1;dashboardAllTasksExpanded=true;selectedCategory="Notas";render();' in main
for preserved in ("WhatsApp", "StickyNotesUi.showEditor", "VoiceQuickTask.show",
                  "ScheduleActivity", "Calendar"):
    assert preserved in (more + study)
assert "Store.get(a).all()" in study
assert "MiDiaDayMetrics.isStudy(task)" in study
assert "originalPage(a, 2, 0)" in more
assert "originalPage(a, 3, 0)" in more
assert "originalPage(a, 3, 1)" in more
assert "originalPage(a, 3, 2)" in more
assert "MiDiaNavigation.open(a, 1)" in more
print("PASS phase7: five tabs, academic filter, original routes and data flows preserved")
