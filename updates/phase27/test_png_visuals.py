#!/usr/bin/env python3
"""Phase27: test PNG alpha, symbol persistence, recurrence and old task handling."""
from pathlib import Path
import struct,zipfile
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
r=Path("AgendaClara/app/src/main/res/drawable-nodpi")
main=(p/"MainActivity.java").read_text(encoding="utf-8")
registry=(p/"CategoryRegistry.java").read_text(encoding="utf-8")
glyph=(p/"ModernGlyph.java").read_text(encoding="utf-8")
png=(p/"ApprovedPng.java").read_text(encoding="utf-8")
picker=(p/"ModernPickers.java").read_text(encoding="utf-8")
repeat=(p/"ModernRepeat.java").read_text(encoding="utf-8")
chooser=(p/"CategorySymbolChooser.java").read_text(encoding="utf-8")
assets=list(r.glob("ic_ref_*.png"))
assert len(assets)>=35,(len(assets),[x.name for x in assets])
for path in assets:
    data=path.read_bytes()
    assert data[:8]==b"\x89PNG\r\n\x1a\n",path
    width,height=struct.unpack(">II",data[16:24])
    assert width>=60 and height>=60,path
    assert data[25]==6,("PNG must be RGBA and transparent",path.name)
assert 'ApprovedPng.view(context,name,sizeDp)' in glyph
assert 'ApprovedPng.button(button,name,iconDp)' in glyph
assert 'ApprovedPng.view(a,CategoryRegistry.icon(a,chosen),28)' in picker
assert 'public final String icon;' in registry
assert 'object.put("icon",e.icon)' in registry
assert 'record.optString("icon","folder")' in registry
assert 'return save(c,previous,desired,color,icon(c,previous));' in registry
assert 'if(oldIndex==0)return false' in registry
assert 'if(!name.isEmpty()&&!has(items,name)' in registry
assert 'CategorySymbolChooser.show(this,existing,name->' in main
assert '"1. Elige un símbolo"' in chooser and '"2. Elige un color"' in chooser
assert 'previewIcon.setImageDrawable(ApprovedPng.drawable(a,icon[0]))' in chooser
assert 'CategoryRegistry.save(a,existing,desired,color[0],icon[0])' in chooser
assert 'repeatMinutes[0]' in main and 'ModernRepeat.show(this,repeatMinutes[0]' in main
assert 'ModernRepeat.title(rv)' in main
assert 't.repeatMinutes=repeatMinutes[0]' in main
assert 'Reminders.schedule(this,t)' in main and 'Reminders.cancel(this,t.id)' in main
assert 'callback.accept(LocalTime.of(h,minute[0]))' in picker
assert 'big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));' in picker
assert 'La repetición termina en la fecha límite' in repeat
assert 'setCompoundDrawablesRelative(d,null,null,null)' in png
assert "setColorFilter" not in png, "Never tint approved PNG"
assert 'new LinearLayout.LayoutParams(dp(108),dp(108))' in main
assert 'setTag("new_task_button")' in main and 'TopPlusButtonMotion.install(this)' in main
assert Path("AgendaClara/app/src/main/res/drawable-nodpi/ic_top_plus_animated.png").exists()
assert 'selectedCategory="General"' in main
assert 'Duración del evento' not in main
print("PASS phase27: 35 real transparent PNGs, separate symbols/colors, native selectors, customizable reminders and top + preserved")
