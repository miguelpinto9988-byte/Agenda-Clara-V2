#!/usr/bin/env python3
"""Check the real PNG alpha, no framing, untouched spacing and nav."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
p=Path('updates/phase39/apply_3_9_9.py')
spec=spec_from_file_location("phase39",p)
module=module_from_spec(spec);spec.loader.exec_module(module)
base=Path('AgendaClara/app/src/main/res/drawable-nodpi')
for name in ('ic_ref_today_jump.png','ic_ref_class_schedule.png'):
    content=(base/name).read_bytes()
    assert module.alpha_stats(content)==(256,256)
    assert (Path('updates/phase39/assets')/name).read_bytes()==content
code=Path('AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java').read_text(encoding='utf-8')
assert 'ApprovedPng.button(todayButton,"today_jump",28)' in code
assert 'todayButton.setCompoundDrawablePadding(dp(12))' in code
assert 'ApprovedPng.view(this,"class_schedule",32)' in code
assert 'scheduleIconSpace.rightMargin=dp(12)' in code
assert 'text("Horario de clases",17,INK,true)' in code
nav=code[code.index('        nav=row();'):code.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
g=Path('AgendaClara/app/build.gradle').read_text(encoding='utf-8')
assert 'versionCode 40' in g and "versionName '3.9.9'" in g
print('PASS phase39: both 256x256 icon-only RGBA PNGs, alpha corners and margins, bottom navigation unchanged')
