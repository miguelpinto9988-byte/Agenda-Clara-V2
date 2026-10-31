package pe.agendaclara.app;

import java.util.*;
import java.util.regex.*;

/** Offline OCR name reconciliation: proposes decisions, never silently merges subjects. */
public final class ScheduleCourseRecognition {
    private ScheduleCourseRecognition() {}
    public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT }
    private static final Pattern LEVEL=Pattern.compile("(?:^| )(?:i|ii|iii|iv|v|vi|vii|viii|ix|x|[0-9]+)$");
    private static final Pattern GROUP=Pattern.compile("(?i)\\s*\\(grupo\\s+\\d+\\)\\s*$");
    private static final Set<String> GENERIC=new HashSet<>(Arrays.asList(
        "historia","literatura","arte","educacion","pedagogia","ciencia",
        "matematica","investigacion","deporte","comunicacion","ingles",
        "programacion","practica","taller","seminario","laboratorio","proyecto",
        "curso","introduccion","fundamentos","desarrollo","metodologia"));
    private static String key(String s){return ScheduleCourseColors.key(s);}
    private static String suffix(String s){
        Matcher m=LEVEL.matcher(key(s));return m.find()?m.group().trim():"";
    }
    private static boolean hasExplicitGroup(String s){return s!=null&&GROUP.matcher(s).find();}
    private static int distance(String a,String b){
        int[] values=new int[b.length()+1];
        for(int i=0;i<=b.length();i++)values[i]=i;
        for(int i=1;i<=a.length();i++){
            int last=values[0];values[0]=i;
            for(int j=1;j<=b.length();j++){
                int prev=values[j];
                values[j]=Math.min(Math.min(values[j]+1,values[j-1]+1),last+(a.charAt(i-1)==b.charAt(j-1)?0:1));
                last=prev;
            }
        }
        return values[b.length()];
    }
    public static Relation compare(String left,String right){
        if(left==null||right==null||left.trim().isEmpty()||right.trim().isEmpty())return Relation.DIFFERENT;
        // Explicitly distinct groups and Roman-numbered levels must never be suggested as the same course.
        if(hasExplicitGroup(left)||hasExplicitGroup(right))return Relation.DIFFERENT;
        if(!suffix(left).equals(suffix(right)))return Relation.DIFFERENT;
        if(ScheduleCourseColors.same(left,right))return Relation.EXACT;
        String a=key(left),b=key(right);
        if(a.isEmpty()||b.isEmpty())return Relation.DIFFERENT;
        String shortName=a.length()<=b.length()?a:b;
        String longName=a.length()>b.length()?a:b;
        String[] sw=shortName.split(" ");
        // Complete-word prefix only; do not infer from a 3-letter OCR fragment or a generic subject name.
        if(shortName.length()>=8&&longName.startsWith(shortName+" ")
                &&longName.split(" ").length>sw.length
                &&!(sw.length==1&&GENERIC.contains(shortName))){
            return Relation.TRUNCATED;
        }
        int largest=Math.max(a.length(),b.length());
        if(largest<9||Math.abs(a.length()-b.length())>Math.max(3,largest*.20))return Relation.DIFFERENT;
        String aa=a.split(" ")[0],bb=b.split(" ")[0];
        if(aa.length()<4||bb.length()<4||distance(aa,bb)>2)return Relation.DIFFERENT;
        int max=(int)Math.floor(largest*.16);
        return distance(a,b)<=Math.max(2,max)?Relation.OCR_VARIANT:Relation.DIFFERENT;
    }
    /** Prefer the fuller spelling when OCR recognizes the same course as a truncated title. */
    public static String preferred(String left,String right){
        if(left==null||left.trim().isEmpty())return right;
        if(right==null||right.trim().isEmpty())return left;
        String a=key(left),b=key(right);
        if(a.length()==b.length())return left;
        return a.length()>b.length()?left:right;
    }
    /** Conservative estimate: each truncated/typo spelling must have one unique counterpart. */
    public static int provisionalCount(Collection<ScheduleEntry> sessions){
        if(sessions==null||sessions.isEmpty())return 0;
        ArrayList<String> distinct=new ArrayList<>();
        for(ScheduleEntry s:sessions){
            if(s==null||s.course==null||key(s.course).isEmpty())continue;
            boolean known=false;
            for(String existing:distinct)if(ScheduleCourseColors.same(existing,s.course)){
                known=true;break;
            }
            if(!known)distinct.add(s.course);
        }
        int n=distinct.size();
        int[] proposed=new int[n];
        Arrays.fill(proposed,-1);
        for(int i=0;i<n;i++){
            int candidate=-1,choices=0;
            for(int j=0;j<n;j++)if(i!=j){
                Relation rel=compare(distinct.get(i),distinct.get(j));
                if(rel==Relation.TRUNCATED||rel==Relation.OCR_VARIANT){candidate=j;choices++;}
            }
            if(choices==1)proposed[i]=candidate;
        }
        int joins=0;
        for(int i=0;i<n;i++)if(proposed[i]>=0){
            int j=proposed[i];
            if(proposed[j]==i&&i<j)joins++;
        }
        return n-joins;
    }
}
