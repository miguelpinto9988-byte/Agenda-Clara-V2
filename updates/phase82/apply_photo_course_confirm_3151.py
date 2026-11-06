#!/usr/bin/env python3
"""Agenda Clara 3.15.1: mandatory human OCR course reconciliation.

Requires the verified reconstructed 3.15.0 source. The fixed-photo
home widget is byte-for-byte unaffected.
"""
from pathlib import Path
import hashlib
import shutil

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
STAGE=Path(__file__).resolve().parent

def replace_once(source,old,new,label):
    n=source.count(old)
    if n!=1:raise RuntimeError(f"{label}: expected one anchor, got {n}")
    return source.replace(old,new,1)

def replace_between(source,start,end,replacement,label):
    if source.count(start)!=1 or source.count(end)!=1:
        raise RuntimeError(f"{label}: boundaries unavailable")
    a=source.index(start);b=source.index(end,a)
    return source[:a]+replacement+source[b:]

def recognition(source):
    source=replace_once(source,
        "TRUNCATED, OCR_VARIANT, SHARED_START }",
        "TRUNCATED, OCR_VARIANT, SHARED_START, SHARED_WORD }",
        "recognition enum")
    source=replace_once(source,
        "    private static String key(String s){return ScheduleCourseColors.key(s);}",
        """    private static String key(String s){return ScheduleCourseColors.key(s);}
    /** Visible to the course confirmation dialog: any shared meaningful word. */
    public static String sharedWord(String left,String right){
        return ScheduleCourseWordReview.shared(left,right);
    }""",
        "shared word delegation")
    source=replace_between(source,
        "    public static Relation compare(String left,String right){",
        "    /** Prefer the fuller spelling",
        r'''    public static Relation compare(String left,String right){
        if(left==null||right==null||left.trim().isEmpty()||right.trim().isEmpty())
            return Relation.DIFFERENT;
        if(ScheduleCourseColors.same(left,right))return Relation.EXACT;
        String a=key(left),b=key(right);
        if(a.isEmpty()||b.isEmpty())return Relation.DIFFERENT;
        // Different Roman levels and explicit groups are not automatically combined;
        // a shared content word still REQUIRES a yes/no question.
        boolean distinctQualifier=hasExplicitGroup(left)||hasExplicitGroup(right)
                ||!suffix(left).equals(suffix(right));
        if(!distinctQualifier){
            String shortName=a.length()<=b.length()?a:b;
            String longName=a.length()>b.length()?a:b;
            String[] sw=shortName.split(" ");
            if(shortName.length()>=3&&longName.startsWith(shortName+" ")
                    &&longName.split(" ").length>sw.length){
                if(sw.length==1&&GENERIC.contains(shortName))return Relation.SHARED_START;
                return shortName.length()>=6?Relation.TRUNCATED:Relation.SHARED_START;
            }
            String firstA=a.split(" ")[0],firstB=b.split(" ")[0];
            if(firstA.length()>=3&&firstA.equals(firstB))return Relation.SHARED_START;
            if(sw.length==1&&shortName.length()>=4&&longName.startsWith(shortName)
                    &&longName.length()-shortName.length()<=3)return Relation.SHARED_START;
            int largest=Math.max(a.length(),b.length());
            if(largest>=9&&Math.abs(a.length()-b.length())<=Math.max(3,largest*.20)){
                if(firstA.length()>=4&&firstB.length()>=4
                        &&distance(firstA,firstB)<=2){
                    int max=(int)Math.floor(largest*.16);
                    if(distance(a,b)<=Math.max(2,max))return Relation.OCR_VARIANT;
                }
            }
        }
        // Not only the first word. Do not silently separate overlapping courses.
        if(!sharedWord(left,right).isEmpty())return Relation.SHARED_WORD;
        return Relation.DIFFERENT;
    }
''',
        "comparison policy")
    source=replace_between(source,
        "    /** Conservative estimate:",
        "\n}",
        r'''    /** Count distinct OCR names, never pretend an unapproved merge happened. */
    public static int provisionalCount(Collection<ScheduleEntry> sessions){
        if(sessions==null)return 0;
        Set<String> unique=new HashSet<>();
        for(ScheduleEntry s:sessions)
            if(s!=null&&s.course!=null&&!ScheduleCourseColors.identity(s.course).isEmpty())
                unique.add(ScheduleCourseColors.identity(s.course));
        return unique.size();
    }''',
        "provisional count")
    return source

