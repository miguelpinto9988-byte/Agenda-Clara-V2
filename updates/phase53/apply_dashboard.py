#!/usr/bin/env python3
"""Phase 6: replace only the Mi día dashboard and move the offline quote below progress.

No change to MainActivity, SQLite, calendar synchronization, WhatsApp, voice or widgets.
Executed only after phase52 and the original phase51 reconstruction.
"""
from pathlib import Path
import hashlib
import shutil

APP = Path("AgendaClara/app/src/main")
PKG = APP / "java/pe/agendaclara/app"
HERE = Path(__file__).resolve().parent
DASHBOARD = PKG / "MiDiaDashboard.java"
METRICS = PKG / "MiDiaDayMetrics.java"
HEADER = PKG / "MiDiaHeaderView.java"
LEGACY = HERE.parent / "phase51/MiDiaDashboard.java"

def install():
    if not (PKG / "MainActivity.java").is_file():
        raise RuntimeError("Build the original Android sources before applying phase6")
    old_dashboard = LEGACY.read_bytes()
    new_dashboard = (HERE / "MiDiaDashboard.java").read_bytes()
    old = DASHBOARD.read_bytes()
    if old not in (old_dashboard, new_dashboard):
        raise RuntimeError("Unrecognized dashboard; refused destructive overwrite")
    new_metrics = (HERE / "MiDiaDayMetrics.java").read_bytes()
    if METRICS.exists() and METRICS.read_bytes() != new_metrics:
        raise RuntimeError("Unrecognized day metrics; refused overwrite")
    header = HEADER.read_text(encoding="utf-8")
    before = "        addView(quote, quoteParams);"
    after = before + "\n        quote.setVisibility(View.GONE);"
    if after not in header:
        if header.count(before) != 1:
            raise RuntimeError("Could not locate phase5 quote; refused partial phase6")
        header = header.replace(before, after, 1)
    main = PKG / "MainActivity.java"
    main_hash = hashlib.sha256(main.read_bytes()).hexdigest()
    DASHBOARD.write_bytes(new_dashboard)
    METRICS.write_bytes(new_metrics)
    HEADER.write_text(header, encoding="utf-8")
    if hashlib.sha256(main.read_bytes()).hexdigest() != main_hash:
        raise RuntimeError("Unexpected MainActivity mutation")
    print("PASS phase6: compact live cards, interactive tasks, correct daily progress, next event and bottom quote")

if __name__ == "__main__":
    install()
