#!/usr/bin/env python3
"""Static Android resource and UI integration regression checks for icon release."""
from pathlib import Path
from PIL import Image
import hashlib,json,re
APP=Path('AgendaClara/app/src/main')
RES=APP/'res/drawable-nodpi'
JAVA=APP/'java/pe/agendaclara/app'
ASSETS=APP/'assets'
FILES=sorted(RES.glob('ic_adapt_*.png'))
assert len(FILES)==500, len(FILES)
assert len({p.name for p in FILES})==500
hashes=set()
for file in FILES:
    with Image.open(file) as im:
        assert im.size==(256,256),(file,im.size)
        assert im.convert('RGBA').getpixel((0,0))[3]==0,file
    hashes.add(hashlib.sha256(file.read_bytes()).hexdigest())
assert len(hashes)==500,len(hashes)
cat=json.loads((ASSETS/'adaptive_icon_catalog.json').read_text(encoding='utf8'))
assert cat['count']==500,len(cat['icons'])
assert len(cat['icons'])==500
assert cat['png_bytes']==sum(f.stat().st_size for f in FILES)
assert cat['png_bytes']<=15_000_000
assert sum(key.startswith('ui_') for key in cat['icons'])==172
idx=(JAVA/'AdaptiveIconIndex.java').read_text(encoding='utf8')
assert len(re.findall(r'"(?:ui_)?[a-z0-9_]+"',idx))==500
ui=(JAVA/'UiDesign.java').read_text(encoding='utf8')
assert 'FeatureIconLibrary.apply(b,caption)' in ui
resolver=(JAVA/'FeatureIconLibrary.java').read_text(encoding='utf8')
for key in ('ui_new_task','ui_new_note','ui_class_schedule','ui_pdf_import','ui_whatsapp_link'):
    assert key in resolver and (RES/f'ic_adapt_{key}.png').exists()
home=(JAVA/'HomeDashboard.java').read_text(encoding='utf8')
assert 'ui_class_schedule","ui_new_task","ui_exam_review","ui_new_note' in home
print('PASS 500 icons 256px; distinct, transparent; all catalog/index keys, UI bindings, APK budget')