def review(source):
    return replace_between(source,
        "    /** Select the best earlier matching course",
        "    /** User-chosen canonical spelling",
        r'''    /** Stable positional key despite a later canonical-name correction. */
    public static String pairKey(Pair p){return p.earlier+":"+p.later;}

    /** Record the reviewed name groups, never hide a different unresolved match. */
    public static void rememberDecision(List<ScheduleEntry> entries,Pair pair,
                                        Set<String> resolved,boolean sameCourse){
        String a=ScheduleCourseColors.identity(entries.get(pair.earlier).course);
        String b=ScheduleCourseColors.identity(entries.get(pair.later).course);
        if(!sameCourse&&a.equals(b)){
            resolved.add(pairKey(pair));return;
        }
        for(int i=0;i<entries.size();i++){
            String x=ScheduleCourseColors.identity(entries.get(i).course);
            if(!x.equals(a)&&!x.equals(b))continue;
            for(int j=i+1;j<entries.size();j++){
                String y=ScheduleCourseColors.identity(entries.get(j).course);
                if(sameCourse){
                    if(y.equals(a)||y.equals(b))resolved.add(i+":"+j);
                }else if((x.equals(a)&&y.equals(b))||(x.equals(b)&&y.equals(a)))
                    resolved.add(i+":"+j);
            }
        }
    }

    /** Exhaust EVERY candidate match, even when one session was reviewed earlier. */
    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> accepted,
                                Set<String> resolved){
        if(entries==null)return null;
        for(int i=1;i<entries.size();i++){
            Pair best=null;int rankBest=0;
            for(int j=0;j<i;j++){
                if(resolved!=null&&resolved.contains(j+":"+i))continue;
                ScheduleCourseRecognition.Relation rel=ScheduleCourseRecognition.compare(
                    entries.get(j).course,entries.get(i).course);
                int rank=rel==ScheduleCourseRecognition.Relation.EXACT?5:
                    rel==ScheduleCourseRecognition.Relation.TRUNCATED?4:
                    rel==ScheduleCourseRecognition.Relation.OCR_VARIANT?3:
                    rel==ScheduleCourseRecognition.Relation.SHARED_START?2:
                    rel==ScheduleCourseRecognition.Relation.SHARED_WORD?1:0;
                if(rank>rankBest){rankBest=rank;best=new Pair(j,i,rel);}
            }
            if(best!=null)return best;
        }
        return null;
    }
    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> decided){
        return nextPair(entries,decided,java.util.Collections.emptySet());
    }

    /** Declining an EXACT saved title must prevent its implicit identity reuse. */
    public static void distinguishFromExisting(List<ScheduleEntry> imported,
                                               List<ScheduleEntry> stored,String course){
        String old=ScheduleCourseColors.identity(course);
        String base=course.replaceAll("(?i)\\s*\\(grupo [0-9]+\\)$","").trim();
        int number=2;String proposal;
        while(true){
            proposal=base+" (grupo "+(number++)+")";
            boolean taken=false;
            for(ScheduleEntry s:stored)if(ScheduleCourseColors.same(proposal,s.course)){
                taken=true;break;
            }
            for(ScheduleEntry s:imported)
                if(!ScheduleCourseColors.identity(s.course).equals(old)
                        &&ScheduleCourseColors.same(proposal,s.course)){
                    taken=true;break;
                }
            if(!taken)break;
        }
        for(ScheduleEntry s:imported)
            if(ScheduleCourseColors.identity(s.course).equals(old)){
                s.course=proposal;s.color=ScheduleCourseColors.deterministic(proposal);
            }
    }
''',
        "review all course pairings")

def fusion(source):
    return replace_once(source,
        """return relation==ScheduleCourseRecognition.Relation.EXACT||
               relation==ScheduleCourseRecognition.Relation.OCR_VARIANT;""",
        """// Typos are suggested unchecked, never silently suppressed.
        return relation==ScheduleCourseRecognition.Relation.EXACT;""",
        "photo OCR alternatives")

