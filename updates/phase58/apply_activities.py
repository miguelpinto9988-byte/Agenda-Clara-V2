#!/usr/bin/env python3
"""Phase 11: attach course-linked, today and outstanding activity windows.

Only the render composition for Inicio — Mi día changes. Existing Task rows,
ScheduleDatabase, Google Calendar integrations, WhatsApp, voice and widgets are
left intact. The original daily motivational quote remains below progress.
"""
from pathlib import Path
import shutil

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE = Path(__file__).resolve().parent
DASHBOARD = CODE / "MiDiaDashboard.java"

BEFORE = """        addTaskList(activity, body, metrics, zone);
        addProgress(activity, body, metrics);"""
AFTER = """        MiDiaActivitiesUi.addCourse(activity, body,
                MiDiaNextClass.choose(ScheduleDatabase.get(activity).all(),
                        java.time.ZonedDateTime.now(zone)), tasks);
        MiDiaActivitiesUi.addToday(activity, body, tasks, dayStart, dayEnd);
        MiDiaActivitiesUi.addPending(activity, body, tasks, dayStart, dayEnd);
        addProgress(activity, body, metrics);"""

def run():
    old = DASHBOARD.read_text(encoding="utf-8")
    if AFTER in old:
        changed = old
    elif old.count(BEFORE) == 1:
        changed = old.replace(BEFORE, AFTER, 1)
    else:
        raise RuntimeError("Phase10 must precede phase11; stopped without altering files")
    if "MiDiaClassCard.add(activity, body," not in changed:
        raise RuntimeError("Phase10 current class card missing")
    if "addQuote(activity, body, today);" not in changed:
        raise RuntimeError("The existing 50-phrase rotation cannot be removed")
    for name in ("MiDiaCourseLinks.java", "MiDiaActivitiesUi.java"):
        source = (HERE / name).read_text(encoding="utf-8")
        target = CODE / name
        if not source.startswith("package pe.agendaclara.app;"):
            raise RuntimeError("Invalid package: " + name)
        if target.exists() and target.read_text(encoding="utf-8") != source:
            raise RuntimeError("Conflicting existing class: " + name)
    DASHBOARD.write_text(changed, encoding="utf-8")
    for name in ("MiDiaCourseLinks.java", "MiDiaActivitiesUi.java"):
        shutil.copyfile(HERE / name, CODE / name)
    print("PASS phase11: course links explicit, today and pending lists shown, motivation unchanged")

if __name__ == "__main__":
    run()
