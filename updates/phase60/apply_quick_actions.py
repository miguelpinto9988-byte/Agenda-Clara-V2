#!/usr/bin/env python3
"""Phase 12: install non-navigating quick actions immediately above daily progress."""
from pathlib import Path
import shutil

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE = Path(__file__).resolve().parent
DASHBOARD = CODE / "MiDiaDashboard.java"

def run():
    before = """        MiDiaActivitiesUi.addPending(activity, body, tasks, dayStart, dayEnd);
        addProgress(activity, body, metrics);
        addQuote(activity, body, today);"""
    after = """        MiDiaActivitiesUi.addPending(activity, body, tasks, dayStart, dayEnd);
        MiDiaQuickActions.add(activity, body);
        addProgress(activity, body, metrics);
        addQuote(activity, body, today);"""
    if not DASHBOARD.is_file():
        raise RuntimeError("Reconstruct and apply phase58 first")
    existing = DASHBOARD.read_text(encoding="utf-8")
    if after not in existing:
        if existing.count(before) != 1:
            raise RuntimeError("Unexpected phase11 rendering: refusing incomplete update")
        existing = existing.replace(before, after, 1)
    source = (HERE / "MiDiaQuickActions.java").read_text(encoding="utf-8")
    target = CODE / "MiDiaQuickActions.java"
    if target.is_file() and target.read_text(encoding="utf-8") != source:
        raise RuntimeError("Refusing to overwrite different quick-action module")
    if "MiDiaDailyRotation.quote(a, date)" not in existing:
        raise RuntimeError("Phase12 cannot change the original daily motivational phrase")
    DASHBOARD.write_text(existing, encoding="utf-8")
    shutil.copyfile(HERE / "MiDiaQuickActions.java", target)
    print("PASS phase12: quick task, sticky note and explicit timed reminder from Inicio")

if __name__ == "__main__":
    run()
