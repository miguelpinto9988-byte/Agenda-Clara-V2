#!/usr/bin/env python3
"""Android 15 smoke for widget companion: chooser, manual edit and IME restoration."""
import re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
P="pe.agendaclara.app"
D=Path("screenshots");D.mkdir(exist_ok=True)
def adb(*args,output=False):
    result=subprocess.run(["adb",*args],check=True,capture_output=output)
    return result.stdout if output else b""
def dump():
    adb("shell","uiautomator","dump","/sdcard/widget_activity.xml")
    return ET.fromstring(adb("exec-out","cat","/sdcard/widget_activity.xml",output=True))
def nodes(root):
    return list(root.iter("node"))
def match(root,label):
    return next((x for x in nodes(root) if label in (x.get("text","")+" "+x.get("content-desc",""))),None)
def touch(x):
    b=[int(v) for v in re.findall(r"\d+",x.get("bounds",""))]
    if len(b)!=4:raise AssertionError("Missing widget element bounds")
    adb("shell","input","tap",str((b[0]+b[2])//2),str((b[1]+b[3])//2))
def ensure(root,label):
    node=match(root,label)
    if node is None:raise AssertionError("Missing "+label)
    return node
# run-as launches a non-exported Activity as its own debug app UID.
adb("shell","am","force-stop",P)
adb("shell","run-as",P,"am","start","-W","-n",P+"/.WidgetTaskActivity",
    "-a","pe.agendaclara.app.WIDGET_CREATE")
time.sleep(4)
root=dump()
ensure(root,"Nueva tarea");ensure(root,"Tarea rápida por voz");normal=ensure(root,"Tarea normal")
D.joinpath("30-widget-selector-flotante.png").write_bytes(adb("exec-out","screencap","-p",output=True))
touch(normal);time.sleep(3)
root=dump();ensure(root,"Tarea normal");ensure(root,"Guardar tarea")
edits=[n for n in nodes(root) if n.get("class","").endswith("EditText")]
if not edits:raise AssertionError("Normal floating editor has no input fields")
outer=next(n for n in nodes(root) if n.get("bounds"))
def height(n):
    b=[int(v) for v in re.findall(r"\d+",n.get("bounds",""))]
    return b[3]-b[1]
before=height(outer)
touch(edits[0]);time.sleep(3)
opened=dump();during=height(next(n for n in nodes(opened) if n.get("bounds")))
adb("shell","input","text","Proyecto%sparticipacion")
adb("shell","input","keyevent","4");time.sleep(4)
closed=dump();after=height(next(n for n in nodes(closed) if n.get("bounds")))
if after<before-110:raise AssertionError(f"Widget editor did not re-expand {before}/{during}/{after}")
if match(closed,"Proyecto") is None:raise AssertionError("Text lost after hiding IME")
D.joinpath("31-widget-tarea-normal-restaurada.png").write_bytes(adb("exec-out","screencap","-p",output=True))
print("PASS floating widget chooser + normal editor + keyboard restoration "+str((before,during,after)))
