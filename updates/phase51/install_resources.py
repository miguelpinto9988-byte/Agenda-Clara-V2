#!/usr/bin/env python3
"""Install approved Mi día resources into a reconstructed Agenda Clara source tree.

Run after phase50, with the approved ZIP provided explicitly as argument.
Never silently substitute missing artwork. No changes are made to the source
tree until every asset and resource has passed validation.
"""
from pathlib import Path
from zipfile import ZipFile
import io
import struct
import sys
import xml.etree.ElementTree as ET

ROOT = Path("AgendaClara")
SOURCE = Path(__file__).resolve().parent
EXPECTED = [f"app/src/main/res/drawable-nodpi/bg_mi_dia_{i:02d}.png" for i in range(1, 31)]
OTHER = [
    "app/src/main/res/values/mi_dia_frases.xml",
    "app/src/main/java/pe/agendaclara/app/MiDiaDailyRotation.java",
    "app/src/main/java/pe/agendaclara/app/MiDiaHeaderView.java",
]

def install(package):
    if not (ROOT / "app/build.gradle").is_file():
        raise RuntimeError("Reconstruct AgendaClara and apply phase50 first")
    with ZipFile(package) as archive:
        files = {}
        for name in EXPECTED + OTHER:
            files[name] = archive.read(name)
        for name in EXPECTED:
            data = files[name]
            if data[:8] != bytes((137, 80, 78, 71, 13, 10, 26, 10)) or struct.unpack(">II", data[16:24]) != (1920, 864):
                raise RuntimeError("Unexpected PNG format/dimensions: " + name)
        root = ET.fromstring(files[OTHER[0]])
        phrases = root.find("string-array")
        if phrases is None or phrases.get("name") != "mi_dia_frases" or len(phrases.findall("item")) != 50:
            raise RuntimeError("Expected exactly 50 offline quotes")
        for name in OTHER[1:]:
            if b"package pe.agendaclara.app;" not in files[name]:
                raise RuntimeError("Unexpected Java package: " + name)
        # Phase51 text sources are staged from GitHub, so the ZIP may carry
        # older Java drafts. Keep the reviewed sources already in the tree.
        for name in EXPECTED:
            target = ROOT / name
            if target.exists() and target.read_bytes() != files[name]:
                raise RuntimeError("Refusing to overwrite existing PNG: " + name)
        for name in EXPECTED:
            target = ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(files[name])
    print("PASS: 30 PNG installed; ZIP text resources validated; staged Java/XML unchanged; MainActivity not modified")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 updates/phase51/install_resources.py APPROVED_RESOURCES.zip")
    install(Path(sys.argv[1]))
