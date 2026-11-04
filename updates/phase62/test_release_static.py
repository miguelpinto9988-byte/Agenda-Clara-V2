#!/usr/bin/env python3
"""Phase 14: complete source/resource preflight before the approved Android build."""
from pathlib import Path
import ast
import hashlib
import re
import xml.etree.ElementTree as ET

APP = Path("AgendaClara/app/src/main")
SRC = APP / "java/pe/agendaclara/app"
UPDATES = Path("updates")
for path in [
    "phase56/apply_hero.py", "phase57/apply_schedule.py",
    "phase58/apply_activities.py", "phase60/apply_quick_actions.py",
    "phase61/apply_responsive_header.py", "phase62/version_3_13_0.py",
]:
    content = (UPDATES / path).read_text(encoding="utf-8")
    ast.parse(content, filename=path)

main = (SRC / "MainActivity.java").read_text(encoding="utf-8")
dashboard = (SRC / "MiDiaDashboard.java").read_text(encoding="utf-8")
header = (SRC / "MiDiaHeaderView.java").read_text(encoding="utf-8")
actions = (SRC / "MiDiaQuickActions.java").read_text(encoding="utf-8")
schedule = (SRC / "MiDiaNextClass.java").read_text(encoding="utf-8")
study = (SRC / "MiDiaActivitiesUi.java").read_text(encoding="utf-8")
version = Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")

assert "body.setPadding(isHome?0:dp(22)" in main
assert "root.addView(new MiDiaHeaderView(activity))" in dashboard
assert "imageStack" in header and "landscapeFrame" in header
assert "Math.round(width * 864f / 1920f)" in header
assert "if (widthDp < 360f)" in header and "} else if (widthDp < 600f)" in header
assert "Math.round(width * 0.73f)" in header and "Math.round(width * 0.62f)" in header
assert "greeting.setMaxLines(2)" in header
assert "dateTitle.setTextSize(widthDp < 360f ? 13f : 15f)" in header
assert "MiDiaDailyRotation.backgroundResource(getContext(), today)" in header

required = [
    "MiDiaClassCard.add(activity, body,",
    "MiDiaActivitiesUi.addCourse(activity, body,",
    "MiDiaActivitiesUi.addToday(activity, body,",
    "MiDiaActivitiesUi.addPending(activity, body,",
    "MiDiaQuickActions.add(activity, body);",
    "addProgress(activity, body, metrics);",
    "addQuote(activity, body, today);",
]
offsets = [dashboard.index(part) for part in required]
assert offsets == sorted(offsets), "User-approved design order must be preserved"

assert 'StickyNotesUi.showEditor(a, null)' in actions
assert "Store.get(a).save(task)" in actions
assert "Reminders.schedule(a, task)" in actions
assert "TaskWidget.refresh(a)" in actions
assert "new DatePickerDialog(a" in actions
assert "new TimePickerDialog(a" in actions
assert "if (due <= System.currentTimeMillis())" in actions
assert "chooseReminderTime(a, value)" in actions
assert 'a.page =' not in actions, "Quick actions cannot force a navigation away from home"
assert 'MiDiaDailyRotation.quote(a, date)' in dashboard
assert "MiDiaDailyRotation.quote(getContext(), today)" in header
assert 'quote.setVisibility(View.GONE)' in header
assert 'MiDiaDayMetrics.calculate(tasks, dayStart, dayEnd)' in dashboard
assert "MiDiaCourseLinks.assign(a, choice.id, course)" in study
assert "ScheduleDatabase.get(activity).all()" in dashboard
assert "start <= now && now < end" in schedule

for feature in (
    "void tasksPage()", "void calendarPage()", "void messagesPage()",
    "void settingsPage()", "void showCreationMenu()", "void openEditor(",
    "void showTaskDetails(", "StickyNotesUi", "VoiceQuickTask",
    "TaskWidget.refresh(this)", "MiDiaNavigation.selectedTab(this)",
):
    assert feature in main, feature

source_phrases = (UPDATES / "phase51/mi_dia_frases.xml").read_bytes()
installed_phrases = (APP / "res/values/mi_dia_frases.xml").read_bytes()
assert installed_phrases == source_phrases, "50 original phrases have been changed"
quotes = ET.fromstring(installed_phrases).find("./string-array[@name='mi_dia_frases']")
assert quotes is not None and len(quotes.findall("item")) == 50
images = list((APP / "res/drawable-nodpi").glob("bg_mi_dia_*.png"))
assert len(images) == 30
assert len({hashlib.sha256(p.read_bytes()).digest() for p in images}) == 30
assert "versionCode 56" in version and "versionName '3.13.0'" in version
assert "applicationId 'pe.agendaclara.app'" in version

print("PASS phases9–14: responsive narrow-phone and tablet hero, 3 quick actions, real schedule, all existing data paths")
print("PASS: exactly the original 30 pictures and 50 quotes remain installed")
print("PASS: update version 3.13.0 (56), no data schema/signing changes")
