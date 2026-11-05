#!/usr/bin/env python3
"""3.13.6: Restore alerts for same-first-word, truncated and duplicate OCR subjects.
Apply to validated 3.13.5 sources. Does not compile APK or touch stored tasks.
"""
from pathlib import Path

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")

def change(source,old,new,label):
    count=source.count(old)
    if count!=1:raise RuntimeError(f"{label}: incompatible 3.13.5 sources ({count})")
    return source.replace(old,new,1)

def recognition(s):
    s=change(s,"public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT }",
               "public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT, SHARED_START }","relation")
    s=change(s,'''        // Complete-word prefix only; do not infer from a 3-letter OCR fragment or a generic subject name.
        if(shortName.length()>=8&&longName.startsWith(shortName+" ")
                &&longName.split(" ").length>sw.length
                &&!(sw.length==1&&GENERIC.contains(shortName))){
            return Relation.TRUNCATED;
        }
        int largest=Math.max(a.length(),b.length());''',
    '''        // Shared first words always require a HUMAN decision, never automatic merge.
        // Generic subjects (Historia, Investigación, Educación) still need an alert.
        if(shortName.length()>=3&&longName.startsWith(shortName+" ")
                &&longName.split(" ").length>sw.length){
            if(sw.length==1&&GENERIC.contains(shortName))return Relation.SHARED_START;
            return shortName.length()>=6?Relation.TRUNCATED:Relation.SHARED_START;
        }
        String firstA=a.split(" ")[0],firstB=b.split(" ")[0];
        if(firstA.length()>=3&&firstA.equals(firstB)){
            // e.g. Tendencias educativas vs Tendencias tecnológicas: may be different.
            return Relation.SHARED_START;
        }
        if(sw.length==1&&shortName.length()>=4&&longName.startsWith(shortName)
                &&longName.length()-shortName.length()<=3){
            return Relation.SHARED_START;
        }
        int largest=Math.max(a.length(),b.length());''',"shared-first-word handling")
    return s

def review(s):
    s=change(s,'''    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> decided){
        if(entries==null)return null;''',
    '''    public static String pairKey(Pair p){return p.earlier+":"+p.later;}
    /** Declining a suggestion must not hide OTHER matches for the same OCR label. */
    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> accepted,
                                Set<String> rejected){
        if(entries==null)return null;''',"pair decisions")
    s=change(s,"if(decided!=null&&decided.contains(i))continue;",
               "if(accepted!=null&&accepted.contains(i))continue;","accepted groups")
    s=change(s,'''            for(int j=0;j<i;j++){
                ScheduleCourseRecognition.Relation rel=ScheduleCourseRecognition.compare(''',
    '''            for(int j=0;j<i;j++){
                if(rejected!=null&&rejected.contains(j+":"+i))continue;
                ScheduleCourseRecognition.Relation rel=ScheduleCourseRecognition.compare(''',"alternative matching")
    s=change(s,'''                    rel==ScheduleCourseRecognition.Relation.OCR_VARIANT?1:0;''',
    '''                    rel==ScheduleCourseRecognition.Relation.OCR_VARIANT?1:
                    rel==ScheduleCourseRecognition.Relation.SHARED_START?1:0;''',"shared-prefix rank")
    s=change(s,'''    /** Combine COURSE identity only. All day/time/room/teacher fields remain unchanged. */''',
    '''    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> decided){
        return nextPair(entries,decided,java.util.Collections.emptySet());
    }
    /** Combine COURSE identity only. All day/time/room/teacher fields remain unchanged. */''',"legacy nextPair")
    return s

def ocr(s):
    return change(s,'''        java.util.List<ScheduleEntry> blocks=SchedulePhotoReview.uniqueBlocks(result.candidates);
        result.candidates.clear();
        result.candidates.addAll(blocks);''',
        '''        // Do not silently discard OCR candidates BEFORE the course review.
        // Exact duplicate sessions are removed only AFTER explicit corroboration.''',
        "early dedup")

def grid(s):
    return change(s,'''            if(dedup.add(key)){
                entry.color=ScheduleCourseColors.deterministic(entry.course);result.candidates.add(entry);
            }''',
    '''            if(dedup.add(key)){
                entry.color=ScheduleCourseColors.deterministic(entry.course);result.candidates.add(entry);
            }else{
                result.uncertain.add("Posible OCR duplicado: «"+entry.course+"» · "+
                    ScheduleEntry.dayName(entry.day)+" "+ScheduleEntry.clock(entry.start)+
                    "–"+ScheduleEntry.clock(entry.end)+
                    ". Comprueba si también hay otro bloque de curso.");
            }''',"grid duplicate signal")

def virtual(s):
    s=change(s,'''                if(previousY==part.y&&title.toString().endsWith(part.text))continue;''',
    '''                if(previousY==part.y&&title.toString().endsWith(part.text)){
                    out.uncertain.add("Posible repetición OCR: «"+part.text+
                        "». Verifica si existe otro curso que comienza igual.");
                    continue;
                }''',"repeated OCR word")
    return change(s,'''            if(unique.add(uniqueKey))out.candidates.add(session);''',
    '''            if(unique.add(uniqueKey))out.candidates.add(session);
            else out.uncertain.add("Posible OCR duplicado: «"+session.course+"» · "+
                    ScheduleEntry.dayName(session.day)+" "+ScheduleEntry.clock(session.start));''',
    "virtual duplicate signal")

