#!/usr/bin/env python3
"""Phases 12–14: non-build guards for quick actions, footer, responsive home."""
from pathlib import Path
import ast

base = Path("AgendaClara/app/src/main")
code = base / "java/pe/agendaclara/app"
for name in ("phase60/apply_quick_actions.py", "phase61/apply_motivation.py",
             "phase62/apply_responsive.py"):
    p = Path("updates") / name
    ast.parse(p.read_text(encoding="utf-8"), filename=str(p))

main = (code / "MainActivity.java").read_text(encoding="utf-8")
head = (code / "MiDiaHeaderView.java").read_text(encoding="utf-8")
dash = (code / "MiDiaDashboard.java").read_text(encoding="utf-8")
quick = (code / "MiDiaQuickActions.java").read_text(encoding="utf-8")
card = (code / "MiDiaClassCard.java").read_text(encoding="utf-8")

for value in ("Tarea rápida", "Nota rápida", "Recordatorio",
              "StickyNotesUi.showEditor(a, null)",
              "Reminders.schedule(a, task)", "TaskWidget.refresh(a)",
              "Store.get(a).save(task)", "TimePickerDialog", "DatePickerDialog"):
    assert value in quick, value
for value in ("MiDiaQuickActions.add(activity, body);",
              "MiDiaActivitiesUi.addCourse(activity, body,",
              "MiDiaActivitiesUi.addToday(activity, body,",
              "MiDiaActivitiesUi.addPending(activity, body,",
              "addProgress(activity, body, metrics);",
              "addQuote(activity, body, today);",
              "MiDiaDailyRotation.quote(a, date)"):
    assert value in dash, value
assert dash.index("MiDiaQuickActions.add(activity, body);") < dash.index(
    "addProgress(activity, body, metrics);") < dash.index("addQuote(activity, body, today);")
assert "boolean twoRows = widthDp < 400 || fontScale > 1.28f;" in dash
assert "greeting.setTextSize(widthDp < 330 ? 19 : widthDp < 400 ? 21 : 23)" in head
assert "Math.round(width * 864f / 1920f)" in head
assert "landscape.setScaleType(ImageView.ScaleType.CENTER_CROP)" in head
assert "dateSubtitle.setEllipsize(TextUtils.TruncateAt.END)" in head
assert "new Intent(a, ScheduleActivity.class)" in card
assert "MiDiaNavigation.selectedTab(this)" in main
assert "void showCreationMenu()" in main
assert "void calendarPage()" in main
assert "void messagesPage()" in main
assert "void settingsPage()" in main
print("PASS phases12–14: original editors/stores/reminders/widgets, motivation, small-phone layout")
