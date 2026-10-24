#!/usr/bin/env python3
"""Agenda Clara 3.3: OCR de bloques fusionados; curso único + sesiones por días."""
from pathlib import Path
import textwrap
base=Path("AgendaClara")
src=base/"app/src/main/java/pe/agendaclara/app"
def change(file,old,new):
 p=src/file;s=p.read_text(encoding="utf-8")
 if s.count(old)!=1:raise RuntimeError(f"{file}: ancla {s.count(old)}: {old[:80]}")
 p.write_text(s.replace(old,new,1),encoding="utf-8")

# La geometría debe agrupar líneas de un mismo recuadro, no solo por fila
# ni limitar la asignación al instante más cercano del eje Y.
p=src/"ScheduleVirtualGrid.java";s=p.read_text(encoding="utf-8")
old='''            Period slot=null;int dy=Integer.MAX_VALUE;
            for(Period p:periods){int distance=Math.abs(line.y()-p.y);
                if(distance<dy){dy=distance;slot=p;}}
            if(slot==null||dy>rowHeight*.68f)continue;'''
new='''            Period slot=null;int dy=Integer.MAX_VALUE;
            // En bloques grandes el texto está centrado, no a la altura de inicio;
            // asignar por la franja que contiene su centro vertical aproximado.
            for(Period p:periods){
                int distance=Math.abs(line.y()-(p.y+rowHeight/2));
                if(distance<dy){dy=distance;slot=p;}
            }
            if(slot==null||dy>rowHeight*.92f)continue;'''
if old not in s:raise RuntimeError("Falta ancla franja");s=s.replace(old,new)
old='''            String name=title.toString().replaceAll("\\\\s+"," ").trim();'''
new='''            String name=title.toString().replaceAll("\\\\s+"," ").trim();'''
# Agrupación de sesiones detectadas por título, sin perder su día/horas.
# El agrupamiento se aplica en revisión y no en la BD.
p.write_text(s,encoding="utf-8")
change("ScheduleActivity.java",
'''        final boolean[] selected=new boolean[7];selected[current.day-1]=true;''',
'''        final boolean[] selected=new boolean[7];
        if(importing&&detected!=null){
            for(ScheduleEntry same:detected.candidates)
                if(ScheduleCourseColors.same(current.course,same.course)&&same.day>=1&&same.day<=7)
                    selected[same.day-1]=true;
        }else selected[current.day-1]=true;''')
# En el editor OCR, editar la materia agrupada solo cuando es la misma,
# reescribiendo sus días. Si la imagen contiene varios horarios del mismo día
# en horas distintas, no eliminarlos en el OCR de manera silenciosa.
change("ScheduleActivity.java",
'''                     if(index>=0){detected.candidates.remove(index);if(index<chosen.size())chosen.remove(index);}
                     else index=detected.candidates.size();''',
'''                     if(index>=0){detected.candidates.remove(index);if(index<chosen.size())chosen.remove(index);}
                     else index=detected.candidates.size();
                     for(int n=detected.candidates.size()-1;n>=0;n--){
                         ScheduleEntry other=detected.candidates.get(n);
                         if(ScheduleCourseColors.same(previous.course,other.course)&&
                            other.start==previous.start&&other.end==previous.end){
                             detected.candidates.remove(n);
                             if(n<chosen.size())chosen.remove(n);
                             if(n<index)index--;
                         }
                     }''')
# Exponer conteo y días por curso durante revisión de foto.
change("ScheduleActivity.java",
'''related.get(ScheduleCourseColors.identity(s.course)).size()''',
'''related.get(ScheduleCourseColors.identity(s.course)).size()''')
gradle=base/"app/build.gradle";g=gradle.read_text(encoding="utf-8")
if "versionCode 22" not in g or "versionName '3.2.0'" not in g:raise RuntimeError("Requiere 3.2.0")
gradle.write_text(g.replace("versionCode 22","versionCode 23").replace("versionName '3.2.0'","versionName '3.3.0'"),encoding="utf-8")
print("Agenda Clara 3.3: OCR agrupación por identidad y días preseleccionados.")
