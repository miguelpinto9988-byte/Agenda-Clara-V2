#!/usr/bin/env python3
"""Phase 13: preserve the 50-phrase motivational footer and clarify visual sections."""
from pathlib import Path

DASH = Path("AgendaClara/app/src/main/java/pe/agendaclara/app/MiDiaDashboard.java")
OLD = """        MiDiaQuickActions.add(activity, body);
        addProgress(activity, body, metrics);
        addQuote(activity, body, today);
        activity.gap(body, 8);"""
NEW = """        MiDiaQuickActions.add(activity, body);
        activity.gap(body, 10);
        addProgress(activity, body, metrics);
        // The existing 50 daily phrases remain the last content on Inicio.
        addQuote(activity, body, today);
        activity.gap(body, 16);"""

def run():
    content = DASH.read_text(encoding="utf-8")
    if NEW not in content:
        if content.count(OLD) != 1:
            raise RuntimeError("Phase12 home not found; refusing to change motivational footer")
        content = content.replace(OLD, NEW, 1)
    for required in ("MiDiaDailyRotation.quote(a, date)",
                     "MiDiaDayMetrics.calculate(tasks, dayStart, dayEnd)",
                     "addQuote(activity, body, today);",
                     "addProgress(activity, body, metrics);"):
        if required not in content:
            raise RuntimeError("Required existing feature missing: " + required)
    DASH.write_text(content, encoding="utf-8")
    print("PASS phase13: progress separated; original daily phrase remains last")

if __name__ == "__main__":
    run()
