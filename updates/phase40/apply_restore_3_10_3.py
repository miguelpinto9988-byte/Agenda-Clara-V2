#!/usr/bin/env python3
"""Restore 3.9.9 two-stage WhatsApp unchanged; set window transitions to 300 ms."""
from pathlib import Path
R=Path("AgendaClara"); S=R/"app/src/main/java/pe/agendaclara/app"
RES=R/"app/src/main/res"; G=R/"app/build.gradle"
def one(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"3.10.3 {label}: expected one anchor, found {n}")
    return s.replace(old,new,1)
def run():
    java=(S/"WhatsAppSessionService.java").read_bytes()
    native=(R/"whatsapp-native/main.go").read_bytes()
    assert b'go t.history("")' in native and b'go t.history(r.JID)' in native
    assert b'"history".equals(action)' in java and b'"more".equals(action)' in java
    assert b'requestedHistoryJid' not in java and b'historyTarget' not in native
    ui=S/"UiMotion.java";popup=S/"CreationChoices.java";styles=RES/"values/styles.xml"
    motion=one(ui.read_text(encoding="utf-8"),".setDuration(195).start();",
        ".setDuration(300).setInterpolator(new android.view.animation.DecelerateInterpolator(1.15f)).withLayer().start();","tab transition")
    choices=one(popup.read_text(encoding="utf-8"),".setDuration(190).start();",
        ".setDuration(300).setInterpolator(new android.view.animation.DecelerateInterpolator(1.15f)).withLayer().start();","plus menu")
    theme=one(styles.read_text(encoding="utf-8"),"@android:anim/fade_in","@anim/agenda_restore_dialog_in","dialog in")
    theme=one(theme,"@android:anim/fade_out","@anim/agenda_restore_dialog_out","dialog out")
    grad=one(G.read_text(encoding="utf-8"),"versionCode 40","versionCode 44","version code")
    grad=one(grad,"versionName '3.9.9'","versionName '3.10.3'","version name")
    animations=RES/"anim";animations.mkdir(parents=True,exist_ok=True)
    for name,a,b in [("agenda_restore_dialog_in.xml","0.0","1.0"),
                     ("agenda_restore_dialog_out.xml","1.0","0.0")]:
        f=animations/name
        if f.exists():raise RuntimeError("Refusing to overwrite existing animation "+name)
        f.write_text('<?xml version="1.0" encoding="utf-8"?>\n'
          '<alpha xmlns:android="http://schemas.android.com/apk/res/android"\n'
          f'    android:fromAlpha="{a}" android:toAlpha="{b}"\n'
          '    android:duration="300"\n'
          '    android:interpolator="@android:interpolator/decelerate_quad"/>\n',encoding="utf-8")
    ui.write_text(motion,encoding="utf-8")
    popup.write_text(choices,encoding="utf-8")
    styles.write_text(theme,encoding="utf-8")
    G.write_text(grad,encoding="utf-8")
    assert (S/"WhatsAppSessionService.java").read_bytes()==java
    assert (R/"whatsapp-native/main.go").read_bytes()==native
    print("PASS 3.10.3 restore: original two-step WhatsApp unchanged; 300ms dialog/tab/plus")
if __name__=="__main__":run()
