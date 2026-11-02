#!/usr/bin/env python3
"""Restore pre-IME dialog size; avoid Android keeping its last keyboard-reduced bounds."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/WindowLayout.java")
s=p.read_text(encoding="utf-8")
def one(before,after):
    global s
    if s.count(before)!=1:raise RuntimeError("Unexpected WindowLayout baseline "+before[:50])
    s=s.replace(before,after,1)
one('final int[] previousMax={-1},previousIme={-1};',
    'final int[] previousMax={-1},previousIme={-1},preKeyboardHeight={0};')
one('''            boolean keyboardClosed=previousIme[0]==1&&!ime;
            WindowManager.LayoutParams p=w.getAttributes();
            int height=DialogResizePolicy.height(p.height,previousMax[0],max,
                decor.getMeasuredHeight(),keyboardClosed);''',
'''            boolean keyboardClosed=previousIme[0]==1&&!ime;
            // Capture natural height before opening the IME. Some Android 15 dialog
            // windows retain the keyboard-reduced content measurement on dismiss.
            if(!ime && previousIme[0]!=1 && decor.getMeasuredHeight()>0)
                preKeyboardHeight[0]=Math.max(preKeyboardHeight[0],
                    Math.min(max,decor.getMeasuredHeight()));
            WindowManager.LayoutParams p=w.getAttributes();
            int height=DialogResizePolicy.height(p.height,previousMax[0],max,
                decor.getMeasuredHeight(),keyboardClosed);
            if(keyboardClosed && preKeyboardHeight[0]>0)
                height=Math.min(max,preKeyboardHeight[0]);''')
p.write_text(s,encoding="utf-8")
print("PASS dialog windows retain and restore their pre-IME height")
