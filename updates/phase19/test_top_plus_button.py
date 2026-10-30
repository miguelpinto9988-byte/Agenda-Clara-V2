#!/usr/bin/env python3
"""Regression checks for the approved native top-right add button."""
from pathlib import Path
import base64
import importlib.util
import struct
import zlib

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("plus_patch", HERE / "apply_top_plus_button.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

sample = "class Main {\n" + patch.ANCHOR + " else if(page==1)calendarPage();\n}"
changed = patch.integrate(sample)
assert changed.count("TopPlusButtonMotion.install(this)") == 1
assert changed.count("else if(page==1)calendarPage();") == 1
assert changed.index("TopPlusButtonMotion.install(this)") < changed.index(patch.ANCHOR)
for sample_bad in ("class Main {}", patch.ANCHOR * 2, changed):
    try:
        patch.integrate(sample_bad)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Unsafe or repeated migration should be rejected")

main = patch.SOURCE.read_text(encoding="utf-8")
assert main.count("TopPlusButtonMotion.install(this)") == 1
assert main.count(patch.ANCHOR) == 1
# Verify the exact original add-task button still opens the existing editor.
assert 'setTag("new_task_button")' in main
assert '()->openEditor(-1,null,null)' in main
java = patch.MOTION.read_text(encoding="utf-8")
assert "setOnClickListener(" not in java
assert "setOnTouchListener(" not in java
assert "performClick(" not in java
assert "setStateListAnimator(motion)" in java
assert "state_pressed" in java
assert 'findViewWithTag("new_task_button")' in java
assert "areAnimatorsEnabled()" in java
assert "getContentDescription" in java
png = patch.RESOURCE.read_bytes()
original = base64.b64decode((HERE / "icon_top_plus.b64").read_text().strip(), validate=True)
assert png == original
assert png.startswith(b"\x89PNG\r\n\x1a\n")
assert struct.unpack(">II", png[16:24]) == (144, 144)
offset = 8
while offset < len(png):
    length = int.from_bytes(png[offset:offset+4], "big")
    tag = png[offset+4:offset+8]
    data = png[offset+8:offset+8+length]
    stored_crc = int.from_bytes(png[offset+8+length:offset+12+length], "big")
    assert zlib.crc32(tag + data) & 0xffffffff == stored_crc, "Corrupt PNG chunk"
    offset += 12 + length
assert offset == len(png)
print("PASS: approved PNG, native motion, and original click path retained")
