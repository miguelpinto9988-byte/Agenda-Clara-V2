#!/usr/bin/env python3
"""Reconstruct and install the 30 approved daily PNG backgrounds bundled in Git.

All artwork is available offline. The ZIP is split into 12 Git blobs only to
keep individual uploads within transport limits. The installer validates the
whole archive before changing Android resources.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import io
import struct

HERE = Path(__file__).resolve().parent
PARTS = HERE / "artwork"
ROOT = Path("AgendaClara/app/src/main/res/drawable-nodpi")
EXPECTED_SHA256 = "9b74990a2f2c2728f0e5760739f63bbaa781eaf9b6b6baf9ad956c4e4d077bba"
EXPECTED = [
    f"app/src/main/res/drawable-nodpi/bg_mi_dia_{i:02d}.png"
    for i in range(1, 31)
]
PNG_SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])


def install():
    if not Path("AgendaClara/app/build.gradle").is_file():
        raise RuntimeError("Reconstruct AgendaClara before installing phase51")
    parts = sorted(PARTS.glob("part*.bin"))
    if len(parts) != 12 or [p.name for p in parts] != [f"part{i:02d}.bin" for i in range(1, 13)]:
        raise RuntimeError("Incomplete phase51 artwork archive: 12 ordered parts required")
    archive_bytes = b"".join(p.read_bytes() for p in parts)
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError("Artwork SHA-256 mismatch: " + digest)
    with ZipFile(io.BytesIO(archive_bytes)) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Artwork ZIP CRC verification failed")
        if sorted(archive.namelist()) != sorted(EXPECTED):
            raise RuntimeError("Artwork archive must contain exactly 30 approved daily PNGs")
        files = {}
        for name in EXPECTED:
            data = archive.read(name)
            if (data[:8] != PNG_SIGNATURE
                    or len(data) < 24
                    or struct.unpack(">II", data[16:24]) != (1920, 864)):
                raise RuntimeError("Unexpected PNG dimensions/format: " + name)
            files[name] = data
    if len(set(hashlib.sha256(data).hexdigest() for data in files.values())) != 30:
        raise RuntimeError("Backgrounds must all be distinct")
    for name, data in files.items():
        target = ROOT / Path(name).name
        if target.exists() and target.read_bytes() != data:
            raise RuntimeError("Refusing to overwrite a different PNG: " + target.name)
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = ROOT / Path(name).name
        if not target.exists():
            target.write_bytes(data)
    print("PASS phase51: 30 distinct approved 1920x864 PNGs installed offline; archive SHA-256:", digest)


if __name__ == "__main__":
    install()
