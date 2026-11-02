#!/usr/bin/env python3
"""Avoid circular IME sizing: Android 11+ window metrics supersede stale dialog frames."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/WindowLayout.java")
s=p.read_text(encoding="utf-8")
old='if(visible.width()>0&&visible.height()>0)bounds.intersect(visible);'
new='''// On Android 11+, window metrics and IME insets already provide safe bounds.
        // The dialog's visible display frame may still reflect its previous
        // keyboard-reduced dimensions, causing permanent shrinkage on IME close.
        if(Build.VERSION.SDK_INT<30&&visible.width()>0&&visible.height()>0)
            bounds.intersect(visible);'''
if s.count(old)!=1:raise RuntimeError("Unexpected WindowLayout visible-frame code")
s=s.replace(old,new,1)
old='''if(keyboardClosed && preKeyboardHeight[0]>0)
                height=Math.min(max,preKeyboardHeight[0]);'''
new='''if(keyboardClosed && preKeyboardHeight[0]>=max*.85f)
                height=Math.min(max,preKeyboardHeight[0]);
            else if(keyboardClosed)
                height=WindowManager.LayoutParams.WRAP_CONTENT;'''
if s.count(old)!=1:raise RuntimeError("Unexpected prior dialog restoration")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("PASS: screen bounds no longer intersect stale floating-dialog visible frames")
