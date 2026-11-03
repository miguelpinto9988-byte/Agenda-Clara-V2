#!/usr/bin/env python3
"""Offline regression checks for phase51's approved resource archive."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess
import sys
import xml.etree.ElementTree as ET

PHASE = Path(__file__).resolve().parent
INSTALL = PHASE / "install_resources.py"

def check(package: Path):
    with ZipFile(package) as z:
        names = set(z.namelist())
        images = {f"app/src/main/res/drawable-nodpi/bg_mi_dia_{n:02d}.png" for n in range(1, 31)}
        assert images <= names, "Missing PNG resources"
        for path in images:
            data = z.read(path)
            assert data[:8] == b"\x89PNG\r\n\x1a\n", path
            assert int.from_bytes(data[16:20], "big") == 1920, path
            assert int.from_bytes(data[20:24], "big") == 864, path
        quotes_path = "app/src/main/res/values/mi_dia_frases.xml"
        assert quotes_path in names
        xml = ET.fromstring(z.read(quotes_path))
        quotes = xml.find("./string-array[@name='mi_dia_frases']")
        assert quotes is not None and len(quotes.findall("item")) == 50
        assert all((x.text or "").strip() for x in quotes.findall("item"))
        for java in ("MiDiaDailyRotation.java", "MiDiaHeaderView.java"):
            path = "app/src/main/java/pe/agendaclara/app/" + java
            assert path in names
            assert b"package pe.agendaclara.app;" in z.read(path)
    print("PASS: 30 approved PNG, 50 nonempty quotes, daily rotation and header sources")

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 updates/phase51/test_resources.py APPROVED_RESOURCES.zip")
    check(Path(sys.argv[1]))

if __name__ == "__main__":
    main()
