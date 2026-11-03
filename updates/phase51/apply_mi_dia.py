#!/usr/bin/env python3
"""Phase 4: integrate native 'Inicio — Mi día' into reconstructed 3.11.3.

Only MainActivity's home rendering and navigation label are modified.
The original tasksPage, calendar, WhatsApp, voice, widgets and settings remain.
Run after phase50 and phase51/stage_text_resources.py.
"""
from pathlib import Path
import shutil

ROOT = Path("AgendaClara/app/src/main")
CODE = ROOT / "java/pe/agendaclara/app"
HERE = Path(__file__).resolve().parent

def replace_one(source, old, new, label):
    if new in source and old not in source:
        return source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)

def run():
    main_file = CODE / "MainActivity.java"
    ui_file = CODE / "UiDesign.java"
    if not main_file.exists() or not ui_file.exists():
        raise RuntimeError("Reconstruct Android sources and apply phase50 first")
    dashboard = (HERE / "MiDiaDashboard.java").read_text(encoding="utf-8")
    if "package pe.agendaclara.app;" not in dashboard:
        raise RuntimeError("Unexpected dashboard package")
    main = main_file.read_text(encoding="utf-8")
    ui = ui_file.read_text(encoding="utf-8")
    if "MiDiaDashboard.render(this)" not in main:
        main = replace_one(main, 'if(page==0)tasksPage();',
                           'if(page==0)MiDiaDashboard.render(this);', "home page")
        main = replace_one(main, '"Mi agenda","Calendario","Revisión","Conexiones"',
                           '"Inicio — Mi día","Calendario","Revisión","Conexiones"', "header")
        main = main.replace('"Agenda","Calendario","Revisar","Conexiones"',
                            '"Inicio","Calendario","Revisar","Conexiones"')
        main = replace_one(main, 'String pendingHistoryChat="";ScrollView contentScroll;',
                           'String pendingHistoryChat="";boolean dashboardAllTasksExpanded=false;ScrollView contentScroll;', "dashboard state")
        main = replace_one(main, 'if(state!=null){pendingHistoryChat=',
                           'if(state!=null){dashboardAllTasksExpanded=state.getBoolean("mi_dia_all_tasks",false);pendingHistoryChat=', "restore state")
        main = replace_one(main, 'out.putString("history_chat",pendingHistoryChat);',
                           'out.putBoolean("mi_dia_all_tasks",dashboardAllTasksExpanded);out.putString("history_chat",pendingHistoryChat);', "save state")
        main = replace_one(main, 'page=0;selectedCategory="Notas";render();',
                           'page=0;dashboardAllTasksExpanded=true;selectedCategory="Notas";render();', "notes deep link")
        main = replace_one(main, 'page=0;selectedCategory=note.category;render();',
                           'page=0;dashboardAllTasksExpanded=true;selectedCategory=note.category;render();', "notes widget deep link")
    if 'root.getChildAt(0).setVisibility(page==0?View.GONE:View.VISIBLE);' not in main:
        main = replace_one(main,
                           '        taskProgressCache=page<2?Store.get(this).subtaskProgressAll():Collections.emptyMap();',
                           '        // The landscape is the home header; original toolbar on other tabs.\n'
                           '        root.getChildAt(0).setVisibility(page==0?View.GONE:View.VISIBLE);\n'
                           '        taskProgressCache=page<2?Store.get(this).subtaskProgressAll():Collections.emptyMap();',
                           "home header visibility")
    if 'case "Inicio":' not in ui:
        ui = replace_one(ui, 'case "Agenda":return "check";',
                         'case "Inicio":case "Agenda":return "check";', "home nav icon")
    mandatory = ['MiDiaDashboard.render(this)', 'dashboardAllTasksExpanded',
                 '"Inicio","Calendario","Revisar","Conexiones"']
    if not all(term in main for term in mandatory):
        raise RuntimeError("Home integration validation failed")
    target = CODE / "MiDiaDashboard.java"
    if target.exists() and target.read_text(encoding="utf-8") != dashboard:
        raise RuntimeError("Refusing to overwrite different dashboard source")
    # Write all three only after each anchor and source has been validated.
    main_file.write_text(main, encoding="utf-8")
    ui_file.write_text(ui, encoding="utf-8")
    target.write_text(dashboard, encoding="utf-8")
    png = list((ROOT / "res/drawable-nodpi").glob("bg_mi_dia_*.png"))
    print(f"PASS phase51 native home connected to existing tasks/calendar; {len(png)}/30 approved backgrounds installed")
    if len(png) not in (0, 30):
        raise RuntimeError("Incomplete artwork pack: expected 0 or 30 PNGs")
    if not (ROOT / "res/values/mi_dia_frases.xml").is_file():
        raise RuntimeError("Missing daily quotes")

if __name__ == "__main__":
    run()
