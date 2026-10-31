package pe.agendaclara.app;

import java.util.*;
import java.util.regex.*;

/** Conservative OCR review: a course can have many sessions without becoming many courses. */
public final class SchedulePhotoReview {
    private SchedulePhotoReview(){}
    public static final class Overview {
        public final int textLines,weekdayHeaders,timeLabels;
        Overview(int a,int b,int c){textLines=a;weekdayHeaders=b;timeLabels=c;}
    }
    public static final class Pair {
        public final int earlier,later;
        public final boolean exact;
        public final ScheduleCourseRecognition.Relation relation;
        Pair(int a,int b,ScheduleCourseRecognition.Relation r){earlier=a;later=b;relation=r;exact=r==ScheduleCourseRecognition.Relation.EXACT;}
    }
    public static Overview overview(List<ScheduleGridInterpreter.Line> lines){
        if(lines==null)return new Overview(0,0,0);
        Set<String> days=new HashSet<>();int times=0,readable=0;
        for(ScheduleGridInterpreter.Line line:lines){
            String value=line.text.trim();if(value.isEmpty())continue;
            readable++;
            Matcher m=Pattern.compile("(?i)^(lunes|martes|miercoles|jueves|viernes|sabado|domingo|lun|mar|mie|jue|vie|sab|dom)\\b")
                    .matcher(ScheduleParser.fold(value));
            if(m.find())days.add(m.group(1).substring(0,3));
            if(Pattern.compile("(?i)\\b\\d{1,2}[:h.]\\d{2}\\b").matcher(value).find())times++;
        }
        return new Overview(readable,days.size(),times);
    }
    /** Identical OCR rectangles for one session should not become separate classes. */
    public static List<ScheduleEntry> uniqueBlocks(List<ScheduleEntry> raw){
        ArrayList<ScheduleEntry> out=new ArrayList<>();
        if(raw==null)return out;
        for(ScheduleEntry s:raw){
            boolean exists=false;
            for(ScheduleEntry prev:out)if(prev.day==s.day&&prev.start==s.start&&prev.end==s.end
                    &&ScheduleCourseColors.same(prev.course,s.course)){exists=true;break;}
            if(!exists)out.add(s);
        }
        return out;
    }
    /** Exact distinct subject count. Review suggestions might lower this after confirmation. */
    public static int courseEstimate(Collection<ScheduleEntry> list){
        Set<String> keys=new HashSet<>();
        if(list!=null)for(ScheduleEntry s:list)if(s!=null)keys.add(ScheduleCourseColors.identity(s.course));
        keys.remove("");return keys.size();
    }
    public static int provisionalEstimate(Collection<ScheduleEntry> list){
        return ScheduleCourseRecognition.provisionalCount(list);
    }
    /** Select the best earlier matching course for this candidate; never merge without asking. */
    public static Pair nextPair(List<ScheduleEntry> entries,Set<Integer> decided){
        if(entries==null)return null;
        for(int i=1;i<entries.size();i++){
            if(decided!=null&&decided.contains(i))continue;
            Pair best=null;int bestRank=0;
            for(int j=0;j<i;j++){
                ScheduleCourseRecognition.Relation rel=ScheduleCourseRecognition.compare(
                    entries.get(j).course,entries.get(i).course);
                int rank=rel==ScheduleCourseRecognition.Relation.EXACT?3:
                    rel==ScheduleCourseRecognition.Relation.TRUNCATED?2:
                    rel==ScheduleCourseRecognition.Relation.OCR_VARIANT?1:0;
                if(rank>bestRank){bestRank=rank;best=new Pair(j,i,rel);}
            }
            if(best!=null)return best;
        }
        return null;
    }
    /** Combine COURSE identity only. All day/time/room/teacher fields remain unchanged. */
    public static void accept(List<ScheduleEntry> entries,Pair pair){
        ScheduleEntry first=entries.get(pair.earlier),second=entries.get(pair.later);
        String oldName=first.course;
        String best=ScheduleCourseRecognition.preferred(oldName,second.course);
        // A previously confirmed same-name group also receives the complete name.
        for(int i=0;i<entries.size();i++){
            ScheduleEntry e=entries.get(i);
            if(i==pair.later||i==pair.earlier||ScheduleCourseColors.same(e.course,oldName)){
                e.course=best;e.color=first.color;
            }
        }
    }
    /** Never delete an OCR block. A declined exact match gets a distinct group name. */
    public static void reject(List<ScheduleEntry> entries,Pair pair){
        ScheduleEntry later=entries.get(pair.later);
        ScheduleEntry earlier=entries.get(pair.earlier);
        if(!ScheduleCourseColors.same(earlier.course,later.course))return;
        String base=later.course.replaceAll("(?i)\\s*\\(grupo [0-9]+\\)$","").trim();
        int number=2;String proposal;
        while(true){
            String suffix=" (grupo "+number+++")";
            proposal=base.substring(0,Math.min(base.length(),120-suffix.length()))+suffix;
            boolean taken=false;
            for(int i=0;i<entries.size();i++)if(i!=pair.later&&
                ScheduleCourseColors.same(entries.get(i).course,proposal)){taken=true;break;}
            if(!taken)break;
        }
        later.course=proposal;later.color=ScheduleCourseColors.deterministic(proposal);
    }
}
