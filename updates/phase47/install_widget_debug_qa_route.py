#!/usr/bin/env python3
"""Expose a diagnostic route through the exported app Activity only in debuggable builds.

The production widget companion remains android:exported=false and is launched by the
app-owned PendingIntent. The route cannot be triggered in non-debuggable releases.
"""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java")
s=p.read_text(encoding="utf-8")
before='''    void route(Intent i){
        if(Intent.ACTION_SEND.equals(i.getAction())'''
after='''    void route(Intent i){
        if("pe.agendaclara.app.WIDGET_QA".equals(i.getAction())
            && (getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE)!=0){
            startActivity(new Intent(this,WidgetTaskActivity.class)
                .setAction(WidgetTaskActivity.ACTION_CREATE));
            finish();return;
        }
        if(Intent.ACTION_SEND.equals(i.getAction())'''
if s.count(before)!=1:raise RuntimeError("Unexpected MainActivity route baseline")
p.write_text(s.replace(before,after,1),encoding="utf-8")
print("PASS widget private diagnostic route is enabled only in debuggable builds")
