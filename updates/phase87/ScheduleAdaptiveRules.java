package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Device-local learning: only explicitly confirmed course-pair decisions are evidence. */
public final class ScheduleAdaptiveRules {
    private ScheduleAdaptiveRules() {}
    public static final int MAX_RULES=80;
    public static final class Rule {
        public final String left,right,canonical;
        public final boolean together;
        public final int confirmations;
        public final long updatedAt;
        public Rule(String left,String right,boolean together,String canonical,
                    int confirmations,long updatedAt){
            this.left=left;this.right=right;this.together=together;
            this.canonical=canonical;this.confirmations=confirmations;this.updatedAt=updatedAt;
        }
    }
    public static String normalize(String raw) {
        if(raw==null)return "";
        return Normalizer.normalize(raw.trim().toLowerCase(Locale.ROOT),Normalizer.Form.NFD)
                .replaceAll("\\p{M}+","").replaceAll("[^\\p{L}\\p{N}]+"," ")
                .trim().replaceAll("\\s+"," ");
    }
    public static String pairKey(String left,String right){
        String a=normalize(left),b=normalize(right);
        if(a.isEmpty()||b.isEmpty())return "";
        return a.compareTo(b)<=0?a.length()+":"+a+"|"+b.length()+":"+b:
                                  b.length()+":"+b+"|"+a.length()+":"+a;
    }
    public static Rule find(List<Rule> history,String a,String b){
        String key=pairKey(a,b);
        if(key.isEmpty()||history==null)return null;
        for(Rule r:history)if(pairKey(r.left,r.right).equals(key))return r;
        return null;
    }
    /** The most recent explicit decision wins; a previous mistake can be corrected. */
    public static List<Rule> record(List<Rule> old,String a,String b,boolean together,
                                    String canonical,long now){
        if(a==null||b==null||a.trim().length()<2||b.trim().length()<2||
           a.length()>120||b.length()>120||
           (together&&(canonical==null||canonical.trim().length()<2||
                         canonical.trim().length()>120)))
            throw new IllegalArgumentException("Nombres de cursos fuera de rango");
        String key=pairKey(a,b);
        ArrayList<Rule> out=new ArrayList<>();
        int count=1;
        if(old!=null)for(Rule r:old){
            if(pairKey(r.left,r.right).equals(key))count=Math.min(100000,r.confirmations+1);
            else out.add(r);
        }
        out.add(0,new Rule(a.trim(),b.trim(),together,
            together?canonical.trim():"",count,now));
        if(out.size()>MAX_RULES)out.subList(MAX_RULES,out.size()).clear();
        return out;
    }
    /** Fail closed on dissimilar names, explicit groups or inconsistent module levels.
     * This is stricter than the normal review dialog: users may still decide manually. */
    public static boolean canReuse(Rule rule,String a,String b){
        if(rule==null||!pairKey(rule.left,rule.right).equals(pairKey(a,b)))return false;
        if(ScheduleCourseRecognition.compare(a,b)==ScheduleCourseRecognition.Relation.DIFFERENT)
            return false;
        if(!ScheduleCourseSemanticGuard.level(a).equals(ScheduleCourseSemanticGuard.level(b)))
            return false;
        if(a.toLowerCase(Locale.ROOT).matches(".*\\(grupo\\s*[0-9]+\\).*")||
           b.toLowerCase(Locale.ROOT).matches(".*\\(grupo\\s*[0-9]+\\).*"))
            return false;
        return !rule.together||(rule.canonical!=null&&rule.canonical.length()>=2);
    }
}