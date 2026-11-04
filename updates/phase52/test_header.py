#!/usr/bin/env python3
"""Phase 5 integration guards: validate compiled Android source staging."""
from pathlib import Path
from hashlib import sha256
import xml.etree.ElementTree as ET

ROOT = Path("AgendaClara/app/src/main")
CODE = ROOT / "java/pe/agendaclara/app"
here = Path(__file__).resolve().parent
old = (here.parent / "phase51/MiDiaHeaderView.java").read_bytes()
new = (here / "MiDiaHeaderView.java").read_bytes()
on_disk = (CODE / "MiDiaHeaderView.java").read_bytes()
assert on_disk == new and old != new, "Phase5 must replace only the approved home header"
main = (CODE / "MainActivity.java").read_text(encoding="utf-8")
assert "if(page==0)MiDiaDashboard.render(this)" in main
assert 'new String[]{"Inicio","Calendario","Revisar","Conexiones"}' in main
header = on_disk.decode("utf-8")
assert header.count('setContentDescription(') >= 5
assert 'activity.page = 2;' in header and 'activity.page = 3;' in header
assert 'new InputFilter.LengthFilter(28)' in header
assert 'MiDiaDailyRotation.backgroundResource' in header
assert 'MiDiaDailyRotation.quote' in header
assert 'dateSubtitle.setText("Semana "' in header
assert 'Prefs.get(getContext()).getString(NAME_KEY, "")' in header
quotes = ET.parse(ROOT / "res/values/mi_dia_frases.xml").getroot().find("./string-array[@name='mi_dia_frases']")
assert quotes is not None and len(quotes.findall("item")) == 50
images = sorted((ROOT / "res/drawable-nodpi").glob("bg_mi_dia_*.png"))
assert len(images) == 30 and len({sha256(p.read_bytes()).hexdigest() for p in images}) == 30
for icon in ["ic_ref_bell.png","ic_ref_notification.png"]:
    assert (ROOT / "res/drawable-nodpi" / icon).is_file()
print("PASS phase5: native source, 30 offline backgrounds, 50 quotes, menu shortcuts, editable greeting, navigation retained")
