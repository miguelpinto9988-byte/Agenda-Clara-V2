#!/usr/bin/env python3
"""Integrate offline, opt-outable adaptive photograph learning into 3.15.5.

Only explicit user decisions become learned rules, and they are committed
only after a successful timetable save (or an explicit saved-course correction).
"""
from pathlib import Path
import os
import tempfile

ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
STAGE=Path(__file__).resolve().parent
GRADLE=Path("AgendaClara/app/build.gradle")
ACTIVITY=ROOT/"ScheduleActivity.java"
SOURCES=("ScheduleAdaptiveRules.java","ScheduleAdaptiveMemory.java")

def once(s,old,new,label):
    count=s.count(old)
    if count!=1:raise RuntimeError(f"{label}: expected one source anchor; found {count}")
    return s.replace(old,new,1)

def patched_activity(s):
    s=once(s,
        "    private final ArrayList<Boolean> chosen=new ArrayList<>();",
        """    private final ArrayList<Boolean> chosen=new ArrayList<>();
    private final ArrayList<ScheduleAdaptiveRules.Rule> pendingAdaptive=new ArrayList<>();
    private int adaptiveReuses=0;
    private boolean adaptiveReadError=false;""","adaptive state")
    s=once(s,
        "    private void recognize(Uri uri){if(recognizing)return;recognizing=true;",
        """    private void recognize(Uri uri){if(recognizing)return;recognizing=true;
        pendingAdaptive.clear();adaptiveReuses=0;adaptiveReadError=false;""",
        "new photo clears uncommitted feedback")
    s=once(s,
        """            "Revisa los nombres, días y horas. Después confirmarás el nombre del horario.");
        if(detected!=null){""",
        """            "Revisa los nombres, días y horas. Después confirmarás el nombre del horario.");
        space(top,8);
        top.addView(btn("Aprendizaje local · Ver reglas y privacidad",
            this::showAdaptiveMemorySettings,false));
        if(detected!=null){""","review memory control")
    s=once(s,
        """        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed,rejected);
        if(pair==null){onComplete.run();return;}
        ScheduleEntry first=approved.get(pair.earlier),second=approved.get(pair.later);""",
        """        // Reuse ONLY exact, previously confirmed pairs. The final summary still
        // shows every resulting group; any new/unsafe pair asks the user.
        SchedulePhotoReview.Pair pair=null;
        for(int tries=0;tries<Math.min(250,approved.size()*approved.size()+4);tries++){
            pair=SchedulePhotoReview.nextPair(approved,confirmed,rejected);
            if(pair==null){onComplete.run();return;}
            ScheduleEntry a=approved.get(pair.earlier),b=approved.get(pair.later);
            ScheduleAdaptiveRules.Rule prior=null;
            try{prior=ScheduleAdaptiveMemory.find(this,a.course,b.course);}
            catch(RuntimeException error){
                if(!adaptiveReadError){
                    adaptiveReadError=true;
                    toast("Memoria adaptativa ilegible. Se solicitará confirmación manual.");
                }
            }
            if(!ScheduleAdaptiveRules.canReuse(prior,a.course,b.course))break;
            try{
                if(prior.together){
                    SchedulePhotoReview.acceptWithName(approved,pair,prior.canonical);
                    confirmed.add(pair.later);
                }else{
                    SchedulePhotoReview.reject(approved,pair);
                    rejected.add(SchedulePhotoReview.pairKey(pair));
                }
                adaptiveReuses++;
            }catch(RuntimeException error){break;}
        }
        if(pair==null){onComplete.run();return;}
        ScheduleEntry first=approved.get(pair.earlier),second=approved.get(pair.later);""",
        "reuse exact decisions in course review")
    s=once(s,
        """        separate.setOnClickListener(v->{
            SchedulePhotoReview.reject(approved,pair);
            rejected.add(SchedulePhotoReview.pairKey(pair));popup.dismiss();""",
        """        separate.setOnClickListener(v->{
            rememberAfterSave(first.course,second.course,false,"");
            SchedulePhotoReview.reject(approved,pair);
            rejected.add(SchedulePhotoReview.pairKey(pair));popup.dismiss();""",
        "learn separation only after save")
    s=once(s,
        """            if(pair.exact){
                SchedulePhotoReview.accept(approved,pair);
                confirmed.add(pair.later);popup.dismiss();""",
        """            if(pair.exact){
                String leftName=first.course,rightName=second.course;
                SchedulePhotoReview.accept(approved,pair);
                rememberAfterSave(leftName,rightName,true,
                    ScheduleCourseRecognition.preferred(leftName,rightName));
                confirmed.add(pair.later);popup.dismiss();""",
        "learn exact merge")
    s=once(s,
        """                SchedulePhotoReview.acceptWithName(approved,pair,title);
                confirmed.add(pair.later);
                choice.dismiss();""",
        """                SchedulePhotoReview.acceptWithName(approved,pair,title);
                rememberAfterSave(firstName,secondName,true,title);
                confirmed.add(pair.later);
                choice.dismiss();""",
        "learn user-named merge")
    s=once(s,
        """        List<String> alerts=ScheduleCourseSemanticGuard.audit(approved);
        if(!alerts.isEmpty()){""",
        """        if(adaptiveReuses>0)message.append("\\nMemoria local: ")
            .append(adaptiveReuses)
            .append(adaptiveReuses==1?" decisión reutilizada":" decisiones reutilizadas")
            .append(". Si hay un error, vuelve y pausa el aprendizaje.\\n");
        List<String> alerts=ScheduleCourseSemanticGuard.audit(approved);
        if(!alerts.isEmpty()){""",
        "explain automatic reuses in final review")
    s=once(s,
        """        detected=null;detectedTitle="";
        manualMode=false;photoSaving=false;""",
        """        // Persist ONLY explicit confirmations after the class database import
        // has completed. A cancelled photograph never trains the next import.
        commitAdaptiveFeedback();
        detected=null;detectedTitle="";
        manualMode=false;photoSaving=false;""",
        "record after successful save")
    s=once(s,
        """            .setView(panel).setNegativeButton("Mantener separados",null)
            .setPositiveButton("Unir bajo este nombre",null).create();""",
        """            .setView(panel)
            .setNegativeButton("Mantener separados",(d,w)->
                rememberSavedDecision(left.course,right.course,false,""))
            .setPositiveButton("Unir bajo este nombre",null).create();""",
        "learn saved-course separation")
    s=once(s,
        """                int updated=ScheduleDatabase.get(this).mergeCourseNames(
                    profileId,left.course,right.course,name);
                AcademicSchedules.syncFromSessions(this,profileId);""",
        """                int updated=ScheduleDatabase.get(this).mergeCourseNames(
                    profileId,left.course,right.course,name);
                rememberSavedDecision(left.course,right.course,true,name);
                AcademicSchedules.syncFromSessions(this,profileId);""",
        "learn saved-course correction")
    s=once(s,
        """        bar.addView(btn("Revisar nombres duplicados del OCR",this::reviewSavedCourseNames,false));
        if(classes.isEmpty())return;""",
        """        bar.addView(btn("Revisar nombres duplicados del OCR",this::reviewSavedCourseNames,false));
        space(bar,8);
        bar.addView(btn("Aprendizaje local · Revisar reglas",
            this::showAdaptiveMemorySettings,false));
        if(classes.isEmpty())return;""",
        "manage learned memory in existing courses")
    anchor="    private void courseList(){"
    if s.count(anchor)!=1:raise RuntimeError("Adaptive helpers: unexpected insertion point")
    helpers='''    private void rememberAfterSave(String left,String right,
                                   boolean together,String canonical){
        if(manualMode||!ScheduleAdaptiveMemory.enabled(this))return;
        if(left==null||right==null||left.length()>120||right.length()>120)return;
        pendingAdaptive.add(new ScheduleAdaptiveRules.Rule(left,right,together,
            canonical==null?"":canonical,1,System.currentTimeMillis()));
    }
    private void commitAdaptiveFeedback(){
        try{
            if(ScheduleAdaptiveMemory.enabled(this))
                for(ScheduleAdaptiveRules.Rule rule:pendingAdaptive)
                    ScheduleAdaptiveMemory.remember(this,rule.left,rule.right,
                        rule.together,rule.canonical);
        }catch(RuntimeException error){
            toast("Horario guardado. No se pudo actualizar la memoria de correcciones.");
        }finally{
            pendingAdaptive.clear();adaptiveReuses=0;
        }
    }
    private void rememberSavedDecision(String left,String right,
                                       boolean together,String canonical){
        try{
            ScheduleAdaptiveMemory.remember(this,left,right,together,canonical);
        }catch(RuntimeException error){
            toast("La corrección se aplicó, pero no se guardó el aprendizaje local.");
        }
    }
    /** Local decision ledger; no photo or OCR contents are uploaded or retained here. */
    private void showAdaptiveMemorySettings(){
        List<ScheduleAdaptiveRules.Rule> saved;
        try{saved=ScheduleAdaptiveMemory.all(this);}
        catch(RuntimeException failure){
            scheduleDialog().setTitle("Memoria no disponible")
                .setMessage("No se pudo leer el registro local. No se sobrescribirá "+
                    "automáticamente; puedes borrarlo y comenzar de nuevo.")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Borrar memoria local",(d,w)->{
                    try{ScheduleAdaptiveMemory.clear(this);}
                    catch(RuntimeException e){toast("No se pudo borrar el registro.");}
                }).show();
            return;
        }
        boolean enabled=ScheduleAdaptiveMemory.enabled(this);
        LinearLayout content=col();
        content.setPadding(dp(16),dp(8),dp(16),dp(16));
        content.addView(txt("Solo aprende cuando confirmas unir o separar cursos. "+
            "Guarda los dos nombres y tu decisión, no fotografías. "+
            "Se reutiliza solo para el mismo par de nombres y respeta niveles "+
            "y grupos. Máximo "+ScheduleAdaptiveRules.MAX_RULES+" reglas.",13,MUTED,false));
        space(content,10);
        content.addView(txt("Estado: "+(enabled?"ACTIVADO":"PAUSADO")+
            " · Decisiones: "+saved.size(),14,INK,true));
        space(content,8);
        Button toggle=btn(enabled?"Pausar aprendizaje":"Activar aprendizaje",()->{},false);
        content.addView(toggle);
        space(content,8);
        Button clear=btn("Borrar todas las reglas aprendidas",()->{},false);
        content.addView(clear);
        space(content,10);
        content.addView(txt("Toca una regla para borrarla individualmente:",12,MUTED,false));
        ArrayList<Button> entries=new ArrayList<>();
        int total=0;
        for(ScheduleAdaptiveRules.Rule rule:saved){
            if(total++>=25)break;
            String text=(rule.together?"UNIR":"SEPARAR")+" · "+
                rule.left+" / "+rule.right+
                (rule.together?" → "+rule.canonical:"");
            Button item=btn(text,()->{},false);
            content.addView(item);
            entries.add(item);
            space(content,4);
        }
        if(saved.size()>25)content.addView(txt("Se muestran las 25 reglas más recientes.",12,MUTED,false));
        ScrollView scrolling=new ScrollView(this);
        scrolling.setFillViewport(false);
        scrolling.addView(content);
        AlertDialog dialog=scheduleDialog().setTitle("Aprendizaje adaptativo local")
            .setView(scrolling).setPositiveButton("Cerrar",null).create();
        toggle.setOnClickListener(v->{
            try{ScheduleAdaptiveMemory.setEnabled(this,!enabled);
                dialog.dismiss();showAdaptiveMemorySettings();
            }catch(RuntimeException e){toast("No se pudo cambiar el ajuste.");}
        });
        clear.setOnClickListener(v->scheduleDialog()
            .setTitle("¿Borrar todo lo aprendido?")
            .setMessage("No afectará los horarios ni las clases guardadas. "+
                "Se perderán las correcciones aprendidas para próximas fotos.")
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("Borrar reglas",(d,w)->{
                try{ScheduleAdaptiveMemory.clear(this);
                    dialog.dismiss();showAdaptiveMemorySettings();
                }catch(RuntimeException e){toast("No se pudo borrar la memoria.");}
            }).show());
        for(int index=0;index<entries.size();index++){
            ScheduleAdaptiveRules.Rule rule=saved.get(index);
            entries.get(index).setOnClickListener(v->scheduleDialog()
                .setTitle("¿Olvidar esta decisión?")
                .setMessage(rule.left+" / "+rule.right+
                    (rule.together?" · Unir":" · Mantener separados"))
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Olvidar",(d,w)->{
                    try{ScheduleAdaptiveMemory.forget(this,rule.left,rule.right);
                        dialog.dismiss();showAdaptiveMemorySettings();
                    }catch(RuntimeException e){toast("No se pudo borrar la regla.");}
                }).show());
        }
        dialog.show();
    }

'''
    return s.replace(anchor,helpers+anchor,1)

