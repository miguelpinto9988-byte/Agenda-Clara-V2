#!/usr/bin/env python3
"""3.11.2: white/lavender widgets, without changing any existing PNG or behavior."""
from pathlib import Path
import hashlib,xml.etree.ElementTree as ET
r=Path("AgendaClara"); res=r/"app/src/main/res"; java=r/"app/src/main/java/pe/agendaclara/app"
expected={
"app/src/main/res/drawable/widget_bg.xml":"e69025922f05543b369797d075038ed40c40222745899c9223bef517becec512",
"app/src/main/res/drawable/widget_list_bg.xml":"26289a4dc46395f5eef6cdb6b3b045a8aa8201729a981c3d70746ca9c9438b73",
"app/src/main/res/layout/widget_tasks.xml":"398e25bab4cc1e1ad57db8a6f575368c5badff777ee5ad7c86ad51f2db5918a6",
"app/src/main/res/layout/widget_sticky_notes.xml":"fcec6ca3ba55e71e1a1a322432b3002ff01d1aa31633a9a0686b1482da2fa6ba",
"app/src/main/res/layout/widget_sticky_notes_compact.xml":"14463efaaabb656fed99a704355ab966acc362d12a4e353558fb729f3747af87",
"app/src/main/java/pe/agendaclara/app/WidgetTaskActivity.java":"cd58a1c071aa6a062e4af44354b1c23c21b20e485c6eaff491385bdf83c854de",
"app/src/main/java/pe/agendaclara/app/VoiceQuickTask.java":"6d54eb62bd480006a23bacc970a4ac18832fd968a4dca007ee5d250026d71d8a"}
for name,digest in expected.items():
    p=r/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise RuntimeError("Refusing unexpected 3.11.1 baseline: "+name)
gradle=r/"app/build.gradle"; g=gradle.read_text()
assert g.count("versionCode 52")==1 and g.count("versionName '3.11.1'")==1
def rep(file,old,new):
    p=r/file; data=p.read_text(encoding="utf-8")
    if data.count(old)!=1: raise RuntimeError("Missing or repeated style anchor: "+file+" / "+old[:48])
    p.write_text(data.replace(old,new,1),encoding="utf-8")
(res/"drawable/widget_bg.xml").write_text("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
<gradient android:type="linear" android:angle="270" android:startColor="#FFFFFF"
android:centerColor="#FCFBFF" android:endColor="#F4F1FF"/>
<corners android:radius="26dp"/>
<stroke android:width="1dp" android:color="#DDD8F4"/>
</shape>
""",encoding="utf-8")
(res/"drawable/widget_list_bg.xml").write_text("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
<solid android:color="#FFFFFF"/><corners android:radius="18dp"/>
<stroke android:width="1dp" android:color="#EAE6F7"/>
</shape>
""",encoding="utf-8")
T="app/src/main/res/layout/widget_tasks.xml"
rep(T,'android:text="Agenda Clara" android:textColor="#FFFFFF"','android:text="Agenda Clara" android:textColor="#101B42"')
rep(T,'android:text="Mis tareas de hoy" android:textColor="#A8ECFF"','android:text="Mis tareas de hoy" android:textColor="#6241E3"')
rep(T,'android:divider="#E2E8F4"','android:divider="#EAE7F5"')
for name in ("widget_sticky_notes.xml","widget_sticky_notes_compact.xml"):
    rep("app/src/main/res/layout/"+name,'android:textColor="#14254B"','android:textColor="#101B42"')
W="app/src/main/java/pe/agendaclara/app/WidgetTaskActivity.java"
rep(W,"private final int INK=0xff102457, MUTED=0xff5d719e, BLUE=0xff2458fb;",
      "private final int INK=0xff111B42, MUTED=0xff64718F, BLUE=0xff6946F2;")
rep(W,"b.setBackground(background(primary?BLUE:0xffedf2ff,17,primary?0:0xffd6e2ff));",
      "b.setBackground(background(primary?BLUE:0xffF0EDFF,17,primary?0:0xffE3DCF8));")
rep(W,"content.setBackground(background(0xfffafdff,26,0xffcfdcff));",
      "content.setBackground(background(0xffFFFFFF,26,0xffDDD8F4));")
rep(W,"x.setBackground(background(0xffedf3ff,15,0xffd9e5ff));",
      "x.setBackground(background(0xffF2EFFF,15,0xffE5E0F7));")
rep(W,"item.setBackground(background(primary?0xfff1efff:Color.WHITE,20,primary?0xff9363ff:0xffd6e2f6));",
      "item.setBackground(background(primary?0xffF2EEFF:Color.WHITE,20,primary?0xff9D87F8:0xffE6E1F5));")
rep(W,'if(primary)labels.addView(text("⚡ Más rápida",12,0xff7940df,true));',
      'if(primary)labels.addView(text("⚡ Más rápida",12,0xff6E43E8,true));')
rep(W,"e.setBackground(background(Color.WHITE,12,0xffd8e3ff));",
      "e.setBackground(background(Color.WHITE,12,0xffE1DDF4));")
V="app/src/main/java/pe/agendaclara/app/VoiceQuickTask.java"
rep(V,"final int blue=UiDesign.BLUE;","final int blue;")
rep(V,"Session(Activity a){activity=a;recordingDate=LocalDate.now();}",
      "Session(Activity a){activity=a;recordingDate=LocalDate.now();blue=a instanceof WidgetTaskActivity?0xff6946F2:UiDesign.BLUE;}")
rep(V,"UiDesign.button(b,mainStyle);b.setMinHeight(dp(54));return b;", """UiDesign.button(b,mainStyle);
            if(activity instanceof WidgetTaskActivity){
                GradientDrawable shape=mainStyle
                    ?new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{0xff7655FA,0xff6340EB})
                    :new GradientDrawable();
                if(!mainStyle){shape.setColor(0xffF2EFFF);shape.setStroke(dp(1),0xffE2DCF8);}
                shape.setCornerRadius(dp(17));b.setBackground(shape);
                b.setTextColor(mainStyle?Color.WHITE:0xff6545E5);
            }
            b.setMinHeight(dp(54));return b;""")
gradle.write_text(g.replace("versionCode 52","versionCode 53")
    .replace("versionName '3.11.1'","versionName '3.11.2'"),encoding="utf-8")
for path in ("drawable/widget_bg.xml","drawable/widget_list_bg.xml","layout/widget_tasks.xml",
             "layout/widget_sticky_notes.xml","layout/widget_sticky_notes_compact.xml"):
    ET.parse(res/path)
print("PASS 3.11.2 white/lavender widgets, unchanged PNG/iconography and widget behavior")
