package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Suggests a *confirmed* canonical course name when one OCR name appears alone.
 * A new variant is only a suggestion; applying it always requires a tap.
 * All evidence comes from user-accepted local ScheduleAdaptiveRules.Rule entries.
 */
public final class ScheduleAdaptiveVariants {
    private ScheduleAdaptiveVariants() {}

    public static final class Suggestion {
        public final String observed;
        public final String canonical;
        public final String learnedFrom;
        public final int similarity; // deterministic lexical estimate, NOT a probability
        public final int confirmations;
        Suggestion(String observed, String canonical, String learnedFrom,
                   int similarity, int confirmations) {
            this.observed=observed;
            this.canonical=canonical;
            this.learnedFrom=learnedFrom;
            this.similarity=similarity;
            this.confirmations=confirmations;
        }
    }

    private static final Pattern GROUP = Pattern.compile(
        "(?iu)\\bgrupo\\s*(?:n[oº°.]?\\s*)?([0-9]{1,3}|[a-z])\\b");
    private static final Pattern COURSE_CODE = Pattern.compile(
        "(?iu)\\(([a-z0-9]{1,3})\\)");

    private static String group(String name) {
        Matcher m=GROUP.matcher(ScheduleAdaptiveRules.normalize(name));
        return m.find()?m.group(1):"";
    }
    private static String code(String name) {
        Matcher m=COURSE_CODE.matcher(name);
        return m.find()?m.group(1).toLowerCase(Locale.ROOT):"";
    }
    private static boolean compatible(String observed,String alias,String canonical) {
        String o=ScheduleCourseSemanticGuard.level(observed),
            a=ScheduleCourseSemanticGuard.level(alias),
            c=ScheduleCourseSemanticGuard.level(canonical);
        if(!o.equals(a)||!a.equals(c))return false;
        String go=group(observed),ga=group(alias),gc=group(canonical);
        if(!go.equals(ga)||!ga.equals(gc))return false;
        String co=code(observed),ca=code(alias),cc=code(canonical);
        if(!co.isEmpty()&&!ca.isEmpty()&&!co.equals(ca))return false;
        if(!co.isEmpty()&&!cc.isEmpty()&&!co.equals(cc))return false;
        if(!ca.isEmpty()&&!cc.isEmpty()&&!ca.equals(cc))return false;
        return true;
    }

    private static int editDistance(String a,String b) {
        int[] prev=new int[b.length()+1],cur=new int[b.length()+1];
        for(int j=0;j<=b.length();j++)prev[j]=j;
        for(int i=1;i<=a.length();i++) {
            cur[0]=i;
            for(int j=1;j<=b.length();j++)
                cur[j]=Math.min(Math.min(cur[j-1]+1,prev[j]+1),
                    prev[j-1]+(a.charAt(i-1)==b.charAt(j-1)?0:1));
            int[] swap=prev;prev=cur;cur=swap;
        }
        return prev[b.length()];
    }

    private static int similarity(String observed,String alias) {
        String a=ScheduleAdaptiveRules.normalize(
            ScheduleCourseSemanticGuard.cleanOcrName(observed));
        String b=ScheduleAdaptiveRules.normalize(
            ScheduleCourseSemanticGuard.cleanOcrName(alias));
        if(a.isEmpty()||b.isEmpty())return 0;
        if(a.equals(b))return 100; // normalized alias already explicitly learned
        String[] wordsA=a.split(" "),wordsB=b.split(" ");
        // New fuzzy aliases need at least two substantive words and a matching
        // informative head; avoid guessing from one shared word like "educativa".
        if(wordsA.length<2||wordsB.length<2)return 0;
        if(wordsA.length!=wordsB.length)return 0;
        if(wordsA[0].length()<5||wordsB[0].length()<5)return 0;
        if(ScheduleCourseSemanticGuard.informative(observed).isEmpty()||
           ScheduleCourseSemanticGuard.informative(alias).isEmpty())return 0;
        if(editDistance(wordsA[0],wordsB[0])>1)return 0;
        int longest=Math.max(a.length(),b.length());
        if(Math.abs(a.length()-b.length())>Math.max(2,longest/8))return 0;
        int errors=editDistance(a,b);
        if(errors==0)return 100;
        int allowed=Math.max(1,Math.min(3,(int)Math.floor(longest*.12)));
        if(errors>allowed)return 0;
        int estimate=100-(errors*100/longest);
        return estimate>=87?estimate:0;
    }

    private static boolean veto(List<ScheduleAdaptiveRules.Rule> rules,
                                String observed,String canonical,String alias) {
        for(ScheduleAdaptiveRules.Rule r:rules) {
            if(r.together)continue;
            if(ScheduleAdaptiveRules.pairKey(r.left,r.right)
                    .equals(ScheduleAdaptiveRules.pairKey(observed,canonical))
                ||ScheduleAdaptiveRules.pairKey(r.left,r.right)
                    .equals(ScheduleAdaptiveRules.pairKey(observed,alias)))
                return true;
        }
        return false;
    }

    /** At most one unambiguous suggestion for this solitary OCR course name. */
    public static Suggestion suggest(List<ScheduleAdaptiveRules.Rule> history,
                                     String observed) {
        if(history==null||history.isEmpty()||observed==null||
            observed.trim().length()<3||observed.length()>120)return null;
        Map<String,Suggestion> ranked=new LinkedHashMap<>();
        for(ScheduleAdaptiveRules.Rule rule:history) {
            if(rule==null||!rule.together||rule.canonical==null||
                rule.canonical.length()<3||rule.canonical.length()>120)continue;
            String canonical=rule.canonical;
            if(ScheduleAdaptiveRules.normalize(observed)
                    .equals(ScheduleAdaptiveRules.normalize(canonical)))continue;
            for(String alias:new String[]{rule.left,rule.right,rule.canonical}) {
                if(!compatible(observed,alias,canonical))continue;
                if(veto(history,observed,canonical,alias))continue;
                int score=similarity(observed,alias);
                if(score<87)continue;
                String key=ScheduleAdaptiveRules.normalize(canonical);
                Suggestion previous=ranked.get(key);
                if(previous==null||previous.similarity<score||
                    (previous.similarity==score&&
                     previous.confirmations<rule.confirmations))
                    ranked.put(key,new Suggestion(observed,canonical,alias,
                        score,rule.confirmations));
            }
        }
        Suggestion best=null,runnerUp=null;
        for(Suggestion candidate:ranked.values()) {
            if(best==null||candidate.similarity>best.similarity) {
                runnerUp=best;best=candidate;
            }else if(runnerUp==null||candidate.similarity>runnerUp.similarity)
                runnerUp=candidate;
        }
        // Competing confirmed course names: do not recommend either.
        if(best==null||(runnerUp!=null&&
            best.similarity-runnerUp.similarity<8))return null;
        return best;
    }
}
