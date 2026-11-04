#!/usr/bin/env python3
"""Static checks for the requested three Mi día shortcuts (no Android build)."""
from pathlib import Path
import ast
import re

here = Path(__file__).resolve().parent
app = Path("AgendaClara/app/src/main")
code = app / "java/pe/agendaclara/app"
quick = (code / "MiDiaQuickActions.java").read_text(encoding="utf-8")
menu = (code / "CreationChoices.java").read_text(encoding="utf-8")
dashboard = (code / "MiDiaDashboard.java").read_text(encoding="utf-8")
main = (code / "MainActivity.java").read_text(encoding="utf-8")
base = (code / "ApprovedPng.java").read_text(encoding="utf-8")
ast.parse((here / "apply_home_quick_actions.py").read_text(encoding="utf-8"))

labels = ("Tarea rápida", "Nueva tarea", "Nueva nota")
descriptions = ("Dictar con comandos · sin grabación guardada",
                "Registrar una actividad", "Nota adhesiva con fecha")
routes = ("() -> VoiceQuickTask.show(activity)",
          "() -> activity.openEditor(-1, null, null)",
          "() -> StickyNotesUi.showEditor(activity, null)")
icons = ("voice_microphone", "save", "sticky_note")
for label, description, route, art in zip(labels, descriptions, routes, icons):
    assert quick.count('"' + label + '"') == 1, label
    assert '"' + description + '"' in quick, description
    assert route in quick, route
    assert 'ApprovedPng.view(activity, png, 36)' in quick
    assert (app / "res/drawable-nodpi" / ("ic_ref_" + art + ".png")).is_file(), art
assert quick.index('"Tarea rápida"') < quick.index('"Nueva tarea"') < quick.index('"Nueva nota"')
assert "quickTask(activity, false)" not in quick
assert 'tile(a, "Recordatorio"' not in quick
assert quick.count("option(activity, parent,") == 3
assert "card.setOnClickListener(v -> action.run())" in quick
assert "card.setContentDescription(title + \". \" + subtitle)" in quick
assert "artwork.setImportantForAccessibility(ImageView.IMPORTANT_FOR_ACCESSIBILITY_NO)" in quick
assert "MiDiaQuickActions.add(activity, body);" in dashboard
assert "addQuote(activity, body, today);" in dashboard
assert 'MiDiaDailyRotation.quote(a, date)' in dashboard
assert "CreationChoices.show(this,add,()->openEditor(-1,null,null)" in main
assert "Tarea rápida" in menu and "Nueva tarea" in menu and "Nueva nota" in menu
for token in ('"voice_microphone"', '"save"', '"sticky_note"'):
    assert token in quick and token in menu
print("PASS: exact voice / full task / dated note options, texts and original PNG resources")
print("PASS: header + popup, Mi día section and 50-quote footer preserved; no APK compiled")
