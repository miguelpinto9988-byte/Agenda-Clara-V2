package pe.agendaclara.app;
import java.util.*;

/** JVM regression tests for user-reported OCR course corroboration regression. */
public final class Phase76RecognitionTests {
    private static void ok(boolean condition,String description){
        if(!condition)throw new AssertionError(description);
    }
    private static ScheduleEntry session(String course,int day,int start){
        ScheduleEntry s=new ScheduleEntry();
        s.course=course;s.day=day;s.start=start;s.end=start+60;
        s.color=ScheduleCourseColors.deterministic(course);
        return s;
    }
    private static void relation(String a,String b,ScheduleCourseRecognition.Relation expected){
        ScheduleCourseRecognition.Relation got=ScheduleCourseRecognition.compare(a,b);
        ok(got==expected,a+" vs "+b+": expected "+expected+", got "+got);
    }
    public static void main(String[] args){
        relation("Investigación","Investigación educativa",ScheduleCourseRecognition.Relation.SHARED_START);
        relation("Historia","Historia de la educación",ScheduleCourseRecognition.Relation.SHARED_START);
        relation("Arte","Arte y creatividad",ScheduleCourseRecognition.Relation.SHARED_START);
        relation("Tendencias","Tendencias educativas",ScheduleCourseRecognition.Relation.TRUNCATED);
        relation("Tendencias educativas","Tendencias tecnológicas",ScheduleCourseRecognition.Relation.SHARED_START);
        relation("Pedagogía aplicada","Pedagogía social",ScheduleCourseRecognition.Relation.SHARED_START);
        relation("Tendencias educativas","Tendencias educativas",ScheduleCourseRecognition.Relation.EXACT);
        relation("Historia I","Historia II",ScheduleCourseRecognition.Relation.DIFFERENT);
        relation("Matemática (grupo 2)","Matemática",ScheduleCourseRecognition.Relation.DIFFERENT);
        relation("Matemática avanzada","Tendencias educativas",ScheduleCourseRecognition.Relation.DIFFERENT);
        ArrayList<ScheduleEntry> courses=new ArrayList<>();
        courses.add(session("Investigación educativa",1,480));
        courses.add(session("Investigación histórica",2,540));
        courses.add(session("Investigación",3,600));
        Set<Integer> accepted=new HashSet<>();
        Set<String> rejected=new HashSet<>();
        SchedulePhotoReview.Pair first=SchedulePhotoReview.nextPair(courses,accepted,rejected);
        ok(first!=null&&first.earlier==0&&first.later==1,"First shared-prefix alternative");
        rejected.add(SchedulePhotoReview.pairKey(first));
        SchedulePhotoReview.Pair next=SchedulePhotoReview.nextPair(courses,accepted,rejected);
        ok(next!=null&&next.earlier==0&&next.later==2,"Second OCR label must still be checked");
        rejected.add(SchedulePhotoReview.pairKey(next));
        next=SchedulePhotoReview.nextPair(courses,accepted,rejected);
        ok(next!=null&&next.earlier==1&&next.later==2,
                "Declining a name must still offer another matching name");
        rejected.add(SchedulePhotoReview.pairKey(next));
        ok(SchedulePhotoReview.nextPair(courses,accepted,rejected)==null,
                "No endless loop after all pairs have been decided");
        ArrayList<ScheduleEntry> repeats=new ArrayList<>();
        repeats.add(session("Tendencias",1,480));
        repeats.add(session("Tendencias educativas",2,540));
        repeats.add(session("Tendencias",3,600));
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(repeats,new HashSet<>(),new HashSet<>());
        ok(pair!=null,"Repeated word needs dialog");
        SchedulePhotoReview.accept(repeats,pair);
        ok(repeats.get(0).day==1&&repeats.get(1).day==2,
                "Accepting name must NOT change day or time");
        ArrayList<ScheduleEntry> same=new ArrayList<>();
        same.add(session("Historia",1,480));
        same.add(session("Historia",1,480));
        same.add(session("Historia",2,480));
        ok(SchedulePhotoReview.uniqueBlocks(same).size()==2,
                "Only duplicate OCR rectangles, never weekly sessions, are removed");
        System.out.println("PASS: common first words, partial names and ambiguous different subjects");
        System.out.println("PASS: all alternatives reviewed even after a decline");
        System.out.println("PASS: levels, course groups, session days and times remain independent");
    }
}
