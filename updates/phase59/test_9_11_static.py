#!/usr/bin/env python3
"""Source-level phase 9-11 smoke guards: no Java/Gradle/Android build."""
from pathlib import Path
import ast
import re

HERE = Path(__file__).resolve().parent
BASE = Path("AgendaClara/app/src/main")
CODE = BASE / "java/pe/agendaclara/app"

for script in (
        "phase56/apply_hero.py", "phase57/apply_schedule.py",
        "phase58/apply_activities.py"):
    filename = HERE.parent / script
    ast.parse(filename.read_text(encoding="utf-8"), filename=str(filename))

main = (CODE / "MainActivity.java").read_text(encoding="utf-8")
dashboard = (CODE / "MiDiaDashboard.java").read_text(encoding="utf-8")
header = (CODE / "MiDiaHeaderView.java").read_text(encoding="utf-8")
schedule_logic = (CODE / "MiDiaNextClass.java").read_text(encoding="utf-8")
schedule_card = (CODE / "MiDiaClassCard.java").read_text(encoding="utf-8")
course_links = (CODE / "MiDiaCourseLinks.java").read_text(encoding="utf-8")
activities = (CODE / "MiDiaActivitiesUi.java").read_text(encoding="utf-8")

# Phase 9: photo spans the screen; controls below it remain padded.
assert "body.setPadding(isHome?0:dp(22),isHome?0:dp(18)" in main
assert 'root.addView(new MiDiaHeaderView(activity))' in dashboard
assert 'body.setPadding(activity.dp(12), 0, activity.dp(12)' in dashboard
assert "Math.round(width * 864f / 1920f)" in header
assert "landscapeFrame.setLayoutParams(picture)" in header
assert "landscape.setScaleType(ImageView.ScaleType.CENTER_CROP)" in header
assert "MiDiaDailyRotation.backgroundResource" in header
assert "MiDiaDailyRotation.quote" in header
assert 'quote.setVisibility(View.GONE)' in header

# Phase 10: real local recurring class schedule, no calendar permission change.
assert "ScheduleDatabase.get(activity).all()" in dashboard
assert "MiDiaNextClass.choose(" in dashboard
assert "MiDiaClassCard.add(activity, body," in dashboard
assert "ScheduleEntry.valid(classTime)" in schedule_logic
assert "!classTime.enabled" in schedule_logic
assert "date.getDayOfWeek().getValue()" in schedule_logic
assert "start <= now && now < end" in schedule_logic
assert "current != null ? current : upcoming" in schedule_logic
assert "days <= 7" in schedule_logic
assert "new Intent(a, ScheduleActivity.class)" in schedule_card
assert "Clase en curso" in schedule_card
assert "Próxima clase" in schedule_card

# Phase 11: explicit course linking and separate scheduled/outstanding lists.
assert 'getSharedPreferences(FILE, Context.MODE_PRIVATE)' in course_links
assert "ScheduleCourseColors.identity" in course_links
assert "Store.get(c).find(taskId)" in course_links
assert "ScheduleDatabase.get(c).all()" in course_links
assert "MiDiaActivitiesUi.addCourse(activity, body," in dashboard
assert "MiDiaActivitiesUi.addToday(activity, body, tasks, dayStart, dayEnd)" in dashboard
assert "MiDiaActivitiesUi.addPending(activity, body, tasks, dayStart, dayEnd)" in dashboard
assert "MiDiaCourseLinks.assign(" in activities
assert "MiDiaCourseLinks.unlink(" in activities
assert "task.completedAt >= start" in activities
assert "t.due > 0 && t.due < start" in activities
assert "Store.get(a).save(fresh)" in activities
assert "Reminders.schedule(a, fresh)" in activities
assert "Reminders.cancel(a, fresh.id)" in activities
assert "TaskWidget.refresh(a)" in activities

# Existing features, five tabs, and approved daily phrase remain untouched.
assert "MiDiaNavigation.selectedTab(this)" in main
assert "MiDiaDayMetrics.calculate(tasks, dayStart, dayEnd)" in dashboard
assert "addProgress(activity, body, metrics);" in dashboard
assert "addQuote(activity, body, today);" in dashboard
assert "MiDiaDailyRotation.quote(a, date)" in dashboard
for original in ("void tasksPage()", "void calendarPage()", "void messagesPage()",
                 "void settingsPage()", "void openEditor(", "void showTaskDetails("):
    assert original in main, original

# Exactly the original 30 landscapes and 50 quotes are still installed.
from hashlib import sha256
import xml.etree.ElementTree as ET
drawables = BASE / "res/drawable-nodpi"
images = sorted(drawables.glob("bg_mi_dia_*.png"))
assert len(images) == 30, len(images)
assert len({sha256(p.read_bytes()).hexdigest() for p in images}) == 30
quotes = ET.parse(BASE / "res/values/mi_dia_frases.xml").getroot()
items = quotes.find("./string-array[@name='mi_dia_frases']")
assert items is not None and len(items.findall("item")) == 50

print("PASS 9-11: panoramic home, authentic class schedule, course links, day/pending lists, original functions")
print("NO Gradle, javac, APK, emulator or release invoked.")