def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    original=path.stat().st_mode & 0o777 if path.exists() else 0o644
    tmp=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix=".phase87-",delete=False) as fh:
            tmp=Path(fh.name);fh.write(data);fh.flush();os.fsync(fh.fileno())
        tmp.chmod(original)
        os.replace(tmp,path)
    finally:
        if tmp is not None:tmp.unlink(missing_ok=True)

def main():
    gradle=GRADLE.read_text(encoding="utf-8")
    targets={ROOT/name:STAGE/name for name in SOURCES}
    if "versionCode 73" in gradle and "versionName '3.15.6'" in gradle:
        if any(not dst.exists() or dst.read_bytes()!=src.read_bytes()
               for dst,src in targets.items()):
            raise RuntimeError("3.15.6 version present but adaptive source files differ")
        print("PASS: adaptive course learning already installed")
        return
    if gradle.count("versionCode 72")!=1 or gradle.count("versionName '3.15.5'")!=1:
        raise RuntimeError("Expected version 3.15.5 source before learning patch")
    if any(p.exists() for p in targets):
        raise RuntimeError("Adaptive source already present unexpectedly")
    proposed={target:source.read_bytes() for target,source in targets.items()}
    proposed[ACTIVITY]=patched_activity(ACTIVITY.read_text(encoding="utf-8")).encode("utf-8")
    proposed[GRADLE]=(gradle.replace("versionCode 72","versionCode 73",1)
        .replace("versionName '3.15.5'","versionName '3.15.6'",1)).encode("utf-8")
    before={p:p.read_bytes() if p.exists() else None for p in proposed}
    modified=[]
    try:
        for p,data in proposed.items():atomic(p,data);modified.append(p)
    except BaseException:
        for p in reversed(modified):
            if before[p] is None:p.unlink(missing_ok=True)
            else:atomic(p,before[p])
        raise
    print("PASS: local feedback recorded only after committed user corrections")
    print("PASS: safe exact-pair reuse and on-device learning management")
    print("PASS: Agenda Clara 3.15.6 / versionCode 73")

if __name__=="__main__":
    main()