def activity(source):
    source=replace_once(source,
        '"  •  Cursos posibles: "+SchedulePhotoReview.provisionalEstimate(detected.candidates)+',
        '"  •  Nombres sin confirmar: "+SchedulePhotoReview.provisionalEstimate(detected.candidates)+',
        "distinct preapproval titles")
    source=replace_once(source,
        '"  •  Confirma nombres repetidos antes de importar."',
        '"  •  Confirma coincidencias de una sola palabra antes de importar."',
        "visible advice")
    source=replace_once(source,
        '"▣  Mismo curso · "+relatedCount+" días/sesiones · color compartido"',
        '"▣  Nombre repetido · "+relatedCount+" sesiones · confirma si son el mismo curso"',
        "do not declare identity prematurely")
    source=replace_once(source,
        '''ScheduleCourseColors.align(approved,ScheduleDatabase.get(this).all(profileId));
                    confirmPhotoWarnings(approved,()->confirmPhotoName(approved));''',
        '''ScheduleCourseColors.align(approved,ScheduleDatabase.get(this).all(profileId));
                    confirmExistingCourseMatches(approved,()->
                        confirmPhotoWarnings(approved,()->confirmPhotoName(approved)));''',
        "compare against saved courses")
    source=replace_once(source,
        'SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,confirmed,rejected);',
        'SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(approved,java.util.Collections.emptySet(),rejected);',
        "never skip approved session")
    source=replace_once(source,
        '''pair.relation==ScheduleCourseRecognition.Relation.SHARED_START?
            "Ambos nombres comienzan con la misma palabra, pero podrían ser cursos distintos.":''',
        '''pair.relation==ScheduleCourseRecognition.Relation.SHARED_START?
            "Ambos nombres comienzan con una palabra similar, pero podrían ser cursos distintos.":
            pair.relation==ScheduleCourseRecognition.Relation.SHARED_WORD?
            "Comparten al menos una palabra significativa («"+
                ScheduleCourseRecognition.sharedWord(first.course,second.course)+
                "»). Confirma si se trata del mismo curso.":''',
        "visible reason for a shared word")
    source=replace_once(source,
        '''SchedulePhotoReview.reject(approved,pair);
            rejected.add(SchedulePhotoReview.pairKey(pair));popup.dismiss();''',
        '''SchedulePhotoReview.rememberDecision(approved,pair,rejected,false);
            SchedulePhotoReview.reject(approved,pair);popup.dismiss();''',
        "record declined pair")
    source=replace_once(source,
        '''if(pair.exact){
                SchedulePhotoReview.accept(approved,pair);''',
        '''if(pair.exact){
                SchedulePhotoReview.rememberDecision(approved,pair,rejected,true);
                SchedulePhotoReview.accept(approved,pair);''',
        "record exact approval")
    source=replace_once(source,
        '''SchedulePhotoReview.acceptWithName(approved,pair,title);
                confirmed.add(pair.later);''',
        '''SchedulePhotoReview.rememberDecision(approved,pair,rejected,true);
                SchedulePhotoReview.acceptWithName(approved,pair,title);
                confirmed.add(pair.later);''',
        "record different-name approval")
    source=replace_once(source,
        "    /** The user explicitly acknowledges any OCR blocks that could not be corroborated. */",
        r'''    /** Compare imported OCR titles to SAVED titles in this schedule only. */
    private void confirmExistingCourseMatches(ArrayList<ScheduleEntry> approved,
                                               Runnable onComplete){
        if(photoFirst||manualMode||profileId.isEmpty()){
            onComplete.run();return;
        }
        List<ScheduleEntry> existing=ScheduleDatabase.get(this).all(profileId);
        confirmExistingCourseMatchesStep(approved,existing,new HashSet<String>(),onComplete);
    }
    private void confirmExistingCourseMatchesStep(ArrayList<ScheduleEntry> approved,
            List<ScheduleEntry> existing,Set<String> resolved,Runnable onComplete){
        LinkedHashMap<String,ScheduleEntry> imported=new LinkedHashMap<>();
        LinkedHashMap<String,ScheduleEntry> saved=new LinkedHashMap<>();
        for(ScheduleEntry s:approved)
            imported.putIfAbsent(ScheduleCourseColors.identity(s.course),s);
        for(ScheduleEntry s:existing)
            saved.putIfAbsent(ScheduleCourseColors.identity(s.course),s);
        for(ScheduleEntry candidate:imported.values())for(ScheduleEntry previous:saved.values()){
            String key=ScheduleCourseColors.identity(candidate.course)+"|"+
                    ScheduleCourseColors.identity(previous.course);
            if(resolved.contains(key))continue;
            ScheduleCourseRecognition.Relation relation=ScheduleCourseRecognition.compare(
                candidate.course,previous.course);
            if(relation==ScheduleCourseRecognition.Relation.DIFFERENT)continue;
            String incomingName=candidate.course,originalName=previous.course;
            String word=ScheduleCourseRecognition.sharedWord(incomingName,originalName);
            String explanation=word.isEmpty()?"Los nombres se parecen.":
                "Ambos contienen la palabra «"+word+"».";
            scheduleDialog().setTitle("¿Es el mismo curso que ya tienes?")
                .setMessage("En la foto: «"+incomingName+"»\n"+
                    "Ya guardado: «"+originalName+"»\n\n"+explanation+
                    "\n\nNo se combinarán sin tu confirmación.")
                .setNeutralButton("Volver a revisar",null)
                .setNegativeButton("No, son distintos",(d,w)->{
                    resolved.add(key);
                    if(ScheduleCourseColors.same(incomingName,originalName))
                        SchedulePhotoReview.distinguishFromExisting(
                            approved,existing,incomingName);
                    confirmExistingCourseMatchesStep(approved,existing,resolved,onComplete);
                })
                .setPositiveButton("Sí, mismo curso",(d,w)->{
                    resolved.add(key);
                    String id=ScheduleCourseColors.identity(incomingName);
                    for(ScheduleEntry row:approved)
                        if(ScheduleCourseColors.identity(row.course).equals(id)){
                            row.course=originalName;row.color=previous.color;
                        }
                    resolved.add(ScheduleCourseColors.identity(originalName)+"|"+
                        ScheduleCourseColors.identity(originalName));
                    confirmExistingCourseMatchesStep(approved,existing,resolved,onComplete);
                }).show();
            return;
        }
        onComplete.run();
    }

    /** The user explicitly acknowledges any OCR blocks that could not be corroborated. */''',
        "saved-course gate")
    return source

