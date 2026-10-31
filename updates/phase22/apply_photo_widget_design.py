#!/usr/bin/env python3
"""Phase22c: visual parity for the photo-widget configuration Activity."""
from pathlib import Path
path=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/PhotoConfigActivity.java")
s=path.read_text(encoding="utf-8")
def one(a,b,label):
    global s
    if s.count(a)!=1:raise RuntimeError("photo widget visual "+label+" anchor: "+str(s.count(a)))
    s=s.replace(a,b,1)
one('body.setBackgroundColor(0xfff4f7ff);','body.setBackgroundColor(UiDesign.BG);',"background")
one('title.setTextColor(0xff101d43);body.addView(title);',
    'title.setTextColor(UiDesign.INK);UiDesign.text(title,true);body.addView(title);',"header")
one('note.setPadding(0,20,0,20);body.addView(note);',
    'note.setTextColor(UiDesign.MUTED);UiDesign.text(note,false);note.setTextSize(14);note.setPadding(0,WindowLayout.dp(this,16),0,WindowLayout.dp(this,20));body.addView(note);',"support text")
one('preview.setBackgroundColor(0xffe9f0ff);',
    'preview.setBackground(UiDesign.shape(this,UiDesign.PALE,20,UiDesign.BORDER));preview.setClipToOutline(true);',"photo preview")
one('choose.setText("Cambiar imagen");body.addView(choose);',
    'choose.setText("Cambiar imagen");UiDesign.button(choose,false);LinearLayout.LayoutParams chooser=new LinearLayout.LayoutParams(-1,WindowLayout.dp(this,50));chooser.topMargin=WindowLayout.dp(this,16);chooser.bottomMargin=WindowLayout.dp(this,14);body.addView(choose,chooser);',"photo picker")
one('fit.setChecked(contain);body.addView(fit);',
    'fit.setChecked(contain);fit.setTextColor(UiDesign.INK);fit.setButtonTintList(android.content.res.ColorStateList.valueOf(UiDesign.BLUE));body.addView(fit);',"preview fit")
one('save.setText("Guardar widget");body.addView(save);',
    'save.setText("Guardar widget");UiDesign.button(save,true);LinearLayout.LayoutParams saveLp=new LinearLayout.LayoutParams(-1,WindowLayout.dp(this,54));saveLp.topMargin=WindowLayout.dp(this,20);saveLp.bottomMargin=WindowLayout.dp(this,24);body.addView(save,saveLp);',"save button")
one('t.setText(title);body.addView(t);',
    't.setText(title);t.setTextColor(UiDesign.INK);t.setTextSize(14);UiDesign.text(t,true);body.addView(t);',"slider label")
one('bar.setMax(100);',
    'bar.setMax(100);bar.setProgressTintList(android.content.res.ColorStateList.valueOf(UiDesign.BLUE));bar.setThumbTintList(android.content.res.ColorStateList.valueOf(UiDesign.BLUE));',"slider colors")
path.write_text(s,encoding="utf-8")
print("PASS phase22: photo-widget config uses shared typography, safe padding, fields, and buttons")
