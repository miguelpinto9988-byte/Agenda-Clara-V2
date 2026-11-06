#!/usr/bin/env python3
"""Regression tests for the transactional 3.15.2 source migration."""

import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock


STAGE = Path(__file__).resolve().parent
SRC_ROOT = Path.cwd()
SYNC_REL = Path("AgendaClara/app/src/main/java/pe/agendaclara/app/AcademicWidgetSync.java")
WEEK_REL = Path("AgendaClara/app/src/main/java/pe/agendaclara/app/AcademicWeekWidget.java")
ORDER_REL = Path("AgendaClara/app/src/main/java/pe/agendaclara/app/AcademicWidgetEvaluationOrder.java")
GRADLE_REL = Path("AgendaClara/app/build.gradle")
PHOTO_RELS = [
    Path("AgendaClara/app/src/main/java/pe/agendaclara/app") / file
    for file in ("PhotoWidget.java", "PhotoConfigActivity.java", "PhotoTapActivity.java")
] + [
    Path("AgendaClara/app/src/main/res/layout/widget_photo.xml"),
    Path("AgendaClara/app/src/main/res/xml/photo_widget_info.xml"),
]

spec = importlib.util.spec_from_file_location("phase83_widget_patch", STAGE / "apply_widget_refresh_3152.py")
assert spec and spec.loader
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


class WidgetPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agenda-3152-")
        self.directory = Path(self.temp.name)
        for file in [SYNC_REL, WEEK_REL, GRADLE_REL, *PHOTO_RELS]:
            target = self.directory / file
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SRC_ROOT / file, target)
        current = (self.directory / GRADLE_REL).read_text(encoding="utf-8")
        self.assertIn("versionCode 68", current)
        self.assertIn("versionName '3.15.1'", current)
        self.previous_cwd = Path.cwd()
        os.chdir(self.directory)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.temp.cleanup()

    def photo_snapshot(self):
        return {p: (self.directory / p).read_bytes() for p in PHOTO_RELS}

    def test_success_does_not_modify_photography_and_is_idempotent(self):
        before = self.photo_snapshot()
        patcher.main()
        self.assertEqual(before, self.photo_snapshot())
        self.assertIn("versionCode 69", GRADLE_REL.read_text(encoding="utf-8"))
        self.assertEqual((STAGE / ORDER_REL.name).read_bytes(), ORDER_REL.read_bytes())
        snapshot = {p: p.read_bytes() for p in [SYNC_REL, WEEK_REL, ORDER_REL, GRADLE_REL]}
        patcher.main()
        self.assertEqual(snapshot, {p: p.read_bytes() for p in snapshot})

    def test_missing_photo_file_fails_without_mutating_application(self):
        before = SYNC_REL.read_bytes()
        PHOTO_RELS[0].unlink()
        with self.assertRaisesRegex(RuntimeError, "Missing protected photography file"):
            patcher.main()
        self.assertEqual(before, SYNC_REL.read_bytes())
        self.assertFalse(ORDER_REL.exists())

    def test_unexpected_legacy_anchor_fails_without_write(self):
        SYNC_REL.write_text("unexpected implementation", encoding="utf-8")
        before = GRADLE_REL.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "expected exactly one occurrence"):
            patcher.main()
        self.assertEqual(before, GRADLE_REL.read_bytes())
        self.assertFalse(ORDER_REL.exists())

    def test_midway_write_error_rolls_back_all_files(self):
        files = [SYNC_REL, WEEK_REL, GRADLE_REL]
        before = {file: file.read_bytes() for file in files}
        atomic = patcher._atomic_write
        count = 0

        def fail_on_second(path, data):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated disk error")
            atomic(path, data)

        with mock.patch.object(patcher, "_atomic_write", side_effect=fail_on_second):
            with self.assertRaisesRegex(OSError, "simulated disk error"):
                patcher.main()
        self.assertEqual(before, {file: file.read_bytes() for file in files})
        self.assertFalse(ORDER_REL.exists())
        self.assertNotIn("phase83-", " ".join(str(p) for p in self.directory.rglob("*.phase83-*")))


if __name__ == "__main__":
    unittest.main()
