#!/usr/bin/env python3
"""Non-compiling structural guards for phase 6; Android execution is deferred."""
from pathlib import Path
from hashlib import sha256
import xml.etree.ElementTree as ET

BASE = Path("AgendaClara/app/src/main")
CODE = BASE / "java/pe/agendaclara/app"
metrics = (CODE / "MiDiaDayMetrics.java").read_text(encoding="utf-8")
dashboard = (CODE / "MiDiaDashboard.java").read_text(encoding="utf-8")
header = (CODE / "MiDiaHeaderView.java").read_text(encoding="utf-8")
assert "final int progressPercent" in metrics
assert "totalToday == 0 ? 0" in metrics, "Empty day must not show 100%"
assert "task.completedAt >= dayStart" in metrics, "Completed tasks counted by completion date"
assert "task.due > 0 && task.due < dayEnd" in metrics, "Include due and overdue tasks"
assert "task.done != b.done" in metrics or "a.done != b.done" in metrics
assert "UiDesign.OutlineIcon" in dashboard
assert dashboard.count('"ic_midia_') == 4
assert 'MiDiaNavigation.open(a, 1)' in dashboard
assert 'MiDiaNavigation.open(a, 2)' in dashboard
assert 'MiDiaNavigation.open(a, 3)' in dashboard
assert "TaskWidget.refresh(a)" in dashboard
assert "Reminders.cancel(a" in dashboard and "Reminders.schedule(a" in dashboard
assert "CalendarBridge.selectedEvents(activity)" in dashboard
assert 'setTag("mi_dia_progress_section")' in dashboard
assert "MiDiaDailyRotation.quote(a, date)" in dashboard
assert "quote.setVisibility(View.GONE)" in header
assert "MiDiaDailyRotation.backgroundResource" in header
assert len(list((BASE/"res/drawable-nodpi").glob("bg_mi_dia_*.png"))) == 30
phrases = ET.parse(BASE/"res/values/mi_dia_frases.xml").getroot().find("./string-array[@name='mi_dia_frases']")
assert phrases is not None and len(phrases.findall("item")) == 50
print("PASS phase6 non-compiling structural guards: no empty-day 100%, task writes, local assets, quote position")
