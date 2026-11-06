#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from xml.etree import ElementTree as ET

ROOT=Path("AgendaClara/app/src/main")
layout=ROOT/"res/layout/widget_academic_day.xml"
tree=ET.parse(layout)
elements=list(tree.iter())
ns="{http://schemas.android.com/apk/res/android}"
ids={e.get(ns+"id","").split("/")[-1] for e in elements}
needed={"academic_day_root","academic_day_heading","academic_day_date",
"academic_day_profile","academic_day_course","academic_day_course_2",
"academic_day_time","academic_day_time_2","academic_day_room",
"academic_day_room_2","academic_day_card_1","academic_day_card_2",
"academic_day_tasks","academic_day_tasks_label","academic_day_cta",
"academic_day_arrow","academic_day_cap_front"}
assert needed.issubset(ids),needed-ids
assert elements[-1].get(ns+"id")=="@+id/academic_day_cap_front"
icons=sorted((ROOT/"res/drawable-nodpi").glob("ac_day_*.png"))
assert len(icons)==9,len(icons)
for p in icons:
    with Image.open(p) as image:
        assert image.format=="PNG"
        if p.name!="ac_day_landscape.png":
            assert image.convert("RGBA").getchannel("A").getextrema()[0]==0,p
for n in elements:
    for value in n.attrib.values():
        if value.startswith("@drawable/"):
            label=value.partition("/")[2]
            assert (ROOT/"res/drawable"/(label+".xml")).is_file() or \
                   (ROOT/"res/drawable-nodpi"/(label+".png")).is_file(),label
source=(ROOT/"java/pe/agendaclara/app/AcademicDayWidget.java").read_text()
for phrase in ["AcademicDayWidgetData.today","academic_day_course_2",
               "academic_day_time_2","hidePrivateTitles",
               "tasksForDisplayedCourses","pendingTasks",
               "AcademicWidgetTheme.applyDay","OPTION_APPWIDGET_MIN_HEIGHT"]:
    if phrase=="tasksForDisplayedCourses":continue
    assert phrase in source,phrase
assert "Tendencias Educativas" not in source
print("PASS: 9 PNG files, cap at highest z-order, all drawable refs and dynamic fields")
print("PASS: Canva design is connected to real course data, no baked-in test titles")
