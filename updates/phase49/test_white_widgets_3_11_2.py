#!/usr/bin/env python3
"""Verify approved light widgets and byte-for-byte preservation of existing icons."""
from pathlib import Path
import hashlib,xml.etree.ElementTree as ET
r=Path("AgendaClara");res=r/"app/src/main/res";java=r/"app/src/main/java/pe/agendaclara/app"
A="{http://schemas.android.com/apk/res/android}"
def parse(name):return ET.parse(res/name).getroot()
def find(tree,id):
    return next(x for x in tree.iter() if x.attrib.get(A+"id")=="@+id/"+id)
bg=parse("drawable/widget_bg.xml");grad=bg.find("gradient")
assert grad.attrib[A+"startColor"].upper()=="#FFFFFF"
assert grad.attrib[A+"endColor"].upper()=="#F4F1FF"
assert parse("drawable/widget_list_bg.xml").find("solid").attrib[A+"color"]=="#FFFFFF"
for layout in ("widget_tasks.xml","widget_sticky_notes.xml","widget_sticky_notes_compact.xml"):
    assert parse("layout/"+layout).attrib[A+"background"]=="@drawable/widget_bg"
tasks=parse("layout/widget_tasks.xml")
assert find(tasks,"widget_header").attrib[A+"textColor"]=="#101B42"
assert find(tasks,"widget_subtitle").attrib[A+"textColor"]=="#6241E3"
assert find(tasks,"widget_add").attrib[A+"src"]=="@drawable/ic_ref_widget_plus"
assert next(x for x in tasks.iter() if x.tag=="ImageView"
     and x.attrib.get(A+"contentDescription")=="Agenda Clara").attrib[A+"src"]=="@drawable/ic_ref_widget_brand"
for name in ("widget_sticky_notes.xml","widget_sticky_notes_compact.xml"):
    assert find(parse("layout/"+name),"sticky_widget_add").attrib[A+"text"]=="＋"
for name in ("widget_sticky_row.xml","widget_sticky_row_compact.xml"):
    row=parse("layout/"+name)
    assert find(row,"sticky_widget_art").attrib[A+"src"]=="@drawable/sticky_yellow"
    assert find(row,"sticky_widget_calendar_icon").attrib[A+"src"]=="@drawable/ic_ref_date"
icons={
'ic_ref_widget_brand.png':'33e425e2a38e0673da3da5369741950fc1be4517a71bab6ce6e5df7ab0b8455a',
'ic_ref_widget_plus.png':'d9a4ca9a86c548f6e6d1a677a690554aa04edc72ff282252961733ef7c4946a9',
'ic_ref_widget_cancel.png':'3c57bb5f62a66890a4aac66aa9c84b2f1329de94faebe40c13a188f2bdad935c',
'ic_ref_widget_voice.png':'b3d6ac1be1c8e5683665b03052dba756a7f5544c3d0f88cf5dc59b5b4808a0d2',
'ic_ref_widget_manual.png':'9f5fbf81bf64ccaefd63a4a494921d47c7d232f333398ff3ab537f1d64a3ef8d',
'sticky_yellow.png':'3abe0a65c8c2bc71399090b1d9ad33037b5e080dcd99072b66055788d8fd2371',
'sticky_pink.png':'3ed0acc236897824ead56249039d5bcabb0db4f5131caa103f21a70fa61949a0',
'sticky_blue.png':'8e1781d5cb1a495c0a41d9b551a9a74a708ab908bebef60d6f9759541e4414bc',
'sticky_green.png':'26f14da526aa70e813fde3a16f832f5aba72efc31d90fb2ef74fe75bce92aaa2',
'sticky_purple.png':'56a5ad19bb69638884614b175c42f5c2e0065e4f5e070d08de5aaf064e1cd27a',
'sticky_peach.png':'f5b8990fc93143d74041ab6c07a641875ab114dfdb68ceb8262330ab83b3ffef',
'ic_ref_date.png':'694dc53bf82404a3f7fe43b9a8b3317cb8d2a8194e8eaa3309a817bdbcc32f1c'}
for filename,sha in icons.items():
    p=res/"drawable-nodpi"/filename
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,"Artwork changed: "+filename
widget=(java/"WidgetTaskActivity.java").read_text()
voice=(java/"VoiceQuickTask.java").read_text()
assert "0xffFFFFFF,26,0xffDDD8F4" in widget and "BLUE=0xff6946F2" in widget
assert "renderSelector()" in widget and "renderNormal()" in widget
assert "WindowInsets.Type.ime()" in widget and "applyWindowSize()" in widget
assert "VoiceQuickTask.show(this)" in widget and "Reminders.schedule(this,task)" in widget
assert "blue=a instanceof WidgetTaskActivity?0xff6946F2:UiDesign.BLUE" in voice
assert "waveAnimator.start()" in voice and "widget_cancel" in voice
assert "new Intent(c,WidgetTaskActivity.class)" in (java/"TaskWidget.java").read_text()
assert "versionCode 53" in (r/"app/build.gradle").read_text()
assert "versionName '3.11.2'" in (r/"app/build.gradle").read_text()
print("PASS: light widgets, floating task/voice functions, IME restoration, 12 original PNG files")