def activity(s):
    s=change(s,'''            confirmPhotoPairs(approved,new HashSet<Integer>(),()->{''',
    '''            confirmPhotoPairs(approved,new HashSet<Integer>(),
                new HashSet<String>(),()->{''',"corroboration call")
    s=change(s,'''                    confirmPhotoName(approved);
                });''',
    '''                    confirmPhotoWarnings(approved,()->confirmPhotoName(approved));
                });''',"anomaly confirmation before title")
    s=change(s,'''    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */''',
    '''    /** The user explicitly acknowledges any OCR blocks that could not be corroborated. */
    private void confirmPhotoWarnings(ArrayList<ScheduleEntry> approved,Runnable proceed){
        if(detected==null||manualMode){proceed.run();return;}
        ArrayList<String> warnings=new ArrayList<>();
        for(String line:detected.uncertain){
            if(line==null)continue;
            String key=line.toLowerCase(java.util.Locale.ROOT);
            if(key.contains("sin curso")||key.contains("curso ambiguo")||
                    key.contains("ocr duplicado")||key.contains("repetición ocr"))
                warnings.add(line);
        }
        if(warnings.isEmpty()){proceed.run();return;}
        StringBuilder message=new StringBuilder(
            "Se encontraron "+warnings.size()+" posibles anomalías en la fotografía. "+
            "Verifica que no falte otro curso o una sesión.\\n\\n");
        for(int i=0;i<Math.min(warnings.size(),6);i++)
            message.append("• ").append(warnings.get(i)).append("\\n");
        if(warnings.size()>6)message.append("Y "+(warnings.size()-6)+" más.");
        scheduleDialog().setTitle("Corroborar anomalías de la imagen")
            .setMessage(message.toString())
            .setNegativeButton("Volver a corregir",null)
            .setPositiveButton("Revisé las anomalías · continuar",(d,w)->proceed.run())
            .show();
    }
    /** A quick yes/no confirmation for similar, truncated, or repeated OCR names. */''',
    "warning popup")
    s=change(s,'''    private void confirmPhotoPairs(ArrayList<ScheduleEntry> approved,
                                    Set<Integer> confirmed,Runnable onComplete){
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed);''',
    '''    private void confirmPhotoPairs(ArrayList<ScheduleEntry> approved,
                                    Set<Integer> confirmed,Set<String> rejected,
                                    Runnable onComplete){
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed,rejected);''',"multi-course decisions")
    s=change(s,'''        String reason=pair.exact?"El nombre aparece más de una vez.":
            pair.relation==ScheduleCourseRecognition.Relation.TRUNCATED?
            "Una lectura parece ser una versión incompleta del otro nombre.":
            "Se detectó una posible diferencia de lectura (OCR).";''',
    '''        String reason=pair.exact?"El nombre aparece más de una vez.":
            pair.relation==ScheduleCourseRecognition.Relation.TRUNCATED?
            "Una lectura parece ser una versión incompleta del otro nombre.":
            pair.relation==ScheduleCourseRecognition.Relation.SHARED_START?
            "Ambos nombres comienzan con la misma palabra, pero podrían ser cursos distintos.":
            "Se detectó una posible diferencia de lectura (OCR).";''',"explain shared word")
    s=change(s,'''        AlertDialog popup=scheduleDialog().setTitle("Corroboración de horarios")
            .setView(panel).setNegativeButton("Cancelar importación",null).create();''',
    '''        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(false);
        scroll.addView(panel);
        AlertDialog popup=scheduleDialog().setTitle("¿Son el mismo curso?")
            .setView(scroll).setNegativeButton("Volver a revisar",null).create();''',
    "full-size scrollable popup")
    s=change(s,'''            SchedulePhotoReview.reject(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,onComplete);''',
    '''            SchedulePhotoReview.reject(approved,pair);
            rejected.add(SchedulePhotoReview.pairKey(pair));popup.dismiss();
            confirmPhotoPairs(approved,confirmed,rejected,onComplete);''',
    "no should not hide next alternative")
    s=change(s,'''            SchedulePhotoReview.accept(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,onComplete);''',
    '''            SchedulePhotoReview.accept(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,rejected,onComplete);''',
    "yes confirmed for later candidate")
    return s

def main():
    edits={
        "ScheduleCourseRecognition.java":recognition,
        "SchedulePhotoReview.java":review,
        "ScheduleOcr.java":ocr,
        "ScheduleGridInterpreter.java":grid,
        "ScheduleVirtualGrid.java":virtual,
        "ScheduleActivity.java":activity,
    }
    updates={}
    for filename,transform in edits.items():
        path=JAVA/filename
        updates[path]=transform(path.read_text(encoding="utf-8"))
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 61")!=1 or gradle.count("versionName '3.13.5'")!=1:
        raise RuntimeError("Expected exact 3.13.5 sources; do not overwrite unknown version")
    updates[GRADLE]=gradle.replace("versionCode 61","versionCode 62",1).replace(
        "versionName '3.13.5'","versionName '3.13.6'",1)
    for path,value in updates.items():path.write_text(value,encoding="utf-8")
    print("PASS 3.13.6: expanded OCR course comparisons, all alternatives, duplicate alerts")
    print("PASS: photo -> corroborate anomalies -> confirm schedule name -> save")
if __name__=="__main__":main()
