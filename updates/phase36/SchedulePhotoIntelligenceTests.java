package pe.agendaclara.app;
import java.util.*;
/** Synthetic OCR detections only; no personal timetable is used. */
public final class SchedulePhotoIntelligenceTests {
    private static void yes(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    private static ScheduleEntry session(String course,int day,int start){
        ScheduleEntry s=new ScheduleEntry();s.course=course;s.day=day;s.start=start;s.end=start+60;
        s.color=ScheduleCourseColors.deterministic(course);return s;
    }
    public static void main(String[] ignored){
        // Geometry-driven OCR fallback: identical subject across weekday columns.
        List<ScheduleGridInterpreter.Line> photoLines=Arrays.asList(
            new ScheduleGridInterpreter.Line("Lunes",250,60,330,86),
            new ScheduleGridInterpreter.Line("Miércoles",470,60,590,86),
            new ScheduleGridInterpreter.Line("08:00-09:00",8,180,110,208),
            new ScheduleGridInterpreter.Line("09:00-10:00",8,290,110,318),
            new ScheduleGridInterpreter.Line("10:00-11:00",8,400,110,428),
            new ScheduleGridInterpreter.Line("Tendencias",242,180,347,214),
            new ScheduleGridInterpreter.Line("Tendencias Educativas",463,290,632,325));
        ScheduleParser.Result parsed=ScheduleVirtualGrid.parse(photoLines,800,550);
        yes(parsed.candidates.size()==2,"geometry reads two sessions in different columns");
        yes(SchedulePhotoReview.provisionalEstimate(parsed.candidates)==1,
            "geometry OCR proposes same course despite a truncated title");
        List<ScheduleEntry> duplicated=Arrays.asList(session("Tendencias Educativas",1,480),session("Tendencias Educativas",3,540));
        yes(SchedulePhotoReview.courseEstimate(duplicated)==1,"same course, two weekly sessions");
        List<ScheduleEntry> partial=new ArrayList<>(Arrays.asList(session("Tendencias",1,480),session("Tendencias Educativas",4,540)));
        yes(SchedulePhotoReview.courseEstimate(partial)==2,"provisional names initially different");
        yes(SchedulePhotoReview.provisionalEstimate(partial)==1,"partial OCR estimate shows one possible course");
        SchedulePhotoReview.Pair p=SchedulePhotoReview.nextPair(partial,new HashSet<Integer>());
        yes(p!=null&&!p.exact&&p.relation==ScheduleCourseRecognition.Relation.TRUNCATED,"partial confirmation");
        SchedulePhotoReview.accept(partial,p);
        yes(partial.get(0).course.equals("Tendencias Educativas"),"preserve fuller name");
        yes(SchedulePhotoReview.courseEstimate(partial)==1,"confirmed merge keeps one course");
        yes(partial.get(0).day==1&&partial.get(1).day==4&&partial.get(1).start==540,"preserve sessions");
        List<ScheduleEntry> declined=new ArrayList<>(Arrays.asList(session("Tendencias",1,480),session("Tendencias Educativas",4,540)));
        SchedulePhotoReview.reject(declined,SchedulePhotoReview.nextPair(declined,new HashSet<Integer>()));
        yes(declined.get(1).course.equals("Tendencias Educativas"),"declining partial match doesn't rename real subject");
        List<ScheduleEntry> uncertainNames=Arrays.asList(
            session("Tendencias",1,480),session("Tendencias Educativas",2,480),
            session("Tendencias Sociales",3,480));
        yes(SchedulePhotoReview.provisionalEstimate(uncertainNames)==3,
            "a short title matching multiple courses must not collapse all three");
        yes(ScheduleCourseRecognition.compare("Historia I","Historia II")==ScheduleCourseRecognition.Relation.DIFFERENT,"Roman levels distinct");
        yes(ScheduleCourseRecognition.compare("Historia","Historia Universal")==ScheduleCourseRecognition.Relation.DIFFERENT,"generic prefix cannot merge");
        yes(ScheduleCourseRecognition.compare("Tendencias Educativas","Tendencias Educativaz")==ScheduleCourseRecognition.Relation.OCR_VARIANT,"OCR typo");
        yes(ScheduleCourseRecognition.compare("Tendencias Educativas","Estadística")==ScheduleCourseRecognition.Relation.DIFFERENT,"unrelated courses");
        yes(ScheduleCourseRecognition.compare("Tendencias","Tenden")==ScheduleCourseRecognition.Relation.DIFFERENT,"reject tiny fragments");
        yes(ScheduleCourseRecognition.compare("Historia (grupo 2)","Historia")==ScheduleCourseRecognition.Relation.DIFFERENT,"manual groups respected");
        List<ScheduleEntry> exact=new ArrayList<>(Arrays.asList(session("Cálculo",1,540),session("Calculo",1,540)));
        yes(SchedulePhotoReview.uniqueBlocks(exact).size()==1,"identical OCR slots deduplicate");
        SchedulePhotoReview.Pair exactPair=SchedulePhotoReview.nextPair(exact,new HashSet<Integer>());
        yes(exactPair!=null&&exactPair.exact,"exact labels still prompted if separately detected");
        SchedulePhotoReview.reject(exact,exactPair);
        yes(exact.get(1).course.contains("grupo 2"),"declined identical courses remain distinct");
        yes(SchedulePhotoReview.nextPair(exact,new HashSet<Integer>())==null,"don't repeatedly prompt rejected group");
        List<ScheduleEntry> several=new ArrayList<>(Arrays.asList(session("Tendencias",1,480),session("Tendencias",3,540),session("Tendencias Educativas",5,600)));
        HashSet<Integer> decided=new HashSet<>();
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(several,decided);
        SchedulePhotoReview.accept(several,pair);decided.add(pair.later);
        pair=SchedulePhotoReview.nextPair(several,decided);
        SchedulePhotoReview.accept(several,pair);
        yes(SchedulePhotoReview.courseEstimate(several)==1,"confirmed group propagates preferred full title");
        yes(several.size()==3,"keep three genuine weekly sessions");
        System.out.println("PASS schedule-photo phase36: 20 checks for OCR partials, ambiguity, decisions, and session safety");
    }
}
