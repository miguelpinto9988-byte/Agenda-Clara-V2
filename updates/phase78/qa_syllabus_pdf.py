#!/usr/bin/env python3
"""End-to-end Android 15 QA: PDF -> matching course (two schedules) -> tasks.

Uses only synthetic academic data. No private user documents. Does not build APK.
"""
import json
import pathlib
import re
import sqlite3
import subprocess
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

PACKAGE="pe.agendaclara.app"
OUT=pathlib.Path("screenshots")
OUT.mkdir(exist_ok=True)
BOUNDS=re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

def adb(*args,timeout=45):
    return subprocess.check_output(["adb",*args],text=True,timeout=timeout).strip()

def screen():
    adb("shell","uiautomator","dump","/sdcard/window.xml")
    raw=adb("shell","cat","/sdcard/window.xml")
    idx=raw.find("<?xml")
    if idx<0:raise AssertionError("Android UI hierarchy unavailable: "+raw[:300])
    return list(ET.fromstring(raw[idx:]).iter("node"))

def label(node):
    return " ".join((node.attrib.get("text",""),node.attrib.get("content-desc",""))).strip()

def find(query):
    results=[]
    for item in screen():
        if query.casefold() not in label(item).casefold():continue
        m=BOUNDS.fullmatch(item.attrib.get("bounds",""))
        if m:
            x1,y1,x2,y2=map(int,m.groups())
            if x2>x1 and y2>y1:results.append(((x1+x2)//2,(y1+y2)//2,label(item)))
    return results

def click(query):
    rows=find(query)
    if not rows:
        raise AssertionError(query+" not visible. UI: "+
            str([label(node) for node in screen() if label(node)][:90]))
    x,y,_=rows[0]
    adb("shell","input","tap",str(x),str(y))
    time.sleep(1.6)

def wait(query,attempts=18):
    for attempt in range(attempts):
        if find(query):return
        time.sleep(2)
    raise AssertionError("Timeout "+query+"; UI: "+
        str([label(item) for item in screen() if label(item)][:70]))

def swipe():
    dimensions=adb("shell","wm","size")
    match=re.search(r"(\d+)x(\d+)",dimensions)
    width,height=(map(int,match.groups()) if match else (1080,2400))
    x=width//2
    adb("shell","input","swipe",str(x),str(int(height*.80)),
        str(x),str(int(height*.27)),"430")
    time.sleep(.8)

def scroll_click(needle,max_swipes=20):
    for _ in range(max_swipes):
        if find(needle):click(needle);return
        swipe()
    raise AssertionError("Could not locate after scrolling: "+needle)

def capture(name):
    adb("shell","screencap","-p",f"/sdcard/{name}.png")
    subprocess.check_call(["adb","pull",f"/sdcard/{name}.png",
                           str(OUT/(name+".png"))],stdout=subprocess.DEVNULL)

def set_preferences(name,data):
    entries="".join("<string name=\""+escape(k)+"\">"+escape(v)+"</string>"
                    for k,v in data.items())
    content="<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\" ?><map>"+\
        entries+"</map>"
    mkdir=subprocess.run(["adb","shell","run-as",PACKAGE,
                          "mkdir","-p","shared_prefs"],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if mkdir.returncode:
        raise AssertionError("Creating test preferences: "+mkdir.stderr)
    # adb shell concatenates argv. Quote the entire sh -c program explicitly
    # or Android sh interprets 'mkdir' as a command missing its arguments.
    program="'cat > shared_prefs/"+name+".xml'"
    proc=subprocess.run(["adb","shell","run-as",PACKAGE,"sh","-c",program],
        input=content,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        timeout=30)
    if proc.returncode:raise AssertionError("Seeding academic profiles: "+proc.stderr)

def seed_two_profiles():
    profiles=[
        {"id":"syllabus-qa-day","name":"Educación 2026","category":"Educación 2026",
         "courses":["Tendencias educativas"],"legacy":False},
        {"id":"syllabus-qa-night","name":"Noche 2026","category":"Noche 2026",
         "courses":["Tendencias educativas"],"legacy":False},
    ]
    set_preferences("agenda_clara_academic_schedules_v1",
                    {"profiles":json.dumps(profiles,ensure_ascii=False),
                     "selected":"syllabus-qa-day"})
    categories=[
        {"name":"Educación 2026","color":-11206158,"icon":"other"},
        {"name":"Noche 2026","color":-11206158,"icon":"other"},
    ]
    set_preferences("settings",{"user_categories_v2":json.dumps(categories,ensure_ascii=False)})

def get_db(name):
    result=subprocess.run(["adb","exec-out","run-as",PACKAGE,"cat","databases/"+name],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    if result.returncode or len(result.stdout)<100:
        raise AssertionError("Cannot read SQLite "+name+": "+result.stderr.decode("utf-8","replace"))
    local=OUT/name
    local.write_bytes(result.stdout)
    for suffix in ("-wal","-shm"):
        extra=subprocess.run(["adb","exec-out","run-as",PACKAGE,"cat","databases/"+name+suffix],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
        if extra.returncode==0 and extra.stdout:
            (OUT/(name+suffix)).write_bytes(extra.stdout)
    return local

def verify_tasks():
    sqlite_path=get_db("agenda_clara.db")
    with sqlite3.connect(str(sqlite_path)) as db:
        tasks=db.execute(
            "SELECT title, category, due, notes, source FROM tasks WHERE source LIKE 'Sílabo%'"
        ).fetchall()
    assert len(tasks)==4,f"Expected 4 exams/finals, got {len(tasks)}: {tasks}"
    assert all(category=="Educación 2026" for _,category,_,_,_ in tasks),tasks
    assert sum(1 for _,_,due,_,_ in tasks if due==0)==3, \
        f"Three week/range-only events must not have invented dates: {tasks}"
    assert sum(1 for _,_,due,_,_ in tasks if due>0)==1, \
        "Exactly one known exam date should schedule reminders"
    assert all("Tendencias educativas" in notes for _,_,_,notes,_ in tasks)
    assert all("Entrega de informe semanal" not in title for title,_,_,_,_ in tasks)
    linked=get_db("academic_task_links.db")
    with sqlite3.connect(str(linked)) as db:
        rows=db.execute("SELECT profile_id,course FROM links").fetchall()
    assert len(rows)==4 and all(profile=="syllabus-qa-day" and
        course=="Tendencias educativas" for profile,course in rows),rows
    print("PASS: 4 evaluation tasks linked to correct timetable UUID, not duplicate profile",
          flush=True)
    print("PASS: 3 week/range events saved WITHOUT guessed dates and alarms",
          flush=True)
    print("PASS: regular weekly delivery omitted",flush=True)
    # Remove temporary SQLite copies from screenshots artifact.
    for name in ("agenda_clara.db","agenda_clara.db-wal","agenda_clara.db-shm",
                 "academic_task_links.db","academic_task_links.db-wal",
                 "academic_task_links.db-shm"):
        (OUT/name).unlink(missing_ok=True)

try:
    adb("shell","am","force-stop",PACKAGE)
    seed_two_profiles()
    adb("shell","am","start","-n",PACKAGE+"/.MainActivity")
    wait("Calendario")
    click("Calendario")
    click("Plan de estudio")
    click("Subir sílabo")
    time.sleep(2)
    filename="silabo_tendencias_2026.pdf"
    seen=False
    for attempt in range(10):
        if find(filename):
            click(filename);seen=True;break
        if attempt==0:
            try:click("Show roots")
            except AssertionError:
                try:click("Open navigation drawer")
                except AssertionError:pass
        if find("Downloads"):click("Downloads")
        elif find("Descargas"):click("Descargas")
        time.sleep(1.5)
    if not seen:raise AssertionError("PDF not found in document picker")
    wait("¿A qué curso corresponde este sílabo?",25)
    assert find("Tendencias educativas · Educación 2026"), \
        "Syllabus did not match correct existing profile"
    assert find("Tendencias educativas · Noche 2026"), \
        "Duplicate course in another timetable should be offered for explicit choice"
    capture("01-syllabus-course-choices")
    click("Tendencias educativas · Educación 2026")
    wait("Eventos detectados: 4")
    capture("02-syllabus-events")
    labels=" ".join(label(node) for node in screen())
    assert "EXAMEN ORAL" in labels,labels[:800]
    assert "Semana 12" in labels,labels[:800]
    scroll_click("Confirmar e incorporar al curso")
    wait("Confirmar 4 evaluaciones")
    capture("03-syllabus-confirmation")
    click("Guardar en este curso")
    wait("Evaluaciones incorporadas")
    capture("04-syllabus-saved")
    adb("shell","am","force-stop",PACKAGE)
    verify_tasks()
except Exception:
    try:capture("00-syllabus-qa-error")
    except Exception:pass
    raise