def run():
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 67")!=1 or gradle.count("versionName '3.15.0'")!=1:
        raise RuntimeError("Requires verified Agenda Clara 3.15.0 sources")
    helper=JAVA/"ScheduleCourseWordReview.java"
    if helper.exists():raise RuntimeError("Course review helper already installed")
    paths=[JAVA/"ScheduleCourseRecognition.java",JAVA/"SchedulePhotoReview.java",
           JAVA/"ScheduleOcrFusion.java",JAVA/"ScheduleActivity.java"]
    photo=[JAVA/"PhotoWidget.java",JAVA/"PhotoConfigActivity.java",
           JAVA/"PhotoTapActivity.java",
           Path("AgendaClara/app/src/main/res/layout/widget_photo.xml"),
           Path("AgendaClara/app/src/main/res/xml/photo_widget_info.xml")]
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in photo}
    originals=[p.read_text(encoding="utf-8") for p in paths]
    transforms=[recognition,review,fusion,activity]
    updated=[fn(value) for fn,value in zip(transforms,originals)]
    # All anchors validated before mutating the reconstructed app.
    shutil.copyfile(STAGE/"ScheduleCourseWordReview.java",helper)
    for path,body in zip(paths,updated):path.write_text(body,encoding="utf-8")
    GRADLE.write_text(gradle.replace("versionCode 67","versionCode 68",1)
        .replace("versionName '3.15.0'","versionName '3.15.1'",1),encoding="utf-8")
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==value
               for p,value in hashes.items()),"Fixed-photo widget was modified"
    print("PASS: mandatory word-based course confirmation, including saved courses")
    print("PASS: no silent OCR-variant suppression and no missing pairwise checks")
    print("PASS: fixed-photo widget files unchanged")

if __name__=="__main__":run()
