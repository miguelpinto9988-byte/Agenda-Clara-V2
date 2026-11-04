#!/usr/bin/env python3
"""Entrega A (sin APK): migración, pestañas, perfiles, clases, OCR y categorías.
Ejecutar tras phase70. Aborta ante fuentes ajenas a la versión 3.13.2 esperada.
"""
from pathlib import Path
import shutil
from patch_android_ui import transform_main,transform_schedule

ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE=Path(__file__).resolve().parent
GRADLE=Path("AgendaClara/app/build.gradle")
STAGED=("AcademicSchedules.java","CalendarStudyPanel.java","CalendarStudyTabs.java",
        "ScheduleTitleParser.java","ScheduleEntry.java","ScheduleDatabase.java",
        "ScheduleBackup.java")

def run():
    main_file=ROOT/"MainActivity.java"
    schedule_file=ROOT/"ScheduleActivity.java"
    if not main_file.is_file() or not schedule_file.is_file():
        raise RuntimeError("Reconstruye Agenda Clara 3.13.2 antes de la Entrega A")
    for name in STAGED:
        original=ROOT/name
        expected=(HERE/name).read_text(encoding="utf-8")
        if original.exists() and original.read_text(encoding="utf-8")!=expected:
            # Only ScheduleEntry/Database are replaced, due to SQLite v1->v2.
            if name=="ScheduleEntry.java":
                old=original.read_text(encoding="utf-8")
                if "public final class ScheduleEntry" not in old or "scheduleId" in old:
                    raise RuntimeError("ScheduleEntry cambiado; migración no aplicada")
            elif name=="ScheduleDatabase.java":
                old=original.read_text(encoding="utf-8")
                if 'super(c,"class_schedule.db",null,1)' not in old:
                    raise RuntimeError("ScheduleDatabase cambiado; migración no aplicada")
            elif name=="ScheduleBackup.java":
                old=original.read_text(encoding="utf-8")
                if "class ScheduleBackup" not in old or '"schema",1' not in old:
                    raise RuntimeError("ScheduleBackup cambiado; migración no aplicada")
            else:
                raise RuntimeError("Archivo inesperado: "+name)
    main=transform_main(main_file.read_text(encoding="utf-8"))
    schedule=transform_schedule(schedule_file.read_text(encoding="utf-8"))
    gradle=GRADLE.read_text(encoding="utf-8")
    if "versionCode 59" in gradle and "versionName '3.13.3'" in gradle:
        pass
    elif gradle.count("versionCode 58")==1 and gradle.count("versionName '3.13.2'")==1:
        gradle=gradle.replace("versionCode 58","versionCode 59",1).replace(
            "versionName '3.13.2'","versionName '3.13.3'",1)
    else:raise RuntimeError("Versión Android inesperada")
    for name in STAGED:shutil.copyfile(HERE/name,ROOT/name)
    main_file.write_text(main,encoding="utf-8")
    schedule_file.write_text(schedule,encoding="utf-8")
    GRADLE.write_text(gradle,encoding="utf-8")
    print("PASS: Entrega A integrada a fuentes: 10 horarios aislados, SQLite v2, OCR y categorías")
    print("NO APK: esta fase realiza solo una transformación de código fuente")

if __name__=="__main__":run()
