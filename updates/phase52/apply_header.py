#!/usr/bin/env python3
"""Install approved phase-5 visual header after phase51, without modifying app logic."""
from pathlib import Path
import hashlib

BASE = Path("AgendaClara/app/src/main")
CODE = BASE / "java/pe/agendaclara/app"
HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "phase51/MiDiaHeaderView.java"
REPLACEMENT = HERE / "MiDiaHeaderView.java"
TARGET = CODE / "MiDiaHeaderView.java"


def run():
    main = CODE / "MainActivity.java"
    if not main.is_file() or not TARGET.is_file():
        raise RuntimeError("First rebuild sources and apply phase51")
    if "MiDiaDashboard.render(this)" not in main.read_text(encoding="utf-8"):
        raise RuntimeError("Phase51 home not connected; refusing partial phase5")
    before_main = hashlib.sha256(main.read_bytes()).hexdigest()
    expected_previous = PREVIOUS.read_bytes()
    desired = REPLACEMENT.read_bytes()
    current = TARGET.read_bytes()
    if current not in (expected_previous, desired):
        raise RuntimeError("Unrecognized MiDiaHeaderView; refusing to overwrite user changes")
    source = desired.decode("utf-8")
    if "package pe.agendaclara.app;" not in source:
        raise RuntimeError("Unexpected Java package")
    anchors = (
        "Paisaje ilustrado del día",
        "MiDiaDailyRotation.backgroundResource",
        "MiDiaDailyRotation.quote",
        "Semana ",
        "IsoFields.WEEK_OF_WEEK_BASED_YEAR",
        "Revisar propuestas y notificaciones",
        "Abrir conexiones y ajustes",
        "Personalizar saludo",
    )
    if not all(term in source for term in anchors):
        raise RuntimeError("A mandatory phase5 design/interaction anchor is missing")
    if current != desired:
        TARGET.write_bytes(desired)
    assert hashlib.sha256(main.read_bytes()).hexdigest() == before_main
    print("PASS phase5: home-only branding, greeting, floating date, existing events/notes/voice/widgets unchanged")


if __name__ == "__main__":
    run()
