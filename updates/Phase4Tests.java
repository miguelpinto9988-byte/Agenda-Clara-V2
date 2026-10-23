import pe.agendaclara.app.*;
import java.time.*;
import java.util.*;

/** Pure JVM regression for transparent task progress after automatic purging. */
public final class Phase4Tests {
  static int checks=0;
  static void verify(boolean truth,String description){
    checks++;
    if(!truth)throw new AssertionError(description);
  }
  static Task task(long id,long due,boolean done,boolean urgent){
    Task t=new Task();t.id=id;t.title="synthetic-"+id;t.due=due;t.done=done;t.urgent=urgent;
    t.created=100;return t;
  }
  public static void main(String[] args){
    long now=java.time.Instant.parse("2026-10-23T18:00:00Z").toEpochMilli();
    List<Task> data=new ArrayList<>();
    TaskSummary.Result empty=TaskSummary.calculate(data,now,0);
    verify(empty.percentage==100,"No pending work is 100 percent");
    verify(empty.pending==0,"Empty agenda");
    data.add(task(1,now+10*86400000L,false,false));
    data.add(task(2,now+2*86400000L,false,true));
    data.add(task(3,now-86400000L,true,false));
    TaskSummary.Result r=TaskSummary.calculate(data,now,5);
    verify(r.pending==2,"Pending ignores already-completed tasks");
    verify(r.completedToday==1,"Visible completions remain independent of history");
    verify(r.urgent>=1,"Manual urgent detection");
    verify(r.completed7days==5,"Historical completion survives task purge");
    verify(r.percentage==71,"Progress from week completed / (week completed + pending)");
    verify(TaskSummary.calculate(data,now,0).percentage==0,"No complete tasks yields zero percent");
    verify(TaskSummary.calculate(data,now,Integer.MAX_VALUE).percentage<=100,"Large histories stay bounded");
    verify(TaskSummary.calculate(data,now,-10).completed7days==0,"Negative counts rejected");
    data.clear();data.add(task(4,now+10000000,false,false));
    verify(TaskSummary.calculate(data,now,0).percentage==0,"Unfinished-only snapshot");
    data.clear();
    verify(TaskSummary.calculate(data,now,3).percentage==100,"Archive-only snapshot");
    System.out.println("{\"checks\":"+checks+",\"passed\":"+checks+",\"failed\":0,\"scope\":\"2.0 historical productivity and snapshot\"}");
  }
}