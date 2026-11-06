package pe.agendaclara.app;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/** Immutable presentation models. No database writes or fabricated academic dates. */
public final class AcademicWidgetModels {
    private AcademicWidgetModels() {}
    public static final class ClassSession {
        public final String profileId, courseId, course, room;
        public final int dayOfWeek;
        public final LocalTime start, end;
        public ClassSession(String profileId,String courseId,String course,String room,
                            int dayOfWeek,LocalTime start,LocalTime end){
            if(dayOfWeek<1||dayOfWeek>7||start==null||end==null||!end.isAfter(start))
                throw new IllegalArgumentException("Invalid class session");
            this.profileId=profileId;this.courseId=courseId;this.course=course;this.room=room;
            this.dayOfWeek=dayOfWeek;this.start=start;this.end=end;
        }
    }
    public static final class Evaluation {
        public final String profileId,courseId,course,title,type;
        public final LocalDate date;
        public final int academicWeek;
        public Evaluation(String profileId,String courseId,String course,String title,
                          String type,LocalDate date,int academicWeek){
            this.profileId=profileId;this.courseId=courseId;this.course=course;
            this.title=title;this.type=type;this.date=date;this.academicWeek=academicWeek;
        }
        public String when(){
            if(date!=null)return date.toString();
            return academicWeek>0?"Semana "+academicWeek+" · Fecha por confirmar":"Fecha por confirmar";
        }
    }
    public static final class TaskItem {
        public final long id;
        public final String profileId,courseId,title;
        public final LocalDate due;
        public final boolean done;
        public TaskItem(long id,String profileId,String courseId,String title,LocalDate due,boolean done){
            this.id=id;this.profileId=profileId;this.courseId=courseId;this.title=title;
            this.due=due;this.done=done;
        }
    }
    public static final class Day {
        public final ClassSession nextClass;
        public final List<TaskItem> tasks;
        public Day(ClassSession nextClass,List<TaskItem> tasks){
            this.nextClass=nextClass;
            this.tasks=Collections.unmodifiableList(new ArrayList<>(tasks));
        }
    }
    public static Day day(String profileId,LocalDate today,LocalTime now,
                          List<ClassSession> classes,List<TaskItem> tasks){
        ClassSession next=null;
        for(ClassSession item:classes){
            if(!profileId.equals(item.profileId))continue;
            if(item.dayOfWeek!=today.getDayOfWeek().getValue()||!item.end.isAfter(now))continue;
            if(next==null||item.start.isBefore(next.start))next=item;
        }
        List<TaskItem> relevant=new ArrayList<>();
        for(TaskItem task:tasks){
            if(task.done||!profileId.equals(task.profileId))continue;
            if(task.due!=null&&task.due.isAfter(today))continue;
            if(next!=null&&!next.courseId.equals(task.courseId))continue;
            relevant.add(task);
        }
        relevant.sort(Comparator.comparing((TaskItem t)->t.due,
                Comparator.nullsLast(Comparator.naturalOrder())).thenComparingLong(t->t.id));
        return new Day(next,relevant);
    }
    public static List<Evaluation> evaluationsForCourse(String profileId,String courseId,
                                                          List<Evaluation> all){
        List<Evaluation> result=new ArrayList<>();
        for(Evaluation item:all)
            if(profileId.equals(item.profileId)&&courseId.equals(item.courseId))
                result.add(item);
        result.sort(Comparator.comparing((Evaluation e)->e.date,
                Comparator.nullsLast(Comparator.naturalOrder()))
                .thenComparing(e->e.title));
        return result;
    }
}
