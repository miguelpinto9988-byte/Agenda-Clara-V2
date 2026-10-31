import pe.agendaclara.app.ScheduleDayClock;
import pe.agendaclara.app.ScheduleEntry;
import java.util.*;
public final class ScheduleDayClockTests {
    private static int tests;
    private static void ok(boolean b,String message){tests++;if(!b)throw new AssertionError(message);}
    public static void main(String[] unused){
        ok(ScheduleDayClock.toMinutes(12,0,false)==0,"midnight");
        ok(ScheduleDayClock.toMinutes(12,0,true)==720,"noon");
        ok(ScheduleDayClock.toMinutes(10,0,false)==600,"10 am");
        ok(ScheduleDayClock.toMinutes(8,0,false)==480,"8 am");
        ok(ScheduleDayClock.toMinutes(4,30,true)==990,"4:30 pm");
        ok(ScheduleDayClock.toMinutes(6,0,true)==1080,"6 pm");
        ok(ScheduleDayClock.twelveHour(0)==12,"12 am shows 12");
        ok(ScheduleDayClock.twelveHour(720)==12,"12 pm shows 12");
        ok(ScheduleDayClock.isPm(780)&&!ScheduleDayClock.isPm(660),"AM PM classification");
        ok("12:00 AM".equals(ScheduleDayClock.display(0)),"midnight display");
        ok("12:00 PM".equals(ScheduleDayClock.display(720)),"noon display");
        ok("04:30 PM".equals(ScheduleDayClock.display(990)),"PM display");
        ok(ScheduleDayClock.withMeridiem(600,true)==1320,"switch 10 AM to 10 PM");
        ok(ScheduleDayClock.withMeridiem(780,false)==60,"switch 1 PM to 1 AM");
        ok(ScheduleDayClock.validInterval(600,700),"Monday different hour");
        ok(ScheduleDayClock.validInterval(480,570),"Wednesday different hour");
        ok(!ScheduleDayClock.validInterval(800,700),"end must follow start");
        ok(!ScheduleDayClock.validInterval(480,1300),"12h max duration");
        ok(ScheduleDayClock.validInterval(720,780),"noon slot");
        ok(ScheduleDayClock.validInterval(0,60),"midnight slot");
        ok("12:00 AM (día siguiente)".equals(ScheduleDayClock.display(1440)),"24h end rendered unambiguously");
        TreeMap<Integer,ScheduleDayClock.Slot> days=new TreeMap<>();
        days.put(1,new ScheduleDayClock.Slot(1,600,700,11));
        days.put(3,new ScheduleDayClock.Slot(3,480,570,12));
        ok(days.size()==2&&days.get(1).start!=days.get(3).start,"different hours independent");
        ok(days.get(1).id==11&&days.get(3).id==12,"different records independent");
        ScheduleEntry monday=new ScheduleEntry();monday.course="Tendencias Educativas";monday.day=1;monday.start=days.get(1).start;monday.end=days.get(1).end;
        ScheduleEntry wednesday=monday.copy();wednesday.day=3;wednesday.start=days.get(3).start;wednesday.end=days.get(3).end;
        ok(ScheduleEntry.valid(monday)&&ScheduleEntry.valid(wednesday),"both database sessions valid");
        try{ScheduleDayClock.toMinutes(0,50,true);throw new AssertionError("invalid hour accepted");}catch(IllegalArgumentException expected){tests++;}
        System.out.println("PASS phase37: "+tests+" time conversion, independent day sessions and interval checks");
    }
}
