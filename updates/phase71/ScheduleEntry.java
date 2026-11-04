package pe.agendaclara.app;

import java.time.*;

/** One recurring class, scoped to a stable schedule profile UUID. */
public final class ScheduleEntry {
    public long id;
    public String course="",room="",teacher="",notes="",scheduleId="";
    public int day=1,start=480,end=540,color=0xff4989f7,reminder=10;
    public boolean enabled=true;
    public ScheduleEntry copy(){
        ScheduleEntry s=new ScheduleEntry();s.id=id;s.course=course;s.room=room;
        s.teacher=teacher;s.notes=notes;s.day=day;s.start=start;s.end=end;
        s.color=color;s.reminder=reminder;s.enabled=enabled;s.scheduleId=scheduleId;
        return s;
    }
    public static String clock(int minutes){
        return String.format(java.util.Locale.ROOT,"%02d:%02d",minutes/60,minutes%60);
    }
    public static int minutes(String input){
        if(input==null)return -1;
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("^\\s*(\\d{1,2})[:.](\\d{2})\\s*$").matcher(input);
        if(!m.matches())return -1;
        int h=Integer.parseInt(m.group(1)),v=Integer.parseInt(m.group(2));
        return h<24&&v<60?h*60+v:-1;
    }
    public static boolean valid(ScheduleEntry s){
        return s!=null&&s.course!=null&&!s.course.trim().isEmpty()&&s.course.length()<=120
                &&s.day>=1&&s.day<=7&&s.start>=0&&s.end<=1440&&s.start<s.end
                &&s.end-s.start<=720&&s.room!=null&&s.teacher!=null&&s.notes!=null
                &&s.room.length()<=140&&s.teacher.length()<=140&&s.notes.length()<=1000;
    }
    public static final int[] COLORS={0xff60a5fa,0xfff48ca5,0xff9f83f5,0xff48c6b5,
            0xfff3c456,0xff55cb87,0xff89b7ff};
    public static String dayName(int day){
        String[] x={"","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"};
        return day>=1&&day<=7?x[day]:"?";
    }
}
