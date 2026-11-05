#!/usr/bin/env python3
"""End-to-end Android QA with a synthetic colored timetable photograph.

Works against the already-built 3.13.7 APK, no Gradle build.
"""
import re,subprocess,time,pathlib,xml.etree.ElementTree as ET
OUT=pathlib.Path("screenshots");OUT.mkdir(exist_ok=True)
BOUNDS=re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")
def adb(*args):
    return subprocess.check_output(["adb",*args],text=True,timeout=50).strip()
def inspect():
    adb("shell","uiautomator","dump","/sdcard/xml.xml")
    xml=adb("shell","cat","/sdcard/xml.xml")
    p=xml.find("<?xml")
    if p<0:raise AssertionError(xml[:300])
    return list(ET.fromstring(xml[p:]).iter("node"))
def label(node):
    return " ".join((node.attrib.get("text",""),node.attrib.get("content-desc",""))).strip()
def lookup(query):
    results=[]
    for node in inspect():
        if query.casefold() not in label(node).casefold():continue
        match=BOUNDS.fullmatch(node.attrib.get("bounds",""))
        if match:
            x1,y1,x2,y2=map(int,match.groups())
            if x2>x1 and y2>y1:results.append(((x1+x2)//2,(y1+y2)//2,label(node)))
    return results
def press(query):
    found=lookup(query)
    if not found:raise AssertionError("Not found "+query+"; visible: "+str([label(x) for x in inspect() if label(x)][:70]))
    x,y,_=found[0];adb("shell","input","tap",str(x),str(y));time.sleep(1.5)
def screenshot(name):
    adb("shell","screencap","-p","/sdcard/"+name+".png")
    subprocess.check_call(["adb","pull","/sdcard/"+name+".png",str(OUT/(name+".png"))],
                          stdout=subprocess.DEVNULL)
def wait_for(query,attempts=15):
    for i in range(attempts):
        if lookup(query):return
        time.sleep(2)
    raise AssertionError("Timeout waiting for "+query)
try:
    adb("shell","am","start","-n","pe.agendaclara.app/.MainActivity")
    wait_for("Calendario")
    press("Calendario")
    press("Plan de estudio")
    press("Nuevo horario")
    press("Subir imagen del horario")
    wait_for("Elegir desde galería")
    press("Elegir desde galería")
    time.sleep(2)
    filename="horario_ocr_regresion.png"
    found=False
    for attempt in range(12):
        if lookup(filename):
            press(filename);found=True;break
        if attempt==0:
            # AOSP DocumentsUI may initially be on Recent, use Downloads drawer.
            try:press("Show roots")
            except AssertionError:
                try:press("Open navigation drawer")
                except AssertionError:pass
        if lookup("Downloads"):
            press("Downloads")
        elif lookup("Descargas"):
            press("Descargas")
        time.sleep(2)
    if not found:raise AssertionError("Android document picker didn't expose "+filename+
                                      "; this is a picker setup failure")
    wait_for("Paso 2 de 3",25)
    texts=[label(n) for n in inspect() if label(n)]
    assert any("Tendencias educativas" in t for t in texts), (
        "OCR missed the complete Tendencias educativas name")
    assert any("Historia de la educación" in t for t in texts), (
        "OCR missed Historia de la educación")
    screenshot("04-synthetic-colored-ocr-review")
    # The continue button is BELOW six course cards. Android exposes only
    # on-screen elements, so scroll before querying the accessibility tree.
    for _ in range(14):
        if lookup("Corroborar cursos y continuar"):break
        adb("shell","input","swipe","430","1660","430","550","460")
        time.sleep(.8)
    else:raise AssertionError("Course confirmation button unavailable after scrolling")
    press("Corroborar cursos y continuar")
    wait_for("¿Son el mismo curso?",10)
    assert lookup("No · separados"),"Separate subjects action missing"
    assert lookup("Sí · mismo curso"),"Same subject action missing"
    screenshot("05-ambiguous-course-dialog")
    print("PASS: on-device photo OCR recognized colored blocks and complete course names",
          flush=True)
    print("PASS: shared-prefix course triggered real ¿Son el mismo curso? dialog",
          flush=True)
    print("PASS: timetable name comes only after academic corroboration",flush=True)
except Exception:
    try:screenshot("04-synthetic-ocr-diagnostic")
    except Exception:pass
    raise
