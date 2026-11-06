#!/usr/bin/env python3
"""Check idempotent adaptive patching, rollback, release bump and privacy boundaries."""
from pathlib import Path
import importlib.util
import os
import shutil
import tempfile

ROOT=Path.cwd()
SRC=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
FILES=[SRC/"ScheduleActivity.java",Path("AgendaClara/app/build.gradle")]
PATH=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("adaptive_patch",PATH/"apply_adaptive_photo_3156.py")
module=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)

def check(ok,message):
    if not ok:raise AssertionError(message)

with tempfile.TemporaryDirectory(prefix="agenda-adaptive-") as temp:
    where=Path(temp)
    for file in FILES:
        dest=where/file;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/file,dest)
    before={p:(where/p).read_bytes() for p in FILES}
    source=Path.cwd()
    try:
        os.chdir(where)
        try:
            module.main()
            check((SRC/"ScheduleAdaptiveRules.java").exists(),"Missing pure decision rules")
            check((SRC/"ScheduleAdaptiveMemory.java").exists(),"Missing private memory storage")
            patched=(SRC/"ScheduleActivity.java").read_text(encoding="utf-8")
            check(patched.count("commitAdaptiveFeedback();")==1,"Must persist feedback only at import completion")
            check(patched.count("showAdaptiveMemorySettings()")>=1,"Missing memory management UI")
            check("versionCode 73" in Path("AgendaClara/app/build.gradle").read_text(),
                  "Wrong app version")
            snapshot={p:p.read_bytes() for p in [
                *FILES,SRC/"ScheduleAdaptiveRules.java",SRC/"ScheduleAdaptiveMemory.java"
            ]}
            module.main()
            check(snapshot=={p:p.read_bytes() for p in snapshot},
                  "Re-running patch should not modify sources")
            check(not list(where.rglob(".phase87-*")),"Leftover staging files")
        finally:os.chdir(source)
    except:raise
with tempfile.TemporaryDirectory(prefix="agenda-adaptive-invalid-") as temp:
    where=Path(temp)
    for file in FILES:
        dest=where/file;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/file,dest)
    activity=where/FILES[0]
    activity.write_text("not the expected ScheduleActivity source",encoding="utf-8")
    old_version=(where/FILES[1]).read_bytes()
    source=Path.cwd()
    try:
        os.chdir(where)
        try:module.main()
        except RuntimeError:pass
        else:raise AssertionError("Patch must reject missing source anchors")
        check(FILES[1].read_bytes()==old_version,
              "Version changed after an incompatible source was rejected")
    finally:os.chdir(source)
print("PASS: adaptive patch applied twice without duplicating code")
print("PASS: incompatible source rejected without partial Android version bump")
print("PASS: private local decision storage, clear/pause UI and post-save learning wired")
