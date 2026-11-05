#!/usr/bin/env python3
"""Android 15 UI regression for user's screenshot: Nuevo horario should not name-first.

Called exclusively by the Phase 75 Android emulator job after the APK is built.
This test actively taps Calendario > Plan de estudio > Nuevo horario, verifies
the method chooser, then checks the first screen of BOTH creation methods.
"""
import pathlib
import re
import subprocess
import time
import xml.etree.ElementTree as ET

OUT=pathlib.Path("screenshots")
OUT.mkdir(exist_ok=True)
BOUNDS=re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

def adb(*args):
    return subprocess.check_output(["adb",*args],text=True,timeout=40).strip()

def hierarchy():
    adb("shell","uiautomator","dump","/sdcard/window.xml")
    raw=adb("shell","cat","/sdcard/window.xml")
    start=raw.find("<?xml")
    if start<0:raise AssertionError("Android did not produce the UI XML")
    return ET.fromstring(raw[start:])

def nodes():
    return list(hierarchy().iter("node"))

def label(node):
    return " ".join([node.attrib.get("text",""),node.attrib.get("content-desc","")]).strip()

def find(needle,prefer="first"):
    choices=[]
    for node in nodes():
        text=label(node)
        if needle.casefold() not in text.casefold():continue
        match=BOUNDS.fullmatch(node.attrib.get("bounds",""))
        if match is None:continue
        x1,y1,x2,y2=map(int,match.groups())
        if x2<=x1 or y2<=y1:continue
        choices.append(((x1+x2)//2,(y1+y2)//2,(y1,y2),text))
    if not choices:
        summary=[label(n) for n in nodes() if label(n)]
        raise AssertionError(f"Could not find {needle!r}; UI: {summary[:90]}")
    if prefer=="lowest":choices.sort(key=lambda x:x[1],reverse=True)
    if prefer=="highest":choices.sort(key=lambda x:x[1])
    return choices[0]

def click(needle,prefer="first"):
    x,y,*_=find(needle,prefer)
    adb("shell","input","tap",str(x),str(y))
    time.sleep(1.5)

def require(needle):
    return find(needle)

def absent(needle):
    try:find(needle)
    except AssertionError:return
    raise AssertionError("Premature/forbidden dialog visible: "+needle)

def shot(name):
    adb("shell","screencap","-p",f"/sdcard/{name}.png")
    subprocess.check_call(["adb","pull",f"/sdcard/{name}.png",str(OUT/(name+".png"))],
                          stdout=subprocess.DEVNULL,timeout=40)

def alive():
    if not adb("shell","pidof","pe.agendaclara.app"):
        raise AssertionError("Agenda Clara process exited unexpectedly")

time.sleep(5)
alive()
click("Calendario",prefer="lowest")
click("Plan de estudio",prefer="highest")
require("Nuevo horario")
click("Nuevo horario")
require("¿Cómo crearás tu horario?")
require("Subir imagen del horario")
require("Agregar cursos manualmente")
absent("Confirma el nombre que identificará")
shot("01-choose-creation-method")

click("Subir imagen del horario")
alive()
require("Selecciona o toma una foto")
require("Elegir desde galería")
absent("Escribe el nombre del horario")
shot("02-photo-first-no-title")

# Android back finishes ScheduleActivity and returns to Calendario > Plan de estudio.
adb("shell","input","keyevent","4")
time.sleep(2)
alive()
require("Nuevo horario")
click("Nuevo horario")
require("¿Cómo crearás tu horario?")
click("Agregar cursos manualmente")
alive()
require("Cursos del nuevo horario")
require("Agregar una clase manualmente")
absent("Escribe el nombre del horario")
shot("03-manual-courses-first")

print("PASS UI: real Nuevo horario button opens METHOD dialog, not title input")
print("PASS UI: photo path starts with image selection and no premature name")
print("PASS UI: manual path starts with courses and no premature name")
print("PASS UI: Android process survived both navigation paths")
