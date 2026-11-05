#!/usr/bin/env python3
"""Android UI smoke test: import a synthetic syllabus PDF and inspect assessments."""
import re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
from reportlab.pdfgen import canvas

FILE="silabo_qa_3140.pdf"
def run(*args):
    return subprocess.check_output(["adb",*args],text=True,timeout=55).strip()
def nodes():
    run("shell","uiautomator","dump","/sdcard/syllabus.xml")
    data=run("shell","cat","/sdcard/syllabus.xml")
    return list(ET.fromstring(data[data.index("<?xml"):]).iter("node"))
def text(n):
    return (n.attrib.get("text","")+" "+n.attrib.get("content-desc","")).strip()
def find(needle):
    for n in nodes():
        if needle.casefold() not in text(n).casefold():continue
        m=re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",n.attrib.get("bounds",""))
        if m:
            x1,y1,x2,y2=map(int,m.groups())
            return (x1+x2)//2,(y1+y2)//2
    return None
def tap(needle):
    xy=find(needle)
    if xy is None:raise AssertionError("Missing "+needle+" in "+str([text(n) for n in nodes() if text(n)][:70]))
    run("shell","input","tap",str(xy[0]),str(xy[1]))
    time.sleep(1.5)
def wait(needle,count=20):
    for _ in range(count):
        if find(needle):return
        time.sleep(2)
    raise AssertionError("Timed out: "+needle)
def capture(name):
    Path("screenshots").mkdir(exist_ok=True)
    run("shell","screencap","-p","/sdcard/"+name+".png")
    subprocess.check_call(["adb","pull","/sdcard/"+name+".png","screenshots/"+name+".png"],
                          stdout=subprocess.DEVNULL)
def fixture():
    pdf=canvas.Canvas(FILE,pagesize=(595,842))
    pdf.setFont("Helvetica-Bold",17)
    pdf.drawString(40,780,"SILABO: TENDENCIAS EDUCATIVAS")
    pdf.setFont("Helvetica",12)
    for i,line in enumerate([
        "Semana | Actividad | Fecha | Peso",
        "12 | Examen oral | 18/11/2026 | 30%",
        "13 | Foro semanal | 19/11/2026 | 5%",
        "14 | Producto final | Por confirmar | 40%",
    ]):pdf.drawString(40,720-i*36,line)
    pdf.save()
fixture()
run("push",FILE,"/sdcard/Download/"+FILE)
try:
    run("shell","am","start","-n","pe.agendaclara.app/.SyllabusImportActivity")
    wait("Subir sílabo")
    tap("Subir sílabo")
    time.sleep(3)
    for _ in range(12):
        if find(FILE):
            tap(FILE);break
        for drawer in ("Show roots","Open navigation drawer"):
            if find(drawer):
                tap(drawer);break
        for folder in ("Downloads","Descargas"):
            if find(folder):
                tap(folder);break
        time.sleep(2)
    else:raise AssertionError("PDF not found in DocumentsUI")
    wait("Revisar evaluaciones",30)
    visible=[text(n) for n in nodes() if text(n)]
    assert any("Examen oral" in t for t in visible),visible[:70]
    assert any("Producto final" in t for t in visible),visible[:70]
    assert not any("Foro semanal" in t for t in visible),visible[:70]
    capture("silabo-3140-review")
    print("PASS: PDF import shows oral exam and final product; ordinary forum excluded")
except Exception:
    try:capture("silabo-3140-diagnostic")
    except Exception:pass
    raise
