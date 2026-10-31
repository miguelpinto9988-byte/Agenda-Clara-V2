package pe.agendaclara.app;

import java.util.Locale;

/** Display 12-hour time without changing the 24-hour minute storage contract. */
public final class ScheduleDayClock {
    private ScheduleDayClock(){}
    public static final class Slot {
        public final int day;
        public final long id;
        public int start,end;
        public Slot(int day,int start,int end,long id){
            if(day<1||day>7)throw new IllegalArgumentException("Día inválido");
            this.day=day;this.start=start;this.end=end;this.id=id;
        }
    }
    public static int twelveHour(int minutes){
        if(minutes<0||minutes>1440)throw new IllegalArgumentException("Hora inválida");
        return ((minutes%1440)/60+11)%12+1;
    }
    public static boolean isPm(int minutes){
        if(minutes<0||minutes>1440)throw new IllegalArgumentException("Hora inválida");
        return minutes>=720&&minutes<1440;
    }
    public static String clock12(int minutes){
        return String.format(Locale.ROOT,"%02d:%02d",twelveHour(minutes),minutes%60);
    }
    /** 12 AM = 00:xx and 12 PM = 12:xx. */
    public static int toMinutes(int hour,int minute,boolean pm){
        if(hour<1||hour>12||minute<0||minute>59)
            throw new IllegalArgumentException("Hora de 12 h inválida");
        return ((hour%12)+(pm?12:0))*60+minute;
    }
    public static int withMeridiem(int minutes,boolean pm){
        return toMinutes(twelveHour(minutes),minutes%60,pm);
    }
    public static boolean validInterval(int start,int end){
        return start>=0&&end<=1440&&start<end&&end-start<=720;
    }
    public static String display(int minutes){
        return clock12(minutes)+(isPm(minutes)?" PM":" AM")+(minutes==1440?" (día siguiente)":"");
    }
}
