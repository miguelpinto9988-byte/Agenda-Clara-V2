#!/usr/bin/env python3
"""Stage phase51's text-only Android resources after phase50.

Safe without the binary artwork: the header will only be instantiated after
the 30 approved PNG files have been installed and validated.
"""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

stage = Path(__file__).resolve().parent
root = Path("AgendaClara")
if not (root / "app/build.gradle").is_file():
    raise RuntimeError("Reconstruct AgendaClara before staging phase51")
xml = ET.parse(stage / "mi_dia_frases.xml")
quotes = xml.getroot().find("./string-array[@name='mi_dia_frases']")
if quotes is None or len(quotes.findall("item")) != 50:
    raise RuntimeError("Phase51 must contain exactly 50 phrases")
paths = {
    "MiDiaDailyRotation.java": root / "app/src/main/java/pe/agendaclara/app/MiDiaDailyRotation.java",
    "MiDiaHeaderView.java": root / "app/src/main/java/pe/agendaclara/app/MiDiaHeaderView.java",
    "mi_dia_frases.xml": root / "app/src/main/res/values/mi_dia_frases.xml",
}
for name, target in paths.items():
    source = stage / name
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise RuntimeError("Refusing to overwrite: " + str(target))
for name, target in paths.items():
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(stage / name, target)
print("PASS phase51: two Java sources and 50 phrases staged; original home unchanged")
