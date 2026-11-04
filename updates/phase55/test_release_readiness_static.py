#!/usr/bin/env python3
"""Phase 8 design-release preflight. DOES NOT compile/build/run Android.

To be executed after phase53, phase54 and phase55 staging.
It checks resources, navigation, original feature paths and artifact safety.
"""
from pathlib import Path
from hashlib import sha256
from struct import unpack
import ast
import xml.etree.ElementTree as ET

ROOT = Path("AgendaClara/app/src/main")
CODE = ROOT / "java/pe/agendaclara/app"
HERE = Path(__file__).resolve().parent

for relative in (
        "phase53/apply_dashboard.py", "phase53/test_dashboard_static.py",
        "phase54/apply_navigation.py", "phase54/test_navigation_static.py",
        "phase55/apply_polish.py"):
    path = HERE.parent / relative
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

main = (CODE / "MainActivity.java").read_text(encoding="utf-8")
ui = (CODE / "UiDesign.java").read_text(encoding="utf-8")
dashboard = (CODE / "MiDiaDashboard.java").read_text(encoding="utf-8")
header = (CODE / "MiDiaHeaderView.java").read_text(encoding="utf-8")
metrics = (CODE / "MiDiaDayMetrics.java").read_text(encoding="utf-8")
nav = (CODE / "MiDiaNavigation.java").read_text(encoding="utf-8")
study = (CODE / "MiDiaStudyPage.java").read_text(encoding="utf-8")
more = (CODE / "MiDiaMorePage.java").read_text(encoding="utf-8")

for term in ('MiDiaDashboard.render(this)', 'MiDiaStudyPage.render(this)',
             'MiDiaMorePage.render(this)', 'body.setPadding(isHome?',
             'newTask.setContentDescription("Crear una tarea o nota")',
             'newTask.setTag("home_create_button")',
             'if(add==null||!add.isShown())add=root==null?null:root.findViewWithTag("new_task_button")',
             'out.putInt("mi_dia_home_section",homeSection)',
             'page=Math.max(0,Math.min(4,state.getInt("page")))',
             'void tasksPage()', 'void calendarPage()', 'void messagesPage()',
             'void settingsPage()', 'void taskCard(', 'void openEditor(',
             'void showCreationMenu(', 'StickyNotesUi', 'VoiceQuickTask',
             'WhatsAppSessionService', 'TaskWidget.refresh(this)'):
    assert term in main, "Missing app feature/route: " + term

assert 'TAB_LABELS = {"Inicio", "Tareas", "Estudio", "Calendario", "Más"}' in nav
for term in ('case "home":', 'case "graduation":', 'case "grid":'):
    assert term in ui, "Missing navigation vector: " + term
assert 'widthDp < 360 || fontScale > 1.28f' in dashboard
assert 'MiDiaDayMetrics.calculate(tasks, dayStart, dayEnd)' in dashboard
assert 'MiDiaDailyRotation.quote(a, date)' in dashboard
assert "quote.setVisibility(View.GONE)" in header
assert "totalToday == 0 ? 0" in metrics
assert "MiDiaNavigation.open(a, 1)" in more
assert "originalPage(a, 2, 0)" in more
assert "originalPage(a, 3, 0)" in more
assert "originalPage(a, 3, 1)" in more
assert "originalPage(a, 3, 2)" in more
assert "new Intent(a, ScheduleActivity.class)" in (study + more)

picture_dir = ROOT / "res/drawable-nodpi"
images = sorted(picture_dir.glob("bg_mi_dia_*.png"))
assert len(images) == 30, "Need exactly 30 approved offline landscapes"
digests = set()
for picture in images:
    data = picture.read_bytes()
    assert data[:8] == bytes((137, 80, 78, 71, 13, 10, 26, 10))
    assert unpack(">II", data[16:24]) == (1920, 864), str(picture)
    digests.add(sha256(data).hexdigest())
assert len(digests) == 30, "All backgrounds must remain distinct"

for icon in ("ic_midia_tareas.png", "ic_midia_eventos.png",
             "ic_midia_estudio.png", "ic_midia_logros.png"):
    icon_path = picture_dir / icon
    assert icon_path.exists(), "Missing approved card icon: " + icon

quotes_file = ROOT / "res/values/mi_dia_frases.xml"
array = ET.parse(quotes_file).getroot().find("./string-array[@name='mi_dia_frases']")
assert array is not None and len(array.findall("item")) == 50
assert all((x.text or "").strip() for x in array.findall("item"))

for module in (CODE / "WhatsAppNative.java",
               CODE / "StickyNotesUi.java",
               CODE / "VoiceQuickTask.java",
               CODE / "CalendarBridge.java",
               CODE / "ScheduleActivity.java"):
    assert module.is_file(), "Original module missing: " + str(module)

print("PASS phase8: static design and 30/50 resources verified; all legacy entry points preserved")
print("NO BUILD executed. Final Android compile/emulator QA requires explicit approval.")
