#!/usr/bin/env python3
"""Regression of real transparent PNGs, independent symbol/color, date/time and alarms."""
from pathlib import Path
import struct,zlib
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
draw=Path("AgendaClara/app/src/main/res/drawable-nodpi")
m=(src/"MainActivity.java").read_text()
cat=(src/"CategoryRegistry.java").read_text()
picker=(src/"ModernPickers.java").read_text()
logic=(src/"TaskLogic.java").read_text()
ui=(src/"UiDesign.java").read_text()
schedule=(src/"ScheduleActivity.java").read_text()
for cls in ("PngIcons","CategoryDesigner","RepeatPicker","ReminderSelector"):
    assert (src/(cls+".java")).is_file(),cls
names=["folder","date","time","bell","repeat","notes","save","whatsapp",
       "google_calendar","device_calendar","backup","notification","widgets",
       "settings","photo","manual","back","help","school","work","heart",
       "home","travel","book","color","urgent","check","calendar","clock",
       "study","cloud","trash","lock","key"]
for name in names:
    png=draw/("agenda_icon_"+name+".png")
    assert png.is_file(),str(png)
    data=png.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n',name
    assert struct.unpack("!II",data[16:24])==(96,96),name
    assert data[25]==6, "PNG must use RGBA"
    pos=8;compressed=b""
    while pos<len(data):
        length=struct.unpack("!I",data[pos:pos+4])[0]
        tag=data[pos+4:pos+8];part=data[pos+8:pos+8+length]
        assert struct.unpack("!I",data[pos+8+length:pos+12+length])[0]==zlib.crc32(tag+part)&0xffffffff
        if tag==b'IDAT':compressed+=part
        pos+=length+12
    raw=zlib.decompress(compressed)
    assert raw[4]==0 and raw[-1]==0, "Transparent outside icon"
assert len(list(draw.glob("agenda_icon_*.png")))>=40
assert "ModernGlyph.button(" not in m and "ModernGlyph.view(" not in m
assert "ModernGlyph.button(" not in schedule and "ModernGlyph.view(" not in schedule
assert "PngIcons.button(" in ui and "PngIcons.view(" in m
assert 'PngIcons.id(this,"back")' in schedule and 'PngIcons.id(this,"help")' in schedule
assert 'object.put("icon",e.icon)' in cat
assert 'record.optString("icon","folder")' in cat, "Old categories must upgrade non-destructively"
assert 'String icon(Context c,String name)' in cat
assert 'boolean save(Context c,String previous,String desired,int color,String symbol)' in cat
assert 'CategoryDesigner.show(this,existing,onSaved)' in m
designer=(src/"CategoryDesigner.java").read_text()
assert '"1 · Elige un símbolo"' in designer and '"2 · Elige un color"' in designer
assert 'CategoryRegistry.save(a,existing,desired,selectedColor[0],selectedIcon[0])' in designer
assert 'previewIcon.setImageResource(PngIcons.id(a,selectedIcon[0]))' in designer
assert 'PngIcons.view(a,entry.icon,28)' in picker
assert 'ModernPickers.showDate(this,date[0]' in m and 'ModernPickers.showTime(this,time[0]' in m
assert 'dial.getChildCount()==0' in picker, "Do not rebuild the clock dial every tick"
assert 'root.post(()->UiDesign.polishTree(root))' not in picker, "Picker must open without full-tree re-layout"
assert 'reminderButton.setOnClickListener(v->ReminderSelector.show(' in m
assert 'RepeatPicker.show(this,repeatValue[0]' in m
assert 'RepeatPicker.label(task.repeatMinutes)' in m
assert 't.repeatMinutes=intervals[repeat.getSelectedItemPosition()]' in m
assert 't.repeatMinutes==-1' in logic and 'first.plusMonths(i)' in logic, "Monthly means calendar months"
assert 'Reminders.schedule(this,t)' in m and 'Reminders.cancel(this,t.id)' in m
assert 'selectedCategory="General"' in m
assert '"Duración del evento"' not in m
plus=[x for x in m.splitlines() if 'setTag("new_task_button")' in x]
assert len(plus)==1 and 'new LinearLayout.LayoutParams(dp(108),dp(108))' in plus[0]
assert 'TopPlusButtonMotion.install(this)' in m and (src/"TopPlusButtonMotion.java").is_file()
assert (draw/"ic_top_plus_animated.png").is_file(), "Approved plus PNG intact"
print("PASS phase27: transparent PNG assets, category symbols/colors, repeat/calendar, fast selectors, unchanged top +")
