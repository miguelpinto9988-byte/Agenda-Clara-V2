#!/usr/bin/env python3
"""Phase 10: replace only the home calendar prompt with the real class schedule.
Does not change the calendar page, CalendarBridge, ScheduleDatabase or Task rows.
Run after phase56/apply_hero.py and before phase58.
"""
from pathlib import Path
import shutil

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE = Path(__file__).resolve().parent
TARGET = CODE / "MiDiaDashboard.java"

BEFORE = """        addStats(activity, body, metrics, eventsToday, hasCalendarPermission);
        activity.gap(body, 16);
        addTaskList(activity, body, metrics, zone);
        addNextEvent(activity, body, next, hasCalendarPermission, zone);
        addProgress(activity, body, metrics);"""
AFTER = """        addStats(activity, body, metrics, eventsToday, hasCalendarPermission);
        activity.gap(body, 16);
        sectionHeader(activity, body, "☷  Mi día", null, null);
        MiDiaClassCard.add(activity, body,
                MiDiaNextClass.choose(ScheduleDatabase.get(activity).all(),
                        java.time.ZonedDateTime.now(zone)));
        activity.gap(body, 12);
        addTaskList(activity, body, metrics, zone);
        addProgress(activity, body, metrics);"""

def run():
    if not TARGET.is_file():
        raise RuntimeError("Reconstruct Android sources and apply earlier phases first")
    original = TARGET.read_text(encoding="utf-8")
    if AFTER not in original:
        if original.count(BEFORE) != 1:
            raise RuntimeError("Unrecognized home render order; refusing to patch")
        changed = original.replace(BEFORE, AFTER, 1)
    else:
        changed = original
    for name in ("MiDiaNextClass.java", "MiDiaClassCard.java"):
        source = (HERE / name).read_text(encoding="utf-8")
        target = CODE / name
        if target.exists() and target.read_text(encoding="utf-8") != source:
            raise RuntimeError("Unexpected existing class: " + name)
        if "package pe.agendaclara.app;" not in source:
            raise RuntimeError("Unexpected Java package")
    if "MiDiaDailyRotation.quote(a, date)" not in changed:
        raise RuntimeError("Daily motivational phrase unexpectedly removed")
    TARGET.write_text(changed, encoding="utf-8")
    for name in ("MiDiaNextClass.java", "MiDiaClassCard.java"):
        shutil.copyfile(HERE / name, CODE / name)
    print("PASS phase10: current/next class comes from saved weekly schedule; calendar services unchanged")

if __name__ == "__main__":
    run()
