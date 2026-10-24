#!/usr/bin/env python3
"""Agenda Clara 3.8.1: three-stage photo timetable recognition and per-day edits.
Run after phase16/apply_3_8_0.py; preserve existing course data.
"""
from pathlib import Path
import textwrap

root=Path("AgendaClara")
src=root/"app/src/main/java/pe/agendaclara/app"
def one(file,old,new):
    p=src/file
    text=p.read_text(encoding="utf-8")
    count=text.count(old)
    if count!=1:raise RuntimeError(f"3.8.1 {file}: expected 1 anchor, found {count}: {old[:90]}")
    p.write_text(text.replace(old,new,1),encoding="utf-8")
def add(file,code):
    p=src/file
    if p.exists():raise RuntimeError("Already exists: "+str(p))
    p.write_text(textwrap.dedent(code).lstrip(),encoding="utf-8")

add("SchedulePhotoReview.java",r'''
package pe.agendaclara.app;

import java.util.*;
import java.util.regex.*;

/** Offline phase-1 overview and phase-3 human-confirmed course identity.
 * A course has independent sessions; matching never changes a session's time or weekday.
 * All comparisons are suggestions: no fuzzy pair can merge without explicit confirmation. */
public final class SchedulePhotoReview {
    private SchedulePhotoReview(){}
    public static final class Overview {
        public final int textLines,weekdayHeaders,timeLabels;
        Overview(int lines,int days,int times){textLines=lines;weekdayHeaders=days;timeLabels=times;}
    }
    public static final class Pair {
        public final int earlier,later;
        public final boolean exact;
        Pair(int a,int b,boolean e){earlier=a;later=b;exact=e;}
    }
    public static Overview overview(List<ScheduleGridInterpreter.Line> lines){
        if(lines==null)return new Overview(0,0,0);
        Set<String> days=new HashSet<>();
        int times=0,readable=0;
        for(ScheduleGridInterpreter.Line l:lines){
            String value=l.text.trim();
            if(value.isEmpty())continue;
            readable++;
            String lower=ScheduleParser.fold(value).trim();
            Matcher m=Pattern.compile("(?i)^(lunes|martes|miercoles|jueves|viernes|sabado|domingo|lun|mar|mie|jue|vie|sab|dom)\\b").matcher(lower);
            if(m.find())days.add(m.group(1).substring(0,3));
            if(Pattern.compile("(?i)\\b\\d{1,2}[:h.]\\d{2}\\b").matcher(value).find())times++;
        }
        return new Overview(readable,days.size(),times);
    }
    public static List<ScheduleEntry> uniqueBlocks(List<ScheduleEntry> raw){
        ArrayList<ScheduleEntry> out=new ArrayList<>();
        if(raw==null)return out;
        for(ScheduleEntry s:raw){
            boolean already=false;
            for(ScheduleEntry old:out)
                if(old.day==s.day&&old.start==s.start&&old.end==s.end
                   &&ScheduleCourseColors.same(old.course,s.course)){already=true;break;}
            if(!already)out.add(s);
        }
        return out;
    }
    public static int courseEstimate(Collection<ScheduleEntry> list){
        HashSet<String> keys=new HashSet<>();
        if(list!=null)for(ScheduleEntry s:list)keys.add(ScheduleCourseColors.identity(s.course));
        keys.remove("");
        return keys.size();
    }
    private static String finalNumber(String title){
        String k=ScheduleCourseColors.key(title);
        Matcher m=Pattern.compile("(?:^| )(i|ii|iii|iv|v|vi|vii|viii|ix|x|[0-9]+)$").matcher(k);
        return m.find()?m.group(1):"";
    }
    private static boolean possibleSame(String a,String b){
        if(a==null||b==null||a.trim().isEmpty()||b.trim().isEmpty())return false;
        if(a.matches("(?i).*\\(grupo [0-9]+\\)$")||b.matches("(?i).*\\(grupo [0-9]+\\)$"))return false;
        String la=finalNumber(a),lb=finalNumber(b);
        if(!la.equals(lb))return false; // "Historia I" != "Historia II"; also avoid dropping a level.
        if(ScheduleCourseColors.same(a,b))return true;
        String x=ScheduleCourseColors.key(a),y=ScheduleCourseColors.key(b);
        if(x.length()<9||y.length()<9)return false;
        String[] ax=x.split(" "),by=y.split(" ");
        if(ax.length==0||by.length==0||!ax[0].substring(0,Math.min(3,ax[0].length()))
           .equals(by[0].substring(0,Math.min(3,by[0].length()))))return false;
        int n=x.length(),m=y.length();
        if(Math.abs(n-m)>Math.max(n,m)*.18)return false;
        int[] d=new int[m+1];
        for(int j=0;j<=m;j++)d[j]=j;
        for(int i=1;i<=n;i++){
            int previous=d[0];d[0]=i;
            for(int j=1;j<=m;j++){
                int temp=d[j];
                d[j]=Math.min(Math.min(d[j]+1,d[j-1]+1),
                    previous+(x.charAt(i-1)==y.charAt(j-1)?0:1));
                previous=temp;
            }
        }
        return d[m]<=Math.max(2,(int)Math.floor(Math.max(n,m)*.16));
    }
    /** Only the later occurrence needs a decision. Earliest matching item is the reference. */
    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> decided){
        for(int i=1;i<entries.size();i++){
            if(decided.contains(i))continue;
            ScheduleEntry target=entries.get(i);
            for(int j=0;j<i;j++){
                ScheduleEntry reference=entries.get(j);
                if(possibleSame(reference.course,target.course))
                    return new Pair(j,i,ScheduleCourseColors.same(reference.course,target.course));
            }
        }
        return null;
    }
    public static void accept(List<ScheduleEntry> entries,Pair pair){
        ScheduleEntry earlier=entries.get(pair.earlier),later=entries.get(pair.later);
        later.course=earlier.course;later.color=earlier.color;
        // Preserve latter's day, start, end, classroom, instructor and notifications.
    }
    public static void reject(List<ScheduleEntry> entries,Pair pair){
        ScheduleEntry later=entries.get(pair.later);
        String base=later.course.replaceAll("(?i)\\s*\\(grupo [0-9]+\\)$","").trim();
        int n=2;
        String proposal;
        boolean used;
        do{
            String suffix=" (grupo "+n+++ ")";
            proposal=base.substring(0,Math.min(base.length(),120-suffix.length()))+suffix;
            used=false;
            for(int j=0;j<entries.size();j++)if(j!=pair.later&&
                ScheduleCourseColors.same(entries.get(j).course,proposal)){used=true;break;}
        }while(used);
        later.course=proposal;
        later.color=ScheduleCourseColors.deterministic(proposal);
    }
}
''')

