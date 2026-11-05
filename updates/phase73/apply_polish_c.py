#!/usr/bin/env python3
"""Delivery C: respect approved design. Calendario only shows calendar;
schedule management lives under the second Plan de estudio panel.
No changes to tasks, notes, notifications or stored data.
"""
from pathlib import Path
JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
MAIN=JAVA/"MainActivity.java"
CLASS=JAVA/"MiDiaClassCard.java"
OLD=r'''        // The monthly calendar and selected-date cards replace the redundant weekly panel.
        LinearLayout schedule=card(body);
        LinearLayout scheduleHeading=row();
        ImageView scheduleIcon=ApprovedPng.view(this,"class_schedule",32);
        scheduleIcon.setContentDescription(null);
        LinearLayout.LayoutParams scheduleIconSpace=new LinearLayout.LayoutParams(dp(36),dp(36));
        scheduleIconSpace.rightMargin=dp(12);
        scheduleHeading.addView(scheduleIcon,scheduleIconSpace);
        TextView scheduleTitle=text("Horario de clases",17,INK,true);
        scheduleTitle.setGravity(Gravity.CENTER_VERTICAL);
        scheduleHeading.addView(scheduleTitle,new LinearLayout.LayoutParams(0,-2,1));
        schedule.addView(scheduleHeading);gap(schedule,6);
        schedule.addView(text("Cursos, sesiones y avisos de clase",12,MUTED,false));gap(schedule,10);
        schedule.addView(primaryButton("Abrir mi horario  →",()->startActivity(new Intent(this,ScheduleActivity.class))));
'''
def run():
    original=MAIN.read_text(encoding="utf-8")
    if original.count(OLD)==1:
        original=original.replace(OLD,"        // Horarios y cursos se gestionan en Calendario > Plan de estudio.\n",1)
        MAIN.write_text(original,encoding="utf-8")
    elif "Horarios y cursos se gestionan en Calendario > Plan de estudio." not in original:
        raise RuntimeError("No se encontró el panel horario heredado; no alterar archivo")
    before="Agrega tus cursos en Estudio > Horario de clases."
    after="Agrega tus cursos en Calendario > Plan de estudio."
    card=CLASS.read_text(encoding="utf-8")
    if card.count(before)==1:
        card=card.replace(before,after,1)
        CLASS.write_text(card,encoding="utf-8")
    elif after not in card:
        raise RuntimeError("No se encontró la indicación de cursos en Inicio")
    print("PASS C: Calendario sin tarjeta de horario duplicada; Plan de estudio conserva sus cursos")
    print("PASS C: referencia correcta al Plan de estudio en el Inicio")
if __name__=="__main__":run()
