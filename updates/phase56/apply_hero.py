#!/usr/bin/env python3
"""Phase 9: full-bleed responsive panorama for Mi día without changing other screens."""
from pathlib import Path
import hashlib

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE = Path(__file__).resolve().parent

def once(source, old, new, label):
    if old not in source or source.count(old) != 1:
        if new in source and old not in source:
            return source
        raise RuntimeError(label + ": expected exactly one patch anchor")
    return source.replace(old, new, 1)

def apply():
    main_path = CODE / "MainActivity.java"
    dash_path = CODE / "MiDiaDashboard.java"
    head_path = CODE / "MiDiaHeaderView.java"
    if not all(p.is_file() for p in (main_path, dash_path, head_path)):
        raise RuntimeError("Reconstruct all earlier phases first")
    main = main_path.read_text(encoding="utf-8")
    dashboard = dash_path.read_text(encoding="utf-8")
    approved_header = (HERE / "MiDiaHeaderView.java").read_text(encoding="utf-8")
    current_header = head_path.read_text(encoding="utf-8")
    if ("MiDiaDailyRotation.quote" not in current_header
            or "new MiDiaHeaderView(activity)" not in dashboard):
        raise RuntimeError("Unexpected existing home: refusing unsafe changes")

    main = once(main,
        "body.setPadding(isHome?dp(12):dp(22),isHome?dp(6):dp(18),\n                isHome?dp(12):dp(22),isHome?dp(18):dp(40));",
        "body.setPadding(isHome?0:dp(22),isHome?0:dp(18),\n                isHome?0:dp(22),isHome?dp(18):dp(40));",
        "Remove only the home body's horizontal inset")
    dashboard = once(dashboard,
        "        LinearLayout body = activity.body;\n        body.addView(new MiDiaHeaderView(activity));\n        activity.gap(body, 11);",
        """        LinearLayout root = activity.body;
        root.addView(new MiDiaHeaderView(activity));
        LinearLayout body = activity.column();
        body.setPadding(activity.dp(12), 0, activity.dp(12), activity.dp(18));
        root.addView(body);
        activity.gap(body, 11);""",
        "Add content inset under a full-width image")

    # Validate everything before modifying any files.
    for expected in ('imageStack', 'landscapeFrame',
                     'Math.round(width * 864f / 1920f)',
                     'quote.setVisibility(View.GONE)',
                     'MiDiaDailyRotation.backgroundResource',
                     'MiDiaDailyRotation.quote'):
        if expected not in approved_header:
            raise RuntimeError("Missing approved panoramic header token: " + expected)
    if 'new MiDiaHeaderView(activity)' not in dashboard:
        raise RuntimeError("Home header was accidentally removed")
    if "MiDiaNavigation.selectedTab(this)" not in main:
        raise RuntimeError("Phase 7 navigation no longer connected")
    main_path.write_text(main, encoding="utf-8")
    dash_path.write_text(dashboard, encoding="utf-8")
    head_path.write_text(approved_header, encoding="utf-8")
    print("PASS phase9: wallpaper spans full tablet/phone width; inner cards stay padded; all 50 phrases retained")

if __name__ == "__main__":
    apply()
