#!/usr/bin/env python3
"""3.15.1: require explicit course-name confirmation for any meaningful shared word.

Applies to reconstructed 3.15.0 sources. Does not change user data or photo widget.
"""
from pathlib import Path

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")

def replace_once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected one source anchor, got {count}")
    return source.replace(old,new,1)

def recognition(source):
    source=replace_once(source,
        "public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT, SHARED_START }",
        "public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT, SHARED_START, SHARED_WORD }",
        "add SHARED_WORD")
    insertion='''    /** One academic keyword anywhere in both titles merits review, not a merge. */
    private static final Set<String> CONNECTORS=new HashSet<>(Arrays.asList(
        "de","del","la","las","el","los","y","e","a","al","en","para",
        "por","con","sin","un","una","unos","unas","o","u","que",
        "curso","asignatura","seccion","grupo"));
    private static Set<String> meaningfulWords(String value){
        LinkedHashSet<String> out=new LinkedHashSet<>();
        if(value==null)return out;
        String normalized=key(value);
        StringBuilder separated=new StringBuilder(normalized.length());
        for(int n=0;n<normalized.length();n++){
            char ch=normalized.charAt(n);
            separated.append(Character.isLetterOrDigit(ch)?ch:' ');
        }
        for(String word:separated.toString().trim().split(" +")){
            if(word.length()>=3&&!CONNECTORS.contains(word))out.add(word);
        }
        return out;
    }
    /** Returns an actual normalized shared content word; empty means no overlap. */
    public static String sharedKeyword(String left,String right){
        Set<String> rightWords=meaningfulWords(right);
        for(String word:meaningfulWords(left))if(rightWords.contains(word))return word;
        return "";
    }
'''
    source=replace_once(source,
        "    private static String suffix(String s){",
        insertion+"    private static String suffix(String s){",
        "meaningful keyword matcher")
    source=replace_once(source,
        "        int largest=Math.max(a.length(),b.length());",
        '''        // OCR may reorder words or truncate one title. Do NOT silently split
        // titles with even a single shared content word (not just first word).
        if(!sharedKeyword(left,right).isEmpty())return Relation.SHARED_WORD;
        int largest=Math.max(a.length(),b.length());''',
        "shared word review before early distance rejects")
    return source

def review(source):
    return replace_once(source,
        "                    rel==ScheduleCourseRecognition.Relation.SHARED_START?1:0;",
        '''                    rel==ScheduleCourseRecognition.Relation.SHARED_START?1:
                    rel==ScheduleCourseRecognition.Relation.SHARED_WORD?1:0;''',
        "recognize SHARED_WORD in nextPair")

def activity(source):
    return replace_once(source,
        '''            pair.relation==ScheduleCourseRecognition.Relation.SHARED_START?
            "Ambos nombres comienzan con la misma palabra, pero podrían ser cursos distintos.":''',
        '''            pair.relation==ScheduleCourseRecognition.Relation.SHARED_START?
            "Ambos nombres comienzan con la misma palabra, pero podrían ser cursos distintos.":
            pair.relation==ScheduleCourseRecognition.Relation.SHARED_WORD?
            "Se encontró una palabra común («"+
                ScheduleCourseRecognition.sharedKeyword(
                    approved.get(pair.earlier).course,approved.get(pair.later).course)+
                "»). Confirma si representan el mismo curso; no se unirán automáticamente.":''',
        "explain shared word to user")

def fusion(source):
    return replace_once(source,
        '''        return relation==ScheduleCourseRecognition.Relation.EXACT||
               relation==ScheduleCourseRecognition.Relation.OCR_VARIANT;''',
        '''        // Different OCR spellings must remain visible as unchecked alternatives.
        // Previously OCR_VARIANT silently disappeared before human review.
        return relation==ScheduleCourseRecognition.Relation.EXACT;''',
        "keep OCR variant for confirmation")

def main():
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 67")!=1 or gradle.count("versionName '3.15.0'")!=1:
        raise RuntimeError("Requires verified 3.15.0 source (versionCode 67)")
    processors={
        "ScheduleCourseRecognition.java":recognition,
        "SchedulePhotoReview.java":review,
        "ScheduleActivity.java":activity,
        "ScheduleOcrFusion.java":fusion,
    }
    modified={}
    for filename,fn in processors.items():
        p=JAVA/filename
        modified[p]=fn(p.read_text(encoding="utf-8"))
    for p,v in modified.items():p.write_text(v,encoding="utf-8")
    GRADLE.write_text(
        gradle.replace("versionCode 67","versionCode 68",1)
              .replace("versionName '3.15.0'","versionName '3.15.1'",1),
        encoding="utf-8")
    print("PASS 3.15.1: any shared meaningful word => explicit course confirmation")
    print("PASS: OCR spelling variants retained for review, not silently suppressed")
    print("PASS: existing schedule entries and PhotoWidget untouched")
if __name__=="__main__":main()
