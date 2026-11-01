#!/usr/bin/env python3
"""Merge voice microphone permission handling with Agenda Clara's existing dispatcher."""
from pathlib import Path
file=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java")
src=file.read_text(encoding="utf-8")
duplicate='''    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        VoiceQuickTask.permissionResult(this,requestCode,permissions,grantResults);
    }
'''
existing='''    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] grants){
        super.onRequestPermissionsResult(request,permissions,grants);
        if(request==32)'''
merged='''    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] grants){
        super.onRequestPermissionsResult(request,permissions,grants);
        VoiceQuickTask.permissionResult(this,request,permissions,grants);
        if(request==32)'''
if src.count(duplicate)!=1 or src.count(existing)!=1:
    raise RuntimeError("Unexpected Android permission callbacks, refusing to modify")
src=src.replace(duplicate,"").replace(existing,merged)
assert src.count("void onRequestPermissionsResult(")==1
file.write_text(src,encoding="utf-8")
print("PASS: one permission callback dispatches voice, calendar and notifications")
