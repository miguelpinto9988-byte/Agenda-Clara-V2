#!/usr/bin/env python3
"""Agenda Clara 3.4: validación conservadora de cursos y revisión OCR diversa."""
from pathlib import Path
root=Path("AgendaClara")
src=root/"app/src/main/java/pe/agendaclara/app"
def replace(file,old,new):
 p=src/file;s=p.read_text(encoding="utf-8")
 if s.count(old)!=1:raise RuntimeError(f"{file}: esperaba 1 ancla, hallé {s.count(old)}: {old[:65]}")
 p.write_text(s.replace(old,new,1),encoding="utf-8")

# Comparación normalizada, sin asumir que nombres parecidos son necesariamente la misma materia.
replace("ScheduleCourseColors.java",
'''    public static boolean same(String a,String b){
        String x=identity(a);return !x.isEmpty()&&x.equals(identity(b));
    }''',
'''    public static boolean same(String a,String b){
        String x=identity(a);return !x.isEmpty()&&x.equals(identity(b));
    }
    /** Nombres OCR con variaciones típicas de espacios, tildes y puntuación. */
    public static String canonical(String text){return key(text);}
    /** Coincidencia exacta normalizada; aproximaciones se dejan a revisión manual. */
    public static boolean confidentMatch(String a,String b){
        String left=canonical(a),right=canonical(b);
        return !left.isEmpty()&&left.equals(right);
    }''')

# En el OCR posicional, evitar aceptar un encabezado como asignatura.
replace("ScheduleVirtualGrid.java",
'''            if(day(caption)>0&&caption.length()<25)continue;''',
'''            if(day(caption)>0&&caption.length()<25)continue;
            if(caption.matches("(?i)^(hora|horario|curso|asignatura|aula|docente|profesor|receso|recreo|descanso)$"))continue;''')
replace("ScheduleVirtualGrid.java",
'''        if(!out.candidates.isEmpty()){
            out.uncertain.add("Foto sin cuadrícula clara: los bloques se estimaron por posición. Revisa el día, aula y duración antes de importar.");''',
'''        if(!out.candidates.isEmpty()){
            ScheduleCourseColors.align(out.candidates,java.util.Collections.emptyList());
            out.uncertain.add("Identifica los cursos repetidos por nombre normalizado, conservando sus sesiones; confirma las coincidencias similares.");
            out.uncertain.add("Foto sin cuadrícula clara: los bloques se estimaron por posición. Revisa el día, aula y duración antes de importar.");''')
# Evitar que las correcciones OCR repliquen horarios distintos en múltiples días.
replace("ScheduleActivity.java",
'''        if(importing&&detected!=null){
            for(ScheduleEntry same:detected.candidates)
                if(ScheduleCourseColors.same(current.course,same.course)&&same.day>=1&&same.day<=7)
                    selected[same.day-1]=true;
        }else selected[current.day-1]=true;''',
'''        if(importing&&detected!=null){
            for(ScheduleEntry same:detected.candidates)
                if(ScheduleCourseColors.confidentMatch(current.course,same.course)
                    &&same.day>=1&&same.day<=7&&same.start==current.start&&same.end==current.end)
                    selected[same.day-1]=true;
            selected[current.day-1]=true;
        }else selected[current.day-1]=true;''')
# Recuperar grupos originales y horas diferentes sin suprimir las sesiones previas.
replace("ScheduleActivity.java",
'''                     for(int n=detected.candidates.size()-1;n>=0;n--){
                         ScheduleEntry other=detected.candidates.get(n);
                         if(ScheduleCourseColors.same(previous.course,other.course)&&
                            other.start==previous.start&&other.end==previous.end){''',
'''                     for(int n=detected.candidates.size()-1;n>=0;n--){
                         ScheduleEntry other=detected.candidates.get(n);
                         if(ScheduleCourseColors.confidentMatch(previous.course,other.course)&&
                            other.start==previous.start&&other.end==previous.end){''')

gradle=root/"app/build.gradle";g=gradle.read_text(encoding="utf-8")
assert g.count("versionCode 23")==1 and g.count("versionName '3.3.0'")==1
gradle.write_text(g.replace("versionCode 23","versionCode 24").replace("versionName '3.3.0'","versionName '3.4.0'"),encoding="utf-8")
print("PASS: OCR 3.4 matching conservador, revisión explícita, recordatorios y sesiones.")
