#!/usr/bin/env python3
"""Apply the validated Agenda Clara 3.15.2 widget refresh and evaluation-order fixes.

The patch is idempotent on an already-patched source tree, checks source anchors
before any writes and rolls back all changed files if an update fails. It does
not modify the photography widget or any stored user data.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import tempfile

APP = Path("AgendaClara/app/src/main")
JAVA = APP / "java/pe/agendaclara/app"
RES = APP / "res"
GRADLE = Path("AgendaClara/app/build.gradle")
STAGE = Path(__file__).resolve().parent

LEGACY_SYNC_ANCHORS = (
    "updatePending=true;",
    "if(updatePending)return;",
    "AcademicDayWidget.refresh(app);",
    "AcademicWeekWidget.refresh(app);",
)
LEGACY_WEEK_ANCHORS = (
    "for(String course:distinctCourses.values())",
    "AcademicWidgetRepository.linkedTasks(c,p.id,course,true)",
    "if(exams>=4){hiddenExams++;continue;}",
)
STAGED_FILES = {
    JAVA / "AcademicWidgetSync.java": STAGE / "AcademicWidgetSync.java",
    JAVA / "AcademicWeekWidget.java": STAGE / "AcademicWeekWidget.java",
    JAVA / "AcademicWidgetEvaluationOrder.java": STAGE / "AcademicWidgetEvaluationOrder.java",
}
PHOTO_FILES = (
    JAVA / "PhotoWidget.java",
    JAVA / "PhotoConfigActivity.java",
    JAVA / "PhotoTapActivity.java",
    RES / "layout/widget_photo.xml",
    RES / "xml/photo_widget_info.xml",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_single_anchors(source: str, anchors: tuple[str, ...], label: str) -> None:
    for anchor in anchors:
        if source.count(anchor) != 1:
            raise RuntimeError(f"{label}: expected exactly one occurrence of {anchor!r}")


def _atomic_write(path: Path, data: bytes) -> None:
    """Write in the destination directory and replace without leaving partial files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{path.name}.phase83-", dir=path.parent, delete=False
        ) as temporary:
            temp_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        temp_path.chmod(mode)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _planned_writes() -> dict[Path, bytes]:
    gradle = GRADLE.read_text(encoding="utf-8")
    for path in PHOTO_FILES:
        if not path.is_file():
            raise RuntimeError(f"Missing protected photography file: {path}")
    if all(token in gradle for token in ("versionCode 69", "versionName '3.15.2'")):
        return {}
    if gradle.count("versionCode 68") != 1 or gradle.count("versionName '3.15.1'") != 1:
        raise RuntimeError("Requires reconstructed Agenda Clara 3.15.1 (versionCode 68)")
    sync = (JAVA / "AcademicWidgetSync.java").read_text(encoding="utf-8")
    week = (JAVA / "AcademicWeekWidget.java").read_text(encoding="utf-8")
    _assert_single_anchors(sync, LEGACY_SYNC_ANCHORS, "AcademicWidgetSync")
    _assert_single_anchors(week, LEGACY_WEEK_ANCHORS, "AcademicWeekWidget")
    if JAVA.joinpath("AcademicWidgetEvaluationOrder.java").exists():
        raise RuntimeError("The evaluation-order class already exists; refusing to overwrite")
    files = {target: staged.read_bytes() for target, staged in STAGED_FILES.items()}
    new_sync = files[JAVA / "AcademicWidgetSync.java"].decode("utf-8")
    new_week = files[JAVA / "AcademicWeekWidget.java"].decode("utf-8")
    new_order = files[JAVA / "AcademicWidgetEvaluationOrder.java"].decode("utf-8")
    _assert_single_anchors(
        new_sync,
        ("dirty=true;", "if(running)return;", "if(!dirty)",
         "try{AcademicDayWidget.refresh(app);}",
         "try{AcademicWeekWidget.refresh(app);}"),
        "staged AcademicWidgetSync",
    )
    _assert_single_anchors(
        new_week,
        ("AcademicWidgetEvaluationOrder.ordered(orderedEntries,startOfToday)",
         'dateLabel="Vencida · "+dateLabel'),
        "staged AcademicWeekWidget",
    )
    _assert_single_anchors(
        new_order, ("class AcademicWidgetEvaluationOrder", "public static List<Entry> ordered"),
        "staged evaluation sorter",
    )
    files[GRADLE] = (
        gradle.replace("versionCode 68", "versionCode 69", 1)
              .replace("versionName '3.15.1'", "versionName '3.15.2'", 1)
    ).encode("utf-8")
    return files


def main() -> None:
    plan = _planned_writes()
    photo_before = {path: _digest(path) for path in PHOTO_FILES}
    if not plan:
        gradle = GRADLE.read_text(encoding="utf-8")
        if gradle.count("versionCode 69") != 1 or gradle.count("versionName '3.15.2'") != 1:
            raise RuntimeError("Conflicting installed Android version")
        if any(not target.is_file() or target.read_bytes() != staged.read_bytes()
               for target, staged in STAGED_FILES.items()):
            raise RuntimeError("Version 3.15.2 present but widget files do not match staged version")
        print("PASS: 3.15.2 patch already installed; no files changed")
        return
    originals: dict[Path, bytes | None] = {
        path: path.read_bytes() if path.exists() else None for path in plan
    }
    modified = []
    try:
        for path, data in plan.items():
            _atomic_write(path, data)
            modified.append(path)
        if any(_digest(path) != sha for path, sha in photo_before.items()):
            raise RuntimeError("Photography widget resources unexpectedly changed")
    except BaseException:
        for path in reversed(modified):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                _atomic_write(path, original)
        raise
    print("PASS: concurrent widget refresh preserved and evaluations ordered across courses")
    print("PASS: five photography widget source/resources hashes unchanged")
    print("PASS: prepared version 3.15.2 (versionCode 69)")


if __name__ == "__main__":
    main()
