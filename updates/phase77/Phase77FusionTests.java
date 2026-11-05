package pe.agendaclara.app;

import java.util.*;

/** Deterministic tests of multi-source OCR, uncertain candidates and user choices. */
public final class Phase77FusionTests {
    private static void check(boolean ok,String message) {
        if(!ok)throw new AssertionError(message);
    }
    private static ScheduleEntry entry(String course,int day,int start,int end) {
        ScheduleEntry e=new ScheduleEntry();
        e.course=course;e.day=day;e.start=start;e.end=end;
        e.color=ScheduleCourseColors.deterministic(course);
        return e;
    }
    private static ScheduleParser.Result result(ScheduleEntry... entries) {
        ScheduleParser.Result result=new ScheduleParser.Result();
        result.candidates.addAll(Arrays.asList(entries));return result;
    }
    private static int optionalCount(ScheduleParser.Result result) {
        int n=0;
        for(ScheduleEntry e:result.candidates)
            if(result.reviewOnlyKeys.contains(ScheduleOcrFusion.key(e)))n++;
        return n;
    }
    public static void main(String[] args) {
        ScheduleParser.Result rectangles=result(
            entry("Tendencias educativas",1,480,540),
            entry("Historia",2,540,600));
        ScheduleParser.Result virtual=result(
            entry("Tendencias educativas",1,480,540), // duplicate: skip
            entry("Tendencias",1,480,540), // truncated name in same slot: show
            entry("Didáctica",3,600,660)); // new cell: show
        ScheduleParser.Result text=result(
            entry("Didáctica",3,600,660), // duplicate supplement: skip
            entry("Historia económica",2,540,600), // same cell alternate: show
            entry("Metodología",4,720,780)); // missed subject: show
        ScheduleParser.Result out=ScheduleOcrFusion.reconcile(rectangles,virtual,text);
        check(out.candidates.size()==6,"Primary 2 + four optional readings: "+out.candidates.size());
        check(optionalCount(out)==4,"All four supplements must remain unchecked");
        check(out.reviewOnlyKeys.size()==4,"Stable fingerprint, not index");
        check(ScheduleCourseColors.same(out.candidates.get(0).course,"Tendencias educativas"),
                "Original rectangular reading unchanged");
        check(out.uncertain.toString().contains("desmarcadas")||
              out.uncertain.toString().contains("DESMARCADAS"),
              "Supplemental readings must instruct review");
        for(ScheduleEntry proposed:out.candidates)
            check(ScheduleEntry.valid(proposed),"No malformed entry imported");
        ScheduleParser.Result fallback=ScheduleOcrFusion.reconcile(
            result(),result(entry("Literatura",1,480,540)),
            result(entry("Comunicación",2,540,600)));
        check(fallback.candidates.size()==2&&optionalCount(fallback)==1,
                "Virtual primary, text secondary when rectangles absent");
        ScheduleParser.Result onlyText=ScheduleOcrFusion.reconcile(
            result(),result(),result(entry("Arte",1,480,540)));
        check(onlyText.candidates.size()==1&&optionalCount(onlyText)==0,
                "Text reader remains usable when no grid geometry exists");
        ScheduleParser.Result empty=ScheduleOcrFusion.reconcile(result(),result(),result());
        check(empty.candidates.isEmpty()&&!empty.uncertain.isEmpty(),
                "Empty OCR must explain the need for manual classes");

        ArrayList<ScheduleEntry> courseGroup=new ArrayList<>();
        courseGroup.add(entry("Tendencias",1,480,540));
        courseGroup.add(entry("Tendencias educativas",3,600,660));
        courseGroup.add(entry("Tendencias",5,720,780));
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(courseGroup,
            new HashSet<>(),new HashSet<>());
        check(pair!=null,"Partial course requires a confirmation");
        SchedulePhotoReview.acceptWithName(courseGroup,pair,"Tendencias educativas");
        for(ScheduleEntry e:courseGroup)
            check(e.course.equals("Tendencias educativas"),
                    "All sessions of both spellings must share confirmed full name");
        check(courseGroup.get(0).day==1&&courseGroup.get(0).start==480&&
              courseGroup.get(1).day==3&&courseGroup.get(1).start==600&&
              courseGroup.get(2).day==5&&courseGroup.get(2).start==720,
              "Merging labels must preserve all dates and hours");
        check(ScheduleCourseRecognition.compare("Historia (grupo 2)",
              "Historia (grupo 2)")==ScheduleCourseRecognition.Relation.EXACT,
              "Same explicit course group is exact across days");
        check(ScheduleCourseRecognition.compare("Historia (grupo 2)",
              "Historia (grupo 3)")==ScheduleCourseRecognition.Relation.DIFFERENT,
              "Different course groups are distinct");

        List<ScheduleGridInterpreter.Line> oneDay=Arrays.asList(
            new ScheduleGridInterpreter.Line("Lunes",330,20,400,42),
            new ScheduleGridInterpreter.Line("08:00 - 09:00",5,142,104,162),
            new ScheduleGridInterpreter.Line("Literatura",325,140,410,161));
        List<ScheduleGridInterpreter.Tile> oneTile=Arrays.asList(
            new ScheduleGridInterpreter.Tile(290,120,460,205));
        ScheduleParser.Result grid=ScheduleGridInterpreter.parse(oneDay,oneTile,800,600);
        check(grid.candidates.size()==1,"Single-day/one-row photo must parse a class");
        ScheduleParser.Result virtualGrid=ScheduleVirtualGrid.parse(oneDay,800,600);
        check(virtualGrid.candidates.size()==1,
                "Single-day/one-row photo must parse without colored tiles");
        System.out.println("PASS 3.13.7: three OCR readers retain missed classes for optional review");
        System.out.println("PASS 3.13.7: original classes unchanged, canonical name user-chosen");
        System.out.println("PASS 3.13.7: one-day timetable and single period supported");
    }
}
