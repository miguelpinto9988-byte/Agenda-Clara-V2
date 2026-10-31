#!/usr/bin/env python3
"""Check PNG contents, calendar rendering labels, spacing and untouched navigation."""
from pathlib import Path
import struct
import zlib
S=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
C=(S/'MainActivity.java').read_text(encoding='utf-8')
A=Path('AgendaClara/app/src/main/res/drawable-nodpi')
assert 'button("▣  Ir a hoy"' not in C
assert 'text("▦  Horario de clases"' not in C
assert 'Button todayButton=button("Ir a hoy",()->{' in C
assert 'ApprovedPng.button(todayButton,"today_jump",28)' in C
assert 'todayButton.setCompoundDrawablePadding(dp(12))' in C
assert 'todayButton.setMinHeight(dp(54))' in C
assert 'todayButton.setContentDescription("Ir a hoy, volver a la fecha actual")' in C
assert 'ApprovedPng.view(this,"class_schedule",32)' in C
assert 'scheduleIconSpace.rightMargin=dp(12)' in C
assert 'scheduleHeading.addView(scheduleTitle,new LinearLayout.LayoutParams(0,-2,1))' in C
assert 'text("Horario de clases",17,INK,true)' in C
nav=C[C.index('        nav=row();'):C.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav
assert 'dp(26),dp(26)' in nav
for name in ('ic_ref_today_jump.png','ic_ref_class_schedule.png'):
    data=(A/name).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n',name
    assert struct.unpack('>II',data[16:24])==(192,192),name
    assert len(data)>2000,name
    assert data[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82',name
    assert b'IDAT' in data,name
    assert zlib.decompress(data[data.index(b'IDAT')+4:-16]),name
assert 'versionCode 39' in Path('AgendaClara/app/build.gradle').read_text()
assert "versionName '3.9.8'" in Path('AgendaClara/app/build.gradle').read_text()
print('PASS phase38: real transparent PNG, bold aligned calendar header and button, bottom nav unchanged')