# Three distinct stages: overall structure -> per-class block detection -> person corroborates.
one("ScheduleOcr.java",
'''        ScheduleParser.Result table=ScheduleGridInterpreter.parse(lines,tiles,imageWidth,imageHeight);''',
'''        // 1. Vistazo general: contabilizar encabezados, horas y texto reconocible.
        SchedulePhotoReview.Overview glance=SchedulePhotoReview.overview(lines);
        // 2. Vistazo específico: identificar cada bloque independiente de clase.
        ScheduleParser.Result table=ScheduleGridInterpreter.parse(lines,tiles,imageWidth,imageHeight);''')
one("ScheduleOcr.java",
'''            return table;
        }
        ScheduleParser.Result virtual=ScheduleVirtualGrid.parse(lines,imageWidth,imageHeight);
        if(!virtual.candidates.isEmpty())return virtual;
        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        fallback.uncertain.add("No se pudo reconstruir la cuadrícula de la imagen. La lectura de texto es aproximada: verifica todas las horas antes de guardar.");
        return fallback;''',
'''            return corroboration(table,glance);
        }
        ScheduleParser.Result virtual=ScheduleVirtualGrid.parse(lines,imageWidth,imageHeight);
        if(!virtual.candidates.isEmpty())return corroboration(virtual,glance);
        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        fallback.uncertain.add("No se pudo reconstruir la cuadrícula de la imagen. La lectura de texto es aproximada: verifica todas las horas antes de guardar.");
        return corroboration(fallback,glance);''')
