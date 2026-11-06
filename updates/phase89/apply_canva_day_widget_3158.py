#!/usr/bin/env python3
"""Install approved PNG-first Canva widget while preserving all other providers."""
from pathlib import Path
import hashlib
import os
import tempfile

STAGE=Path(__file__).resolve().parent
MAIN=Path("AgendaClara/app/src/main")
JAVA=MAIN/"java/pe/agendaclara/app"
RES=MAIN/"res"
GRADLE=Path("AgendaClara/app/build.gradle")
PROTECTED=[
    JAVA/"PhotoWidget.java",
    JAVA/"AcademicWeekWidget.java",
    RES/"layout/widget_academic_week.xml",
    RES/"layout/widget_photo.xml",
    RES/"layout/widget_tasks.xml",
]
SHAPES={
 "ac_day_shell":("#EFE3FC","#D7C4F5",22),
 "ac_day_shell_dark":("#31284D","#52406C",22),
 "ac_day_card_lilac":("#FDF7FF","#E8CDF9",17),
 "ac_day_card_mint":("#EFFBF9","#B8ECE7",17),
 "ac_day_card_lilac_dark":("#4C3E62","#776795",17),
 "ac_day_card_mint_dark":("#294B51","#47828A",17),
 "ac_day_header_clip":("#F8DBF2","#DDB7F1",16),
 "ac_day_header_panel":("#C9FFF6F9","#A1F8F2FF",14),
 "ac_day_accent_lilac":("#A457EF","#A457EF",3),
 "ac_day_accent_mint":("#44E2B1","#44E2B1",3),
}

def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    mode=path.stat().st_mode&0o777 if path.exists() else 0o644
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix=".acday-",
                                         delete=False) as f:
            temporary=Path(f.name)
            f.write(data);f.flush();os.fsync(f.fileno())
        temporary.chmod(mode)
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)

def files():
    source={
        JAVA/"AcademicDayWidget.java":STAGE/"AcademicDayWidget.java",
        JAVA/"AcademicWidgetTheme.java":STAGE/"AcademicWidgetTheme.java",
        JAVA/"AcademicDayWidgetData.java":STAGE/"AcademicDayWidgetData.java",
        RES/"layout/widget_academic_day.xml":STAGE/"widget_academic_day.xml",
    }
    for image in sorted((STAGE/"assets").glob("ac_day_*.png")):
        source[RES/"drawable-nodpi"/image.name]=image
    if len([f for f in source if f.suffix==".png"])!=9:
        raise RuntimeError("All nine approved PNGs are required")
    result={path:src.read_bytes() for path,src in source.items()}
    for name,(bg,border,radius) in SHAPES.items():
        xml=f'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
<solid android:color="{bg}"/>
<corners android:radius="{radius}dp"/>
<stroke android:width="1dp" android:color="{border}"/>
</shape>
'''
        result[RES/"drawable"/(name+".xml")]=xml.encode()
    result[RES/"xml/widget_academic_day_info.xml"]=b'''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
android:minWidth="270dp" android:minHeight="235dp"
android:minResizeWidth="200dp" android:minResizeHeight="170dp"
android:targetCellWidth="4" android:targetCellHeight="4"
android:resizeMode="horizontal|vertical" android:updatePeriodMillis="1800000"
android:initialLayout="@layout/widget_academic_day"
android:previewLayout="@layout/widget_academic_day"
android:configure="pe.agendaclara.app.AcademicWidgetSettingsActivity"
android:widgetFeatures="reconfigurable"
android:description="@string/academic_day_widget_description"
android:widgetCategory="home_screen"/>
'''
    return result

def main():
    gradle=GRADLE.read_text(encoding="utf-8")
    changes=files()
    for p in PROTECTED:
        if not p.is_file():raise RuntimeError("Protected widget missing: "+str(p))
    if "versionCode 75" in gradle and "versionName '3.15.8'" in gradle:
        if any(not p.exists() or p.read_bytes()!=v for p,v in changes.items()):
            raise RuntimeError("Version already advanced with mismatched resources")
        print("PASS: Canva widget 3.15.8 patch idempotent")
        return
    if gradle.count("versionCode 74")!=1 or gradle.count("versionName '3.15.7'")!=1:
        raise RuntimeError("Requires verified 3.15.7 sources")
    protect={p:hashlib.sha256(p.read_bytes()).digest() for p in PROTECTED}
    changes[GRADLE]=(gradle.replace("versionCode 74","versionCode 75",1)
        .replace("versionName '3.15.7'","versionName '3.15.8'",1)).encode()
    old={p:p.read_bytes() if p.exists() else None for p in changes}
    written=[]
    try:
        for p,contents in changes.items():
            atomic(p,contents);written.append(p)
        if any(hashlib.sha256(p.read_bytes()).digest()!=hashValue
               for p,hashValue in protect.items()):
            raise RuntimeError("An unrelated widget has changed")
    except BaseException:
        for p in reversed(written):
            if old[p] is None:p.unlink(missing_ok=True)
            else:atomic(p,old[p])
        raise
    print("PASS: original Canva-style PNG assets + dynamic courses installed")
    print("PASS: other widgets unchanged; 3.15.8 versionCode 75")

if __name__=="__main__":
    main()
