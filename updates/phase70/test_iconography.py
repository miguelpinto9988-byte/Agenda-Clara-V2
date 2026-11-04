#!/usr/bin/env python3
"""Pruebas estáticas de la fase 26/27 tras reconstruir fuentes e instalar iconos."""
from pathlib import Path
import hashlib
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_iconography import collect, DRAWABLE, JAVA

assets = collect()
assert len(assets) == 68
assert sum(n.startswith("ic_subject_") for n in assets) == 40
assert sum(not n.startswith("ic_subject_") for n in assets) == 28
for name, source in assets.items():
    actual = (DRAWABLE / name).read_bytes()
    assert hashlib.sha256(actual).digest() == hashlib.sha256(source).digest(), name
assert (DRAWABLE / "ic_quick_task.png").is_file()
assert (DRAWABLE / "ic_quick_new_task.png").is_file()
assert (DRAWABLE / "ic_quick_new_note.png").is_file()
catalog = (JAVA / "IconografiaFase26.java").read_text(encoding="utf-8")
assert 'subjectDrawable(Context context, String courseName)' in catalog
assert 'return "ic_subject_general";' in catalog
assert catalog.count('"' + 'general' + '"') == 1
quick = (JAVA / "MiDiaQuickActions.java").read_text(encoding="utf-8")
for token in ("ic_quick_task", "ic_quick_new_task", "ic_quick_new_note",
              "VoiceQuickTask.show(activity)", "activity.openEditor(-1, null, null)",
              "StickyNotesUi.showEditor(activity, null)"):
    assert token in quick, token
card = (JAVA / "MiDiaClassCard.java").read_text(encoding="utf-8")
assert "IconografiaFase26.subjectDrawable(a, selection.entry.course)" in card
assert 'new UiDesign.OutlineIcon("graduation", VIOLET)' in card
gradle = Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionCode 58" in gradle and "versionName '3.13.2'" in gradle
assert "applicationId 'pe.agendaclara.app'" in gradle
assert "signingConfig signingConfigs.development" in gradle
print("PASS: 68 recursos y 40 materias/28 complementarios con SHA-256 correctos")
print("PASS: iconos de voz, tarea, nota y clase; fallback presente; versión 3.13.2 (58)")
