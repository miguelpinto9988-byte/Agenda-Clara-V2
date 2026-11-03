#!/usr/bin/env python3
"""Exercise the real phase51 installer with 30 distinct synthetic PNG fixtures."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import os
import struct
import subprocess
import sys
import zlib

HERE = Path(__file__).resolve().parent
INSTALLER = HERE / "install_resources.py"

def png(rgb):
    w, h = 1920, 864
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    scanline = b"\x00" + bytes(rgb) * w
    pixels = zlib.compress(scanline * h, 9)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")

def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = root / "AgendaClara"
        (project / "app").mkdir(parents=True)
        (project / "app/build.gradle").write_text("// synthetic fixture")
        archive = root / "assets.zip"
        with ZipFile(archive, "w") as z:
            for i in range(1, 31):
                z.writestr(f"app/src/main/res/drawable-nodpi/bg_mi_dia_{i:02d}.png", png((i, 255-i, i*3 % 256)))
            for name in ("MiDiaDailyRotation.java", "MiDiaHeaderView.java"):
                z.writestr(f"app/src/main/java/pe/agendaclara/app/{name}", (HERE / name).read_bytes())
            z.writestr("app/src/main/res/values/mi_dia_frases.xml", (HERE / "mi_dia_frases.xml").read_bytes())
        def run():
            return subprocess.run([sys.executable, str(INSTALLER), str(archive)], cwd=root, capture_output=True, text=True)
        first = run()
        assert first.returncode == 0, first.stderr
        images = [project / f"app/src/main/res/drawable-nodpi/bg_mi_dia_{i:02d}.png" for i in range(1,31)]
        assert len({p.read_bytes() for p in images}) == 30, "PNG files must not be duplicated"
        assert not (project / "app/src/main/java/pe/agendaclara/app/MiDiaHeaderView.java").exists(), "Installer must not replace staged Java"
        assert run().returncode == 0, "Installing identical resources should be idempotent"
        images[0].write_bytes(b"protected artwork")
        assert run().returncode != 0, "Conflicting PNG must be rejected"
    print("PASS phase51 installer: 30 distinct PNGs, idempotence, overwrite protection")

if __name__ == "__main__":
    main()