one("ScheduleOcr.java",
'''    private ScheduleOcr(){}''',
'''    private ScheduleOcr(){}
    private static ScheduleParser.Result corroboration(ScheduleParser.Result result,
                                                      SchedulePhotoReview.Overview glance){
        java.util.List<ScheduleEntry> blocks=SchedulePhotoReview.uniqueBlocks(result.candidates);
        result.candidates.clear();
        result.candidates.addAll(blocks);
        result.uncertain.add("Etapa 1/3 · Vista general: "+glance.weekdayHeaders+
            " columnas de días, "+glance.timeLabels+" referencias de horas y "+
            glance.textLines+" líneas de texto.");
        result.uncertain.add("Etapa 2/3 · Lectura por cursos: "+
            result.candidates.size()+" sesiones o bloques detectados; "+
            SchedulePhotoReview.courseEstimate(result.candidates)+
            " materias estimadas. No son la misma cantidad.");
        result.uncertain.add("Etapa 3/3 · Corroboración: al guardar te preguntaremos si "+
            "cada coincidencia exacta o parecida pertenece al mismo curso.");
        return result;
    }''')

one("ScheduleActivity.java",
'''        TextView symbol=txt("▧  Imagen del horario",20,BLUE,true);''',
'''        c.addView(txt("ETAPA 1 · Vista general  →  ETAPA 2 · Cursos  →  ETAPA 3 · Corroboración",12,BLUE,true));
        space(c,10);
        TextView symbol=txt("▧  Imagen del horario",20,BLUE,true);''')

one("ScheduleActivity.java",
'''    private void review(){LinearLayout top=card();head(top,"Revisa antes de guardar","Reconocimos "+(detected==null?0:detected.candidates.size())+" bloques de clase. Si un curso abarca varias filas, se toma el inicio de la primera y el fin de la última. Revisa antes de guardar.");''',
'''    private void review(){LinearLayout top=card();
        head(top,"3/3 · Corroborar cursos","Las sesiones semanales no son cursos diferentes. Una misma materia puede aparecer varios días, con horas distintas.");
        if(detected!=null){
            top.addView(txt("Etapa 1 ✓ Vista general  ·  Etapa 2 ✓ Cursos por bloque  ·  Etapa 3 ◉ Confirmación",12,BLUE,true));
            space(top,8);
            top.addView(txt("Bloques: "+detected.candidates.size()+
                "  •  Cursos estimados: "+SchedulePhotoReview.courseEstimate(detected.candidates)+
                "  •  Revisa nombres repetidos antes de importar.",13,INK,true));
        }''')

one("ScheduleActivity.java",
'''            c.addView(btn("✎  Corregir datos",()->editor(s,()->{chosen.set(index,true);show(5);}),false));''',
'''            c.addView(btn("✎  Editar día y hora de este bloque",()->editor(s,()->show(5)),false));''')

one("ScheduleActivity.java",
'''            ArrayList<ScheduleEntry> approved=new ArrayList<>();for(int i=0;i<detected.candidates.size();i++)if(chosen.get(i))approved.add(detected.candidates.get(i));
            if(approved.isEmpty()){toast("Selecciona alguna clase o usa la creación manual.");return;}
            confirmConflicts(approved,()->{ScheduleCourseColors.align(approved,ScheduleDatabase.get(this).all());int added=ScheduleDatabase.get(this).importReviewed(approved);ScheduleReminders.rebuild(this);toast("Clases nuevas guardadas: "+added);detected=null;show(2);});''',
'''            ArrayList<ScheduleEntry> approved=new ArrayList<>();
            for(int i=0;i<detected.candidates.size();i++)if(chosen.get(i))
                approved.add(detected.candidates.get(i).copy());
            if(approved.isEmpty()){toast("Selecciona alguna clase o usa la creación manual.");return;}
            // 3. Corroboration requires explicit yes/no even for identical OCR course labels.
            confirmPhotoPairs(approved,new HashSet<Integer>(),()->{
                confirmConflicts(approved,()->{
                    ScheduleCourseColors.align(approved,ScheduleDatabase.get(this).all());
                    int added=ScheduleDatabase.get(this).importReviewed(approved);
                    ScheduleReminders.rebuild(this);
                    toast("Bloques guardados: "+added+" · cursos: "+
                        SchedulePhotoReview.courseEstimate(approved));
                    detected=null;show(2);
                });
            });''')

