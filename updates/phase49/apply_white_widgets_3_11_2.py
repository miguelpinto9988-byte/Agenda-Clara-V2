#!/usr/bin/env python3
"""Agenda Clara 3.11.2: approved white/lavender widget UI only.

No bitmap data, widget routing, reminder logic, or private user content is modified.
The check against the exact 3.11.1 baseline prevents accidental overwrites.
"""
from pathlib import Path
import hashlib

ROOT=Path('AgendaClara')
RES=ROOT/'app/src/main/res'
SRC=ROOT/'app/src/main/java/pe/agendaclara/app'
GRADLE=ROOT/'app/build.gradle'

BASELINE={
 'app/src/main/res/drawable/widget_bg.xml':'e69025922f05543b369797d075038ed40c40222745899c9223bef517becec512',
 'app/src/main/res/drawable/widget_list_bg.xml':'26289a4dc46395f5eef6cdb6b3b045a8aa8201729a981c3d70746ca9c9438b73',
 'app/src/main/res/layout/widget_tasks.xml':'398e25bab4cc1e1ad57db8a6f575368c5badff777ee5ad7c86ad51f2db5918a6',
 'app/src/main/res/layout/widget_sticky_notes.xml':'fcec6ca3ba55e71e1a1a322432b3002ff01d1aa31633a9a0686b1482da2fa6ba',
 'app/src/main/res/layout/widget_sticky_notes_compact.xml':'14463efaaabb656fed99a704355ab966acc362d12a4e353558fb729f3747af87',
 'app/src/main/java/pe/agendaclara/app/WidgetTaskActivity.java':'cd58a1c071aa6a062e4af44354b1c23c21b20e485c6eaff491385bdf83c854de',
 'app/src/main/java/pe/agendaclara/app/VoiceQuickTask.java':'6d54eb62bd480006a23bacc970a4ac18832fd968a4dca007ee5d250026d71d8a',
}
for name,digest in BASELINE.items():
    path=ROOT/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise RuntimeError('Source differs from verified 3.11.1, refusing widget restyling: '+name)
version=GRADLE.read_text(encoding='utf-8')
if version.count('versionCode 52')!=1 or version.count("versionName '3.11.1'")!=1:
    raise RuntimeError('Unexpected version; refusing to update')

(RES/'drawable/widget_bg.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="#FFFFFF" android:centerColor="#FCFBFF" android:endColor="#F4F1FF"/>
    <corners android:radius="26dp"/>
    <stroke android:width="1dp" android:color="#DDD8F4"/>
</shape>
''',encoding='utf-8')
(RES/'drawable/widget_list_bg.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFFFF"/>
    <corners android:radius="18dp"/>
    <stroke android:width="1dp" android:color="#EAE6F7"/>
</shape>
''',encoding='utf-8')

def replace_once(src,old,new,label):
    count=src.count(old)
    if count!=1:raise RuntimeError(f'Unexpected {label} anchor: {count}')
    return src.replace(old,new,1)

tasks=RES/'layout/widget_tasks.xml';s=tasks.read_text(encoding='utf-8')
s=replace_once(s,'android:text="Agenda Clara" android:textColor="#FFFFFF"',
    'android:text="Agenda Clara" android:textColor="#101B42"','task widget header')
s=replace_once(s,'android:text="Mis tareas de hoy" android:textColor="#A8ECFF"',
    'android:text="Mis tareas de hoy" android:textColor="#6241E3"','task widget subtitle')
s=replace_once(s,'android:divider="#E2E8F4"',
    'android:divider="#EAE7F5"','row dividers')
tasks.write_text(s,encoding='utf-8')

for filename,old,new in [
    ('widget_sticky_notes.xml','android:textColor="#14254B"','android:textColor="#101B42"'),
    ('widget_sticky_notes_compact.xml','android:textColor="#14254B"','android:textColor="#101B42"'),
]:
    f=RES/'layout'/filename;txt=f.read_text(encoding='utf-8')
    f.write_text(replace_once(txt,old,new,filename),encoding='utf-8')

f=SRC/'WidgetTaskActivity.java';txt=f.read_text(encoding='utf-8')
txt=replace_once(txt,
    'private final int INK=0xff102457, MUTED=0xff5d719e, BLUE=0xff2458fb;',
    'private final int INK=0xff111B42, MUTED=0xff64718F, BLUE=0xff6946F2;',
    'widget surface color tokens')
txt=replace_once(txt,
    'b.setBackground(background(primary?BLUE:0xffedf2ff,17,primary?0:0xffd6e2ff));',
    'b.setBackground(background(primary?BLUE:0xffF0EDFF,17,primary?0:0xffE3DCF8));',
    'widget buttons')
txt=replace_once(txt,
    'content.setBackground(background(0xfffafdff,26,0xffcfdcff));',
    'content.setBackground(background(0xffFFFFFF,26,0xffDDD8F4));',
    'floating background')
txt=replace_once(txt,
    'x.setBackground(background(0xffedf3ff,15,0xffd9e5ff));',
    'x.setBackground(background(0xffF2EFFF,15,0xffE5E0F7));',
    'close button')
txt=replace_once(txt,
    'item.setBackground(background(primary?0xfff1efff:Color.WHITE,20,primary?0xff9363ff:0xffd6e2f6));',
    'item.setBackground(background(primary?0xffF2EEFF:Color.WHITE,20,primary?0xff9D87F8:0xffE6E1F5));',
    'floating chooser cards')
txt=replace_once(txt,
    'if(primary)labels.addView(text("⚡ Más rápida",12,0xff7940df,true));',
    'if(primary)labels.addView(text("⚡ Más rápida",12,0xff6E43E8,true));',
    'floating badge')
txt=replace_once(txt,
    'e.setBackground(background(Color.WHITE,12,0xffd8e3ff));',
    'e.setBackground(background(Color.WHITE,12,0xffE1DDF4));',
    'manual input outline')
f.write_text(txt,encoding='utf-8')

f=SRC/'VoiceQuickTask.java';txt=f.read_text(encoding='utf-8')
txt=replace_once(txt,
    'final int blue=UiDesign.BLUE;',
    'final int blue;',
    'voice accent declaration')
txt=replace_once(txt,
    'Session(Activity a){activity=a;recordingDate=LocalDate.now();}',
    'Session(Activity a){activity=a;recordingDate=LocalDate.now();'
    'blue=a instanceof WidgetTaskActivity?0xff6946F2:UiDesign.BLUE;}',
    'voice accent for widget only')
txt=replace_once(txt,
    'UiDesign.button(b,mainStyle);b.setMinHeight(dp(54));return b;',
    '''UiDesign.button(b,mainStyle);
            if(activity instanceof WidgetTaskActivity){
                GradientDrawable shape=mainStyle
                    ?new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,
                        new int[]{0xff7655FA,0xff6340EB})
                    :new GradientDrawable();
                if(!mainStyle){shape.setColor(0xffF2EFFF);shape.setStroke(dp(1),0xffE2DCF8);}
                shape.setCornerRadius(dp(17));b.setBackground(shape);
                b.setTextColor(mainStyle?Color.WHITE:0xff6545E5);
            }
            b.setMinHeight(dp(54));return b;''',
    'voice action buttons')
f.write_text(txt,encoding='utf-8')

GRADLE.write_text(version.replace('versionCode 52','versionCode 53')
    .replace("versionName '3.11.1'","versionName '3.11.2'"),encoding='utf-8')
print('PASS 3.11.2: white/lavender task and note widgets and floating dialogs; existing icons unchanged')
