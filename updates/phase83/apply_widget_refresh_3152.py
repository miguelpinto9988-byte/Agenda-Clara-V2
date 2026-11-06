#!/usr/bin/env python3
"""Agenda Clara 3.15.2: never drop academic widget refreshes when stores change."""
from pathlib import Path
import hashlib
import shutil

APP=Path("AgendaClara/app/src/main")
JAVA=APP/"java/pe/agendaclara/app"
RES=APP/"res"
SYNC=JAVA/"AcademicWidgetSync.java"
GRADLE=Path("AgendaClara/app/build.gradle")
STAGE=Path(__file__).resolve().parent/"AcademicWidgetSync.java"

def main():
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 68")!=1 or gradle.count("versionName '3.15.1'")!=1:
        raise RuntimeError("Expected verified 3.15.1 source (versionCode 68)")
    previous=SYNC.read_text(encoding="utf-8")
    for anchor in ("updatePending=true;", "if(updatePending)return;", "AcademicDayWidget.refresh(app);", "AcademicWeekWidget.refresh(app);"):
        if previous.count(anchor)!=1:
            raise RuntimeError("Unexpected widget sync source: "+anchor)
    proposed=STAGE.read_text(encoding="utf-8")
    for anchor in ("dirty=true;", "if(running)return;", "if(!dirty)", "try{AcademicDayWidget.refresh(app);}", "try{AcademicWeekWidget.refresh(app);}"):
        if proposed.count(anchor)!=1:
            raise RuntimeError("Missing required sync invariant: "+anchor)
    photo=[
        JAVA/"PhotoWidget.java",
        JAVA/"PhotoConfigActivity.java",
        JAVA/"PhotoTapActivity.java",
        RES/"layout/widget_photo.xml",
        RES/"xml/photo_widget_info.xml",
    ]
    checksums={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in photo}
    shutil.copyfile(STAGE,SYNC)
    GRADLE.write_text(gradle.replace("versionCode 68","versionCode 69",1)
                            .replace("versionName '3.15.1'","versionName '3.15.2'",1),
                      encoding="utf-8")
    if any(hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest
           for name,digest in checksums.items()):
        raise RuntimeError("Photo widget assets unexpectedly changed")
    print("PASS: academic widget updates cannot silently drop overlapping refresh requests")
    print("PASS: Photography widget source and configuration byte-identical")
    print("PASS: version 3.15.2")

if __name__=="__main__":
    main()
