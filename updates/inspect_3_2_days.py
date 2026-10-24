#!/usr/bin/env python3
"""Agenda Clara 3.2: corregir el selector EXISTENTE de Lun-Dom para elegir varios días."""
from pathlib import Path
import re
base=Path("AgendaClara")
path=base/"app/src/main/java/pe/agendaclara/app/ScheduleActivity.java"
s=path.read_text(encoding="utf-8")
# Retirar solamente el añadido de la versión 3.1 (diálogo y botones suplementarios).
begin=s.index("    // 3.1: helper para elegir hasta los siete días")
end=s.index("    private void colorMixer(",begin)
s=s[:begin]+s[end:]
imported='''            c.addView(btn("Seleccionar días · Lunes a domingo",()->chooseScheduleDays(s,null),false));
            space(c,6);'''
assert s.count(imported)==1
s=s.replace(imported,"",1)
begin=s.index("        if(current.id==0){\n            form.addView(btn(\"Repetir este curso")
end=s.index('        form.addView(txt("Color del curso · 72 tonos rápidos + 360 tonos en catálogo"',begin)
s=s[:begin]+s[end:]
# El editor ya posee una fila de siete chips, se conserva su apariencia y se cambia solo el estado.
# Inspección por anclas con reporte explícito si la fuente difiere.
day_candidates=[line for line in s.splitlines() if "current.day" in line or "selectedDay" in line or "dayButtons" in line or "dayChoice" in line]
print("DAY_REFERENCES",*day_candidates,sep="\n")
match=re.search(r'(?s)form.addView\(txt\("Días de la semana".{0,2600}',s)
if not match:raise RuntimeError("La sección Días de la semana cambió; no alterar a ciegas")
print("DAY_SECTION",match.group(0)[:2100])
raise RuntimeError("Inspección conservadora: pendiente identificar el estado y persistencia del editor actual")
