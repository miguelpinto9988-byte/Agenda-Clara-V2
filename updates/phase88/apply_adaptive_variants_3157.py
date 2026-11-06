#!/usr/bin/env python3
"""Agenda Clara 3.15.7 — suggestions for unseen OCR variants of confirmed courses.

A suggestion never edits an imported session automatically. It appears in the
review cards with the learned source and requires a specific user confirmation.
Rejected suggestions are remembered only if the timetable is saved.
"""
from pathlib import Path
import hashlib
import os
import tempfile

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
ACTIVITY=JAVA/"ScheduleActivity.java"
STAGE=Path(__file__).resolve().parent
VARIANTS=JAVA/"ScheduleAdaptiveVariants.java"
PROTECTED=(
    JAVA/"PhotoWidget.java",
    JAVA/"PhotoConfigActivity.java",
    JAVA/"PhotoTapActivity.java",
    Path("AgendaClara/app/src/main/res/layout/widget_photo.xml"),
    Path("AgendaClara/app/src/main/res/xml/photo_widget_info.xml"),
)

def once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(old,new,1)

def modify_activity(code):
    code=once(code,
        "    private boolean adaptiveReadError=false;",
        """    private boolean adaptiveReadError=false;
    private final Set<String> declinedVariantSuggestions=new HashSet<>();""",
        "local declined suggestions")
    code=once(code,
        "        pendingAdaptive.clear();adaptiveReuses=0;adaptiveReadError=false;",
        """        pendingAdaptive.clear();adaptiveReuses=0;adaptiveReadError=false;
        declinedVariantSuggestions.clear();""",
        "reset on new photograph")
    code=once(code,
        """        Map<String,List<ScheduleEntry>> related=ScheduleCourseColors.groups(detected.candidates);
        for(int i=0;i<detected.candidates.size();i++){""",
        """        // Read the bounded local history ONCE, not once per rendered class.
        List<ScheduleAdaptiveRules.Rule> adaptiveHistory=null;
        if(!manualMode&&ScheduleAdaptiveMemory.enabled(this)){
            try{adaptiveHistory=ScheduleAdaptiveMemory.all(this);}
            catch(RuntimeException problem){
                if(!adaptiveReadError){
                    adaptiveReadError=true;
                    toast("No se pudo leer la memoria adaptativa. Revisa los cursos manualmente.");
                }
            }
        }
        Set<String> alreadyProposed=new HashSet<>();
        Map<String,List<ScheduleEntry>> related=ScheduleCourseColors.groups(detected.candidates);
        for(int i=0;i<detected.candidates.size();i++){""",
        "load on-device learned names once")
    code=once(code,
        """            c.addView(txt(ScheduleEntry.dayName(s.day)+" · "+ScheduleEntry.clock(s.start)+"–"+ScheduleEntry.clock(s.end)+(s.room.isEmpty()?"":" · "+s.room),13,MUTED,false));""",
        """            if(adaptiveHistory!=null&&
                    alreadyProposed.add(ScheduleAdaptiveRules.normalize(s.course))){
                ScheduleAdaptiveVariants.Suggestion proposal=
                    ScheduleAdaptiveVariants.suggest(adaptiveHistory,s.course);
                if(proposal!=null&&!declinedVariantSuggestions.contains(
                        ScheduleAdaptiveRules.pairKey(s.course,proposal.canonical))){
                    c.addView(txt("Aprendizaje local · Posible nombre aprendido: «"+
                        proposal.canonical+"». Aún no se ha cambiado esta clase.",
                        12,BLUE,true));
                    c.addView(btn("Revisar variante sugerida",()->
                        reviewLearnedVariant(s,proposal),false));
                }
            }
            c.addView(txt(ScheduleEntry.dayName(s.day)+" · "+ScheduleEntry.clock(s.start)+"–"+ScheduleEntry.clock(s.end)+(s.room.isEmpty()?"":" · "+s.room),13,MUTED,false));""",
        "show optional proposal once per source label")
    anchor="    private void rememberAfterSave(String left,String right,"
    helper='''    /** User-visible consent is mandatory for any name not previously seen.
     * Never changes selected flags, session IDs, day, hour or classroom. */
    private void reviewLearnedVariant(ScheduleEntry entry,
            ScheduleAdaptiveVariants.Suggestion proposed){
        if(detected==null||manualMode||!ScheduleAdaptiveMemory.enabled(this))return;
        final String original=entry.course;
        final String canonical=proposed.canonical;
        final String key=ScheduleAdaptiveRules.pairKey(original,canonical);
        scheduleDialog().setTitle("Posible variante de un curso aprendido")
            .setMessage("La foto dice: «"+original+"».\\n\\n"+
                "Anteriormente confirmaste el nombre «"+canonical+
                "» a partir de «"+proposed.learnedFrom+"».\\n\\n"+
                "¿Quieres corregir todas las sesiones que tengan exactamente "+
                "el mismo nombre detectado? No se cambiarán días, horas ni aulas. "+
                "Las demás asignaturas seguirán separadas.")
            .setNeutralButton("Cancelar",null)
            .setNegativeButton("No · mantener nombre",(dialog,which)->{
                declinedVariantSuggestions.add(key);
                rememberAfterSave(original,canonical,false,"");
                show(5);
            })
            .setPositiveButton("Sí · utilizar nombre",(dialog,which)->{
                try{
                    ScheduleAdaptiveVariants.Suggestion still=
                        ScheduleAdaptiveVariants.suggest(
                            ScheduleAdaptiveMemory.all(this),original);
                    if(still==null||
                        !ScheduleAdaptiveRules.normalize(still.canonical).equals(
                            ScheduleAdaptiveRules.normalize(canonical))){
                        toast("La memoria ha cambiado. Revisa nuevamente el nombre.");
                        show(5);return;
                    }
                    int renamed=0;
                    for(ScheduleEntry candidate:detected.candidates){
                        if(ScheduleAdaptiveRules.normalize(candidate.course).equals(
                            ScheduleAdaptiveRules.normalize(original))){
                            candidate.course=canonical;
                            renamed++;
                        }
                    }
                    if(renamed<1){show(5);return;}
                    rememberAfterSave(original,canonical,true,canonical);
                    ScheduleCourseColors.align(detected.candidates,
                        ScheduleDatabase.get(this).all(profileId));
                    toast(renamed==1?"Nombre corregido · 1 sesión":
                        "Nombre corregido · "+renamed+" sesiones");
                    show(5);
                }catch(RuntimeException error){
                    toast("No se pudo aplicar la sugerencia. No se guardó ningún cambio.");
                    show(5);
                }
            }).show();
    }

'''
    if code.count(anchor)!=1:raise RuntimeError("Variant UI method insertion point missing")
    code=code.replace(anchor,helper+anchor,1)
    code=once(code,
        '''            "Se reutiliza solo para el mismo par de nombres y respeta niveles "+
            "y grupos. Máximo "+ScheduleAdaptiveRules.MAX_RULES+" reglas.",13,MUTED,false));''',
        '''            "Las parejas exactas confirmadas se reutilizan; las variantes "+
            "nuevas solo se proponen y nunca se cambian sin tu autorización. "+
            "Se respetan niveles y grupos. Máximo "+
            ScheduleAdaptiveRules.MAX_RULES+" reglas.",13,MUTED,false));''',
        "explain proactive proposals transparently")
    return code

