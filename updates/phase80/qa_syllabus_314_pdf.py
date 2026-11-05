#!/usr/bin/env python3
"""Android 15 full PDF import regression, adapted from the 3.13.8 verified scenario.

Uses an entirely synthetic academic document; exercises real file picker,
multi-profile choice, review, confirmation and SQLite task/link persistence.
"""
from pathlib import Path

original=Path("updates/phase78/qa_syllabus_pdf.py")
text=original.read_text(encoding="utf-8")
translations={
    'wait("Confirmar 4 evaluaciones")':'wait("Confirmar cambios del sílabo")',
    'click("Guardar en este curso")':'click("Aplicar cambios")',
    'wait("Evaluaciones incorporadas")':'wait("Sílabo incorporado")',
}
for before,after in translations.items():
    if text.count(before)!=1:
        raise RuntimeError("QA anchor changed: "+before)
    text=text.replace(before,after)
# Display a useful diagnosis if the document picker is unavailable on an emulator.
text=text.replace('    if not seen:raise AssertionError("PDF not found in document picker")',
                  '    if not seen:raise AssertionError("PDF not found in Android DocumentsUI; "'
                  '+str([label(n) for n in screen() if label(n)][:70]))')
exec(compile(text,str(original),"exec"),{"__name__":"__main__"})
