package pe.agendaclara.app;
import java.util.*;

/** Regressions for the reported split Tendencias and unrelated "educativa" prompts. */
public final class Phase86SemanticPhotoTests {
    private static void ok(boolean condition,String message) {
        if(!condition)throw new AssertionError(message);
    }
    private static ScheduleEntry session(String name,int day,int start) {
        ScheduleEntry s=new ScheduleEntry();s.course=name;
        s.day=day;s.start=start;s.end=start+100;
        s.color=ScheduleCourseColors.deterministic(name);
        return s;
    }
    public static void main(String[] unused) {
        ScheduleCourseRecognition.Relation DIFFERENT=ScheduleCourseRecognition.Relation.DIFFERENT;
        ScheduleCourseRecognition.Relation EXACT=ScheduleCourseRecognition.Relation.EXACT;
        ScheduleCourseRecognition.Relation UNSURE=ScheduleCourseRecognition.Relation.LEVEL_UNCERTAIN;
        ok(ScheduleCourseRecognition.compare("Tutoría educativa","Investigación educativa")
            ==DIFFERENT,"Generic adjective must not prompt unrelated subjects");
        ok(ScheduleCourseRecognition.compare("Fundamentos de la educación",
            "Psicología de la educación")==DIFFERENT,
            "Generic word education must not imply one course");
        ok(ScheduleCourseRecognition.compare("Matemática (grupo 2)",
            "Matemática (grupo 3)")==DIFFERENT,"Explicit distinct groups preserved");
        ok(ScheduleCourseRecognition.compare("Historia I","Historia II")==DIFFERENT,
            "Roman levels I and II are not equivalent");
        ok(ScheduleCourseRecognition.compare("Historia","Historia I")==UNSURE,
            "Missing level requires review, not automatic merge");
        ok(ScheduleCourseRecognition.compare("Historia","Historia")==EXACT,
            "Identical names form one course");
        ok(ScheduleCourseRecognition.compare("Pedagogía","Pedagogla")==
            ScheduleCourseRecognition.Relation.OCR_VARIANT,
            "OCR near spelling must remain a candidate");
        ok(ScheduleCourseRecognition.compare("Tendencias educativas (E)",
            "Tendencias educativas (E) educativa")==EXACT,
            "Duplicated adjective after course code is OCR noise");
        ok(ScheduleCourseSemanticGuard.cleanOcrName(
            "TENDENCIAS EDUCATIVAS (E) EDUCATIVA")
            .equals("TENDENCIAS EDUCATIVAS (E)"),
            "Repeated tail must be removed from OCR proposal");
        ok(ScheduleCourseSemanticGuard.cleanOcrName(
            "TENDENCIAS EDUCATIVAS (E) EDUCATIVA I")
            .equals("TENDENCIAS EDUCATIVAS (E) I"),
            "Uncertain level remains intact");
        ok(ScheduleCourseRecognition.compare("TENDENCIAS EDUCATIVAS (E)",
            "TENDENCIAS EDUCATIVAS (E) EDUCATIVA I")==UNSURE,
            "Possible course level must not be merged automatically");
        ok(ScheduleCourseRecognition.compare("Tendencias educativas",
            "Tendencias tecnológicas")==
            ScheduleCourseRecognition.Relation.SHARED_START,
            "Shared head without complete match is still reviewed");
        ok(ScheduleCourseRecognition.compare("Investigación educativa",
            "Investigación")!=DIFFERENT,
            "Truncated distinctive course must be offered for review");
        ArrayList<ScheduleEntry> input=new ArrayList<>(Arrays.asList(
            session("Tutoría educativa",1,480),
            session("Investigación educativa",2,540),
            session("TENDENCIAS EDUCATIVAS (E)",3,600),
            session("TENDENCIAS EDUCATIVAS (E) EDUCATIVA",4,660)));
        SchedulePhotoReview.Pair first=SchedulePhotoReview.nextPair(
            input,new HashSet<Integer>(),new HashSet<String>());
        ok(first!=null && first.earlier==2 && first.later==3,
            "Only actual Tendencias variants should be paired");
        SchedulePhotoReview.accept(input,first);
        ok(ScheduleCourseColors.groups(input).size()==3,
            "All Tendencias variants should share a single group after confirmation");
        ok(input.get(2).day==3&&input.get(3).day==4,
            "Merging names must preserve each session day");
        ok(input.get(2).start==600&&input.get(3).start==660,
            "Merging names must preserve each time");
        ArrayList<ScheduleEntry> suspicious=new ArrayList<>(Arrays.asList(
            session("TENDENCIAS EDUCATIVAS (E)",1,480),
            session("TENDENCIAS EDUCATIVAS (E) I",2,540)));
        ok(!ScheduleCourseSemanticGuard.audit(suspicious).isEmpty(),
            "Internal audit should flag ambiguous level before saving");
        ArrayList<ScheduleEntry> unrelated=new ArrayList<>(Arrays.asList(
            session("Tutoría educativa",1,480),
            session("Investigación educativa",2,540)));
        ok(ScheduleCourseSemanticGuard.audit(unrelated).isEmpty(),
            "Unrelated course names must not generate noisy audit warnings");
        System.out.println("PASS: unrelated educational subjects no longer compared");
        System.out.println("PASS: duplicated OCR descriptors repaired; ambiguous levels preserved");
        System.out.println("PASS: confirmed merge groups all sessions without altering time or day");
        System.out.println("PASS: internal audit flags uncertain levels without false merges");
    }
}