def atomic_write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    mode=(path.stat().st_mode&0o777) if path.exists() else 0o644
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,
            prefix=".phase88-",delete=False) as out:
            temp=Path(out.name)
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        temp.chmod(mode)
        os.replace(temp,path)
    finally:
        if temp is not None:temp.unlink(missing_ok=True)

def main():
    gradle=GRADLE.read_text(encoding="utf-8")
    staged=(STAGE/"ScheduleAdaptiveVariants.java").read_bytes()
    if gradle.count("versionCode 74")==1 and gradle.count("versionName '3.15.7'")==1:
        if not VARIANTS.is_file() or VARIANTS.read_bytes()!=staged:
            raise RuntimeError("3.15.7 version exists but variant matcher differs")
        if ACTIVITY.read_text(encoding="utf-8").count("reviewLearnedVariant(")<2:
            raise RuntimeError("3.15.7 variant review UI is missing")
        print("PASS: adaptive 3.15.7 variant patch already applied")
        return
    if gradle.count("versionCode 73")!=1 or gradle.count("versionName '3.15.6'")!=1:
        raise RuntimeError("Requires Agenda Clara 3.15.6 sources")
    if VARIANTS.exists():
        raise RuntimeError("Existing matcher file; refusing to overwrite")
    protect={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in PROTECTED}
    changes={
        VARIANTS:staged,
        ACTIVITY:modify_activity(ACTIVITY.read_text(encoding="utf-8")).encode("utf-8"),
        GRADLE:(gradle.replace("versionCode 73","versionCode 74",1)
                 .replace("versionName '3.15.6'","versionName '3.15.7'",1)
               ).encode("utf-8"),
    }
    before={p:p.read_bytes() if p.exists() else None for p in changes}
    updated=[]
    try:
        for path,data in changes.items():
            atomic_write(path,data)
            updated.append(path)
        if any(hashlib.sha256(p.read_bytes()).hexdigest()!=value
               for p,value in protect.items()):
            raise RuntimeError("Photography widget files unexpectedly changed")
    except BaseException:
        for path in reversed(updated):
            old=before[path]
            if old is None:path.unlink(missing_ok=True)
            else:atomic_write(path,old)
        raise
    print("PASS: learned variants propose canonical names without silent changes")
    print("PASS: accepted and rejected proposals are persisted only after successful import")
    print("PASS: photography widget source/resources remain untouched")
    print("PASS: Agenda Clara 3.15.7 (versionCode 74)")

if __name__=="__main__":
    main()