one("ScheduleActivity.java",
'''    private void courseList(){List<ScheduleEntry> classes=ScheduleDatabase.get(this).all();''',
'''    /** Never auto-merge image courses, including OCR-equivalent names. */
    private void confirmPhotoPairs(ArrayList<ScheduleEntry> approved,
                                    Set<Integer> confirmed,Runnable onComplete){
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed);
        if(pair==null){onComplete.run();return;}
        ScheduleEntry first=approved.get(pair.earlier),second=approved.get(pair.later);
        String message="¿Estos dos bloques corresponden al MISMO curso?"+
            "\\n\\n1) "+first.course+" · "+ScheduleEntry.dayName(first.day)+
            " "+ScheduleEntry.clock(first.start)+"–"+ScheduleEntry.clock(first.end)+
            "\\n2) "+second.course+" · "+ScheduleEntry.dayName(second.day)+
            " "+ScheduleEntry.clock(second.start)+"–"+ScheduleEntry.clock(second.end)+
            "\\n\\nSi aceptas, será un curso con dos sesiones independientes. "+
            "Si rechazas, se guardarán como dos cursos. Sus horas no se modificarán.";
        new AlertDialog.Builder(this).setTitle(pair.exact?"Confirmar curso repetido":"¿Nombres parecidos?")
            .setMessage(message)
            .setPositiveButton("Sí · mismo curso",(d,w)->{
                SchedulePhotoReview.accept(approved,pair);
                confirmed.add(pair.later);confirmPhotoPairs(approved,confirmed,onComplete);
            })
            .setNegativeButton("No · cursos distintos",(d,w)->{
                SchedulePhotoReview.reject(approved,pair);
                confirmed.add(pair.later);confirmPhotoPairs(approved,confirmed,onComplete);
            })
            .setNeutralButton("Cancelar importación",null).show();
    }
    private void courseList(){List<ScheduleEntry> classes=ScheduleDatabase.get(this).all();''')

one("ScheduleActivity.java",
'''        if(importing&&detected!=null){
            for(ScheduleEntry same:detected.candidates)
                if(ScheduleCourseColors.confidentMatch(current.course,same.course)
                    &&same.day>=1&&same.day<=7&&same.start==current.start&&same.end==current.end)
                    selected[same.day-1]=true;
            selected[current.day-1]=true;
        }else selected[current.day-1]=true;LinearLayout dayRow=row();''',
'''        // Changing Tuesday must never overwrite the same course's Monday hours.
        selected[current.day-1]=true;
        form.addView(txt("Cada día tiene su propio horario. Aquí solo se edita el día seleccionado; "+
            "puedes agregar otro día manualmente sin cambiar los existentes.",12,MUTED,false));
        space(form,7);
        LinearLayout dayRow=row();''')

one("ScheduleActivity.java",
'''                     for(int n=detected.candidates.size()-1;n>=0;n--){
                         ScheduleEntry other=detected.candidates.get(n);
                         if(ScheduleCourseColors.confidentMatch(previous.course,other.course)&&
                            other.start==previous.start&&other.end==previous.end){
                             detected.candidates.remove(n);
                             if(n<chosen.size())chosen.remove(n);
                             if(n<index)index--;
                         }
                     }
                     int insert=index;''',
'''                     // Only replace the chosen OCR block. Other weekly occurrences,
                     // even with the same course and time, must remain intact.
                     int insert=index;''')

# Do not duplicate an existing normalized slot when importing a differently accented name.
one("ScheduleDatabase.java",
'''        ScheduleCourseColors.align(items,all());
        for(ScheduleEntry s:items){if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))continue;try(Cursor c=db.rawQuery("SELECT 1 FROM sessions WHERE day=? AND start_min=? AND end_min=? AND course=? COLLATE NOCASE LIMIT 1",new String[]{""+s.day,""+s.start,""+s.end,s.course.trim()})){if(c.moveToFirst())continue;}
            if(db.insert("sessions",null,values(s))>0)inserted++;''',
'''        ScheduleCourseColors.align(items,all());
        List<ScheduleEntry> existing=all();
        for(ScheduleEntry s:items){
            if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))continue;
            boolean duplicate=false;
            for(ScheduleEntry old:existing){
                if(old.day==s.day&&old.start==s.start&&old.end==s.end&&
                   ScheduleCourseColors.same(old.course,s.course)){duplicate=true;break;}
            }
            if(duplicate)continue;
            if(db.insert("sessions",null,values(s))>0){inserted++;existing.add(s.copy());}''')

p=root/"app/build.gradle"
gradle=p.read_text(encoding="utf-8")
assert gradle.count("versionCode 28")==1 and gradle.count("versionName '3.8.0'")==1
p.write_text(gradle.replace("versionCode 28","versionCode 29")
                   .replace("versionName '3.8.0'","versionName '3.8.1'"),encoding="utf-8")
print("PASS: 3.8.1 three-phase image OCR review and independent weekly course sessions")
