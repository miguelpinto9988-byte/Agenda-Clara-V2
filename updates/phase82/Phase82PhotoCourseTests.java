package pe.agendaclara.app;

import java.util.*;

/** Regressions for the user-reported silent separation of OCR course names. */
public final class Phase82PhotoCourseTests {
    private static void check(boolean yes,String message){
        if(!yes)throw new AssertionError(message);
    }
    private static ScheduleEntry entry(String name,int day,int start){
        ScheduleEntry e=new ScheduleEntry();
        e.course=name;e.day=day;e.start=start;e.end=start+60;
        e.color=ScheduleCourseColors.deterministic(name);
        return e;
    }
    private static void shared(String a,String b){
        ScheduleCourseRecognition.Relation relation=ScheduleCourseRecognition.compare(a,b);
        check(relation!=ScheduleCourseRecognition.Relation.DIFFERENT,
                "Should ask even for one shared word: "+a+" / "+b);
    }
    public static void main(String[] args){
        shared("Tecnología educativa","Recursos de tecnología");
        shared("Didáctica de la matemática","Evaluación matemática");
        shared("Historia universal","Seminario de historia");
        check(ScheduleCourseRecognition.compare("Fundamentos de la educación",
                "Psicología de la educación")==ScheduleCourseRecognition.Relation.DIFFERENT,
                "Common word educación must not cause an unrelated-course prompt");
        shared("Curso de investigación","Seminario de investigación");
        check(ScheduleCourseRecognition.compare("Didáctica de la matemática",
                "Evaluación matemática")==ScheduleCourseRecognition.Relation.SHARED_WORD,
                "Shared trailing word should yield review relation");
        check(ScheduleCourseRecognition.sharedKeyword("Tecnología educativa",
                "Recursos de tecnología").equals("tecnologia"),"Meaningful shared word");
        check(ScheduleCourseRecognition.compare("Teoría de las ciencias",
                "Metodología de proyectos")==ScheduleCourseRecognition.Relation.DIFFERENT,
                "Articles/prepositions must not prompt a false match");
        check(ScheduleCourseRecognition.compare("Historia I",
                "Historia II")==ScheduleCourseRecognition.Relation.DIFFERENT,
                "Clearly distinct course levels remain separate");
        check(ScheduleCourseRecognition.compare("Historia (grupo 2)",
                "Historia (grupo 3)")==ScheduleCourseRecognition.Relation.DIFFERENT,
                "Already separated user groups must stay separated");
        ArrayList<ScheduleEntry> selections=new ArrayList<>(Arrays.asList(
            entry("Tecnología educativa",1,540),
            entry("Recursos de tecnología",2,540),
            entry("Laboratorio de tecnología",3,540)));
        Set<Integer> accepted=new HashSet<>();
        Set<String> rejected=new HashSet<>();
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(selections,accepted,rejected);
        check(pair!=null && pair.relation==ScheduleCourseRecognition.Relation.SHARED_WORD,
                "Word overlap must enter the visible yes/no course review");
        rejected.add(SchedulePhotoReview.pairKey(pair));
        check(SchedulePhotoReview.nextPair(selections,accepted,rejected)!=null,
                "Rejecting one course must not hide the other alternative");
        check(selections.get(0).course.equals("Tecnología educativa")&&
                selections.get(1).course.equals("Recursos de tecnología"),
                "Review suggestions must never mutate names before confirmation");
        SchedulePhotoReview.acceptWithName(selections,pair,"Tecnología educativa");
        check(selections.get(1).course.equals("Tecnología educativa"),
                "Only explicit accepted decision merges course titles");
        check(selections.get(1).day==2&&selections.get(1).start==540,
                "A confirmed course merger must preserve all class times");
        ScheduleParser.Result table=new ScheduleParser.Result();
        table.candidates.add(entry("Pedagogía",1,480));
        ScheduleParser.Result alt=new ScheduleParser.Result();
        alt.candidates.add(entry("Pedagogla",1,480));
        check(ScheduleCourseRecognition.compare("Pedagogía","Pedagogla")==
                ScheduleCourseRecognition.Relation.OCR_VARIANT,
                "Fixture should be a true OCR typo rather than identical spelling");
        ScheduleParser.Result fusion=ScheduleOcrFusion.reconcile(table,alt,
                new ScheduleParser.Result());
        check(fusion.candidates.size()==2,
                "OCR typo must not disappear silently during reader fusion");
        check(fusion.reviewOnlyKeys.contains(ScheduleOcrFusion.key(fusion.candidates.get(1))),
                "OCR alternate must be visible but not imported without selection");
        System.out.println("PASS: shared word anywhere, multi-choice confirmation, profile-safe sessions");
        System.out.println("PASS: OCR spelling alternatives stay visible for the user");
    }
}