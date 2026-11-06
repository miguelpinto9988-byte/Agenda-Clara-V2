#!/usr/bin/env python3
"""Correct RemoteViews-only widget layouts and release Agenda Clara 3.15.3.

The old academic widget XML uses <View/> as a separator. Android's widget
RemoteViews inflater does not permit generic android.view.View. Replace it
with a supported FrameLayout without changing spacing, background or data.
"""

from pathlib import Path
import hashlib
import os
import re
import tempfile
import xml.etree.ElementTree as ET

APP = Path("AgendaClara/app/src/main")
RES = APP / "res/layout"
GRADLE = Path("AgendaClara/app/build.gradle")
DAY = RES / "widget_academic_day.xml"
WEEK = RES / "widget_academic_week.xml"
PHOTO = [
    APP / "java/pe/agendaclara/app/PhotoWidget.java",
    APP / "java/pe/agendaclara/app/PhotoConfigActivity.java",
    APP / "java/pe/agendaclara/app/PhotoTapActivity.java",
    RES / "widget_photo.xml",
    APP / "res/xml/photo_widget_info.xml",
]


def atomic_write(path: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.84-",
        suffix=".tmp", encoding="utf-8", delete=False
    ) as temp:
        temp.write(text)
        temp.flush()
        os.fsync(temp.fileno())
        name = temp.name
    try:
        os.chmod(name, path.stat().st_mode & 0o777)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def main() -> None:
    original = {p: p.read_text(encoding="utf-8") for p in (DAY, WEEK, GRADLE)}
    photo_hash = {p: hashlib.sha256(p.read_bytes()).digest() for p in PHOTO}
    gradle = original[GRADLE]
    if "versionCode 70" in gradle and "versionName '3.15.3'" in gradle:
        if any(re.search(r"<View(?:\\s|>)", original[p]) for p in (DAY, WEEK)):
            raise RuntimeError("3.15.3 version present but illegal XML widget views remain")
        print("PASS: 3.15.3 widget-layout patch already applied")
        return
    if gradle.count("versionCode 69") != 1 or gradle.count("versionName '3.15.2'") != 1:
        raise RuntimeError("Expected Agenda Clara 3.15.2 (versionCode 69) before layout fix")
    planned = {}
    for path in (DAY, WEEK):
        before = original[path]
        if len(re.findall(r"<View(?=\\s)", before)) != 1:
            raise RuntimeError(f"{path}: expected exactly one unsupported View divider")
        after = re.sub(r"<View(?=\\s)", "<FrameLayout", before, count=1)
        if after == before:
            raise RuntimeError(f"{path}: unable to replace divider")
        ET.fromstring(after)
        planned[path] = after
    planned[GRADLE] = gradle.replace("versionCode 69", "versionCode 70", 1).replace(
        "versionName '3.15.2'", "versionName '3.15.3'", 1
    )
    done = []
    try:
        for path, text in planned.items():
            atomic_write(path, text)
            done.append(path)
        if any(hashlib.sha256(p.read_bytes()).digest() != photo_hash[p] for p in PHOTO):
            raise RuntimeError("Photography widget assets changed unexpectedly")
    except BaseException:
        for path in reversed(done):
            atomic_write(path, original[path])
        raise
    print("PASS: 2 academic widgets now use only RemoteViews-compatible FrameLayout dividers")
    print("PASS: photography widget source/resources preserved byte-for-byte")
    print("PASS: Agenda Clara 3.15.3, versionCode 70")


if __name__ == "__main__":
    main()
