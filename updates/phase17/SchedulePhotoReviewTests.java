import pe.agendaclara.app.*;
import java.util.*;
public final class SchedulePhotoReviewTests {
    private static int n=0;
    static void ok(boolean value,String note){n++;if(!value)throw new AssertionError(note);}
    static ScheduleEntry s(String course,int day,int st,int en){
        ScheduleEntry e=new ScheduleEntry();e.course=course;e.day=day;e.start=st;e.end=en;return e;
    }
    static List<ScheduleEntry> sample(){
        return new ArrayList<>(Arrays.asList(
            s("Tutoría Educativa",1,420,520),s("Tutoría Educativa",3,600,700),
            s("Recursos Digitales",1,530,630),s("Recursos Digitales",4,600,700),
            s("Textos Líricos",2,420,520),s("Texto Lírico",4,600,700),
            s("Didáctica de la Lengua y Literatura II",2,530,690),s("Didáctica de la Lengua y Literatura II",5,420,520),
            s("Tendencias Educativas (E)",3,420,520),s("Tendencias Educativas (E)",5,600,700),
            s("Responsabilidad Social y Rendición de Cuentas (E)",3,530,630),
            s("Investigación Educativa I",4,420,520),s("Investigacion Educaiva I",6,600,700),
            s("Literatura Hispanoamericana",5,530,630)
        ));
    }
    public static void main(String[] args){
        List<ScheduleEntry> list=sample();
        ok(list.size()==14,"14 blocks, not 14 subjects");
        ok(SchedulePhotoReview.courseEstimate(list)>=8,"initial estimate is not a hard course count");
        Set<Integer> resolved=new HashSet<>();
        int prompts=0;
        while(true){
            SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(list,resolved);
            if(pair==null)break;
            int originalDay=list.get(pair.later).day;
            int originalStart=list.get(pair.later).start;
            int originalEnd=list.get(pair.later).end;
            SchedulePhotoReview.accept(list,pair);
            resolved.add(pair.later);
            prompts++;
            ok(list.get(pair.later).day==originalDay,"day retained");
            ok(list.get(pair.later).start==originalStart && list.get(pair.later).end==originalEnd,"distinct times retained");
            ok(prompts<20,"resolution is finite");
        }
        ok(SchedulePhotoReview.courseEstimate(list)==8,"14 weekly blocks -> exactly 8 courses");
        ok(prompts==6,"6 explicit accept/reject dialogs");
        ok(list.get(0).start==420&&list.get(1).start==600,"same course, independent day hours");

        List<ScheduleEntry> deny=new ArrayList<>(Arrays.asList(s("Matemáticas",1,420,480),s("Matemáticas",3,600,660)));
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(deny,new HashSet<>());
        ok(pair!=null&&pair.exact,"identical OCR labels require explicit confirmation");
        SchedulePhotoReview.reject(deny,pair);
        ok(SchedulePhotoReview.courseEstimate(deny)==2,"negative answer => two independent courses");
        ok(deny.get(1).course.contains("grupo 2"),"separate label persists in database");
        ok(deny.get(1).start==600,"negative answer preserves time");
        ok(SchedulePhotoReview.nextPair(deny,new HashSet<>())==null,"refused pair not presented repeatedly");
        List<ScheduleEntry> ordinal=Arrays.asList(s("Historia I",1,420,480),s("Historia II",2,600,660));
        ok(SchedulePhotoReview.nextPair(ordinal,new HashSet<>())==null,"level I and II are not the same course");
        List<ScheduleEntry> unique=SchedulePhotoReview.uniqueBlocks(Arrays.asList(
          s("Textos Líricos",1,420,480),s("Texto Lírico",1,420,480),s("Textos Líricos",3,600,660)));
        ok(unique.size()==2,"same day/time same normalized name appears only once; other day retained");

        ArrayList<ScheduleGridInterpreter.Line> preview=new ArrayList<>();
        preview.add(new ScheduleGridInterpreter.Line("Lunes",100,20,150,40));
        preview.add(new ScheduleGridInterpreter.Line("Miércoles",200,20,270,40));
        preview.add(new ScheduleGridInterpreter.Line("07:00–08:00",25,60,99,70));
        preview.add(new ScheduleGridInterpreter.Line("Tutoría Educativa",150,65,320,85));
        SchedulePhotoReview.Overview o=SchedulePhotoReview.overview(preview);
        ok(o.weekdayHeaders==2&&o.timeLabels==1&&o.textLines==4,"stage 1 overview counts labels");
        System.out.println("PASS: "+n+" assertions — 8 courses, 14 blocks, explicit review and different day times");
    }
}
