#!/usr/bin/env python3
"""Conservative offline OCR course reconciliation, review-only merge decisions."""
from pathlib import Path
SRC=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
RES=Path('AgendaClara/app/src/main/res/drawable')
HERE=Path(__file__).resolve().parent
GRADLE=Path('AgendaClara/app/build.gradle')

def once(src,old,new,label):
    count=src.count(old)
    if count!=1:raise RuntimeError('phase36 '+label+': expected one anchor, found '+str(count))
    return src.replace(old,new,1)

def apply():
    activity=(SRC/'ScheduleActivity.java').read_text(encoding='utf-8')
    ocr=(SRC/'ScheduleOcr.java').read_text(encoding='utf-8')
    gradle=GRADLE.read_text(encoding='utf-8')
    activity=once(activity,
        '  •  Cursos estimados: '+ '"+SchedulePhotoReview.courseEstimate(detected.candidates)+' ,
        '  •  Nombres OCR: '+ '"+SchedulePhotoReview.courseEstimate(detected.candidates)+',
        'review label')
    activity=once(activity,
        '''                "  •  Revisa nombres repetidos antes de importar.",13,INK,true));''',
        '''                "  •  Cursos posibles: "+SchedulePhotoReview.provisionalEstimate(detected.candidates)+
                "  •  Confirma nombres repetidos antes de importar.",13,INK,true));''',
        'distinct course estimates')
    activity=once(activity,
        '''            confirmPhotoPairs(approved,new HashSet<Integer>(),()->{
                confirmConflicts(approved,()->{''',
        '''            confirmPhotoPairs(approved,new HashSet<Integer>(),()->{
                // Confirmed duplicate OCR rectangles are ONE session, but weekly
                // occurrences on different days remain separate sessions.
                List<ScheduleEntry> unique=SchedulePhotoReview.uniqueBlocks(approved);
                approved.clear();approved.addAll(unique);
                confirmConflicts(approved,()->{''',
        'deduplicate confirmed same-slot OCR fragments')
    start=activity.index('    /** Never auto-merge image courses, including OCR-equivalent names. */')
    end=activity.index('    private void courseList()',start)
    replacement='''    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */
    private void confirmPhotoPairs(ArrayList<ScheduleEntry> approved,
                                    Set<Integer> confirmed,Runnable onComplete){
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed);
        if(pair==null){onComplete.run();return;}
        ScheduleEntry first=approved.get(pair.earlier),second=approved.get(pair.later);
        String reason=pair.exact?"El nombre aparece más de una vez.":
            pair.relation==ScheduleCourseRecognition.Relation.TRUNCATED?
            "Una lectura parece ser una versión incompleta del otro nombre.":
            "Se detectó una posible diferencia de lectura (OCR).";
        LinearLayout panel=col();panel.setPadding(dp(16),dp(10),dp(16),dp(12));
        panel.addView(txt("¿Son el mismo curso?",18,INK,true));space(panel,8);
        panel.addView(txt(reason,13,MUTED,true));space(panel,12);
        panel.addView(txt("1. "+first.course+" · "+ScheduleEntry.dayName(first.day)+
            " "+ScheduleEntry.clock(first.start)+"–"+ScheduleEntry.clock(first.end),14,INK,true));
        space(panel,8);
        panel.addView(txt("2. "+second.course+" · "+ScheduleEntry.dayName(second.day)+
            " "+ScheduleEntry.clock(second.start)+"–"+ScheduleEntry.clock(second.end),14,INK,true));
        space(panel,12);
        panel.addView(txt("Sí: un curso con sus sesiones.  No: dos cursos distintos. "+
            "No se borra ninguna clase ni se cambian sus días u horas.",12,MUTED,true));
        space(panel,14);
        LinearLayout decisions=row();
        Button separate=btn("No · separados",()->{},false);
        Button together=btn("Sí · mismo curso",()->{},false);
        separate.setTextColor(0xffb52c48);together.setTextColor(0xff16784d);
        GradientDrawable red=new GradientDrawable(GradientDrawable.Orientation.TL_BR,
            new int[]{0xffffe6ed,0xfffff7f9});red.setCornerRadius(dp(16));red.setStroke(dp(1),0xfff3aec0);
        GradientDrawable green=new GradientDrawable(GradientDrawable.Orientation.TL_BR,
            new int[]{0xffddf9e8,0xfff2fff6});green.setCornerRadius(dp(16));green.setStroke(dp(1),0xffa6e5bd);
        separate.setBackground(red);together.setBackground(green);
        separate.setAllCaps(false);together.setAllCaps(false);
        separate.setTextSize(UiPreferences.scaled(this,12));
        together.setTextSize(UiPreferences.scaled(this,12));
        separate.setCompoundDrawablePadding(dp(6));together.setCompoundDrawablePadding(dp(6));
        android.graphics.drawable.Drawable remove=getDrawable(R.drawable.ic_course_separate);
        android.graphics.drawable.Drawable check=getDrawable(R.drawable.ic_course_merge);
        if(remove!=null){remove.setBounds(0,0,dp(24),dp(24));separate.setCompoundDrawablesRelative(remove,null,null,null);}
        if(check!=null){check.setBounds(0,0,dp(24),dp(24));together.setCompoundDrawablesRelative(check,null,null,null);}
        separate.setContentDescription("No, conservar como dos cursos distintos");
        together.setContentDescription("Sí, unir nombres en un curso sin cambiar las sesiones");
        LinearLayout.LayoutParams half=new LinearLayout.LayoutParams(0,dp(62),1);
        half.rightMargin=dp(8);decisions.addView(separate,half);
        decisions.addView(together,new LinearLayout.LayoutParams(0,dp(62),1));
        panel.addView(decisions);
        AlertDialog popup=scheduleDialog().setTitle("Corroboración de horarios")
            .setView(panel).setNegativeButton("Cancelar importación",null).create();
        separate.setOnClickListener(v->{
            SchedulePhotoReview.reject(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,onComplete);
        });
        together.setOnClickListener(v->{
            SchedulePhotoReview.accept(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,onComplete);
        });
        popup.show();
    }
'''
    activity=activity[:start]+replacement+activity[end:]
    ocr=once(ocr,
        '''            SchedulePhotoReview.courseEstimate(result.candidates)+
            " materias estimadas. No son la misma cantidad.");''',
        '''            SchedulePhotoReview.courseEstimate(result.candidates)+
            " nombres distintos, posiblemente "+SchedulePhotoReview.provisionalEstimate(result.candidates)+
            " cursos después de confirmar coincidencias. Una materia puede tener varias sesiones.");''',
        'OCR provisional distinct course count')
    ocr=once(ocr,
        '''            "cada coincidencia exacta o parecida pertenece al mismo curso.");''',
        '''            "los nombres repetidos, incompletos (p. ej. Tendencias / Tendencias Educativas) o parecidos son el mismo curso.");''',
        'OCR prefix explanation')
    gradle=once(gradle,'versionCode 36','versionCode 37','version code')
    gradle=once(gradle,"versionName '3.9.5'","versionName '3.9.6'",'version name')
    for name in ('SchedulePhotoReview.java','ScheduleCourseRecognition.java'):
        dest=SRC/name
        if name=='ScheduleCourseRecognition.java' and dest.exists():
            raise RuntimeError('Refusing overwrite existing recognizer')
        dest.write_bytes((HERE/name).read_bytes())
    for name in ('ic_course_merge.xml','ic_course_separate.xml'):
        dest=RES/name
        if dest.exists():raise RuntimeError('Refusing overwrite drawable '+name)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((HERE/name).read_bytes())
    (SRC/'ScheduleActivity.java').write_text(activity,encoding='utf-8')
    (SRC/'ScheduleOcr.java').write_text(ocr,encoding='utf-8')
    GRADLE.write_text(gradle,encoding='utf-8')
    print('PASS phase36: partial OCR names, cautious review, accessible green/red decisions and session-safe dedup')

if __name__=='__main__':apply()
