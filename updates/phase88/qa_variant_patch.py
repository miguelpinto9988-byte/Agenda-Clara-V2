#!/usr/bin/env python3
"""3.15.7 patch regression: transactional, idempotent and widget-safe."""
from pathlib import Path
import importlib.util
import os
import shutil
import tempfile

ROOT=Path.cwd()
STAGE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("phase88",STAGE/"apply_adaptive_variants_3157.py")
assert spec and spec.loader
patch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
SOURCE=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
NEEDED=[
    SOURCE/"ScheduleActivity.java",
    Path("AgendaClara/app/build.gradle"),
    *patch.PROTECTED
]

def check(state,message):
    if not state:raise AssertionError(message)

def sandbox():
    path=Path(tempfile.mkdtemp(prefix="agenda-variant-"))
    for file in NEEDED:
        dest=path/file
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/file,dest)
    return path

root=sandbox()
previous=Path.cwd()
try:
    os.chdir(root)
    original={f:f.read_bytes() for f in patch.PROTECTED}
    patch.main()
    check("versionCode 74" in patch.GRADLE.read_text(),
        "Expected app version 3.15.7")
    code=patch.ACTIVITY.read_text()
    check("ScheduleAdaptiveVariants.suggest(adaptiveHistory,s.course)" in code,
        "Variant proposal must be shown in photo review")
    check("reviewLearnedVariant(s,proposal)" in code,
        "User must be able to review the proposal")
    check("rememberAfterSave(original,canonical,true,canonical)" in code,
        "Only accepted proposals can become learned merges")
    check("rememberAfterSave(original,canonical,false,\"\")" in code,
        "Explicit rejection needs to be remembered")
    check("if(renamed<1)" in code,"Review must verify it renamed a candidate")
    check("pendingAdaptive" in code and "commitAdaptiveFeedback()" in code,
        "Confirmed decisions must be saved after successful import")
    check("declinedVariantSuggestions.clear()" in code,
        "Declined suggestions must be reset for each new photo")
    check({f:f.read_bytes() for f in patch.PROTECTED}==original,
        "Photography widget assets changed")
    snapshot={p:p.read_bytes() for p in
        (patch.ACTIVITY,patch.GRADLE,patch.VARIANTS)}
    patch.main()
    check(snapshot=={p:p.read_bytes() for p in snapshot},
        "Repeated patch changed sources")
finally:
    os.chdir(previous)
    shutil.rmtree(root)

bad=sandbox()
try:
    os.chdir(bad)
    patch.ACTIVITY.write_text("outdated code",encoding="utf-8")
    old=patch.GRADLE.read_bytes()
    try:patch.main()
    except RuntimeError:pass
    else:raise AssertionError("Incompatible activity must be rejected")
    check(patch.GRADLE.read_bytes()==old,"Gradle changed despite patch failure")
    check(not patch.VARIANTS.exists(),"Created new class on rejected patch")
finally:
    os.chdir(previous)
    shutil.rmtree(bad)

print("PASS: variant suggestions added only to photo review with consent buttons")
print("PASS: explicit accept/reject feedback survives only committed imports")
print("PASS: version bump is idempotent and incompatible projects are not changed")
print("PASS: photography widget remains byte-for-byte unchanged")
