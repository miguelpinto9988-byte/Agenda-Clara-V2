#!/usr/bin/env python3
"""Offline regressions for Android performance metrics."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("performance_qa",Path(__file__).with_name("performance_qa.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
header=("Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,"
        "HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,"
        "SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,"
        "FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted")
rows=[]
for index,ms in enumerate((10,16,20,24,30,50)):
    values=[0]*17;values[1]=1_000_000_000+index*20_000_000
    values[13]=values[1]+ms*1_000_000
    rows.append(",".join(map(str,values)))
samples=mod.frames("---PROFILEDATA---\n"+header+"\n"+"\n".join(rows)+"\n---PROFILEDATA---")
assert len(samples)==6
assert not mod.frames("no data")
assert mod.pss("TOTAL PSS: 42,500 TOTAL RSS: 55,000")==42500
assert mod.pss("  TOTAL     1120    30")==1120
result=mod.summary(samples,40000,42000,60)
assert result["frame_p50_ms"]==20.0 and result["frame_p95_ms"]==50.0
assert result["pss_delta_kib"]==2000
assert result["over_frame_budget_pct"]>50
for fn in (lambda:mod.pss("invalid"),lambda:mod.summary(samples[:2],1,2,60)):
    try:fn()
    except ValueError:pass
    else:raise AssertionError("Invalid measurements should fail")
print("PASS phase29: framestats, FPS caveats and memory PSS")
