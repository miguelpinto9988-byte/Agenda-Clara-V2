#!/usr/bin/env python3
"""Entrega A: calendario con dos pestañas y registro independiente de 10 horarios.
No modifica ScheduleDatabase, tareas, notificaciones, ni la clave de firma.
"""
from pathlib import Path
import shutil
ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE=Path(__file__).resolve().parent
MAIN=ROOT/"MainActivity.java"
GRADLE=Path("AgendaClara/app/build.gradle")
NAMES=("AcademicSchedules.java","CalendarStudyPanel.java","CalendarStudyTabs.java")
BEFORE="else if(page==1)calendarPage();"
AFTER="else if(page==1)CalendarStudyTabs.render(this);"

def run():
    if not MAIN.is_file():raise RuntimeError("Primero reconstruir las fuentes 3.13.2")
    source=MAIN.read_text(encoding="utf-8")
    if AFTER not in source:
        if source.count(BEFORE)!=1:
            raise RuntimeError("Anclaje de Calendario distinto; detener sin modificar")
        source=source.replace(BEFORE,AFTER,1)
    for name in NAMES:
        desired=(HERE/name).read_text(encoding="utf-8")
        target=ROOT/name
        if target.exists() and target.read_text(encoding="utf-8")!=desired:
            raise RuntimeError("Archivo existente diferente: "+name)
    gradle=GRADLE.read_text(encoding="utf-8")
    if "versionCode 59" in gradle and "versionName '3.13.3'" in gradle:
        pass
    elif gradle.count("versionCode 58")==1 and gradle.count("versionName '3.13.2'")==1:
        gradle=gradle.replace("versionCode 58","versionCode 59",1).replace(
            "versionName '3.13.2'","versionName '3.13.3'",1)
    else:raise RuntimeError("Versión Android desconocida")
    MAIN.write_text(source,encoding="utf-8")
    for name in NAMES:shutil.copyfile(HERE/name,ROOT/name)
    GRADLE.write_text(gradle,encoding="utf-8")
    print("PASS Entrega A inicial: pestañas Calendario/Plan de estudio; 10 horarios; categorías y cursos")
if __name__=="__main__":run()
