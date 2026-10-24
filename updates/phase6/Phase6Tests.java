import pe.agendaclara.app.*;
import java.time.*;
public final class Phase6Tests {
    static int cases=0;
    static void check(boolean ok,String message){cases++;if(!ok)throw new AssertionError(message);}
    public static void main(String[] args){
        long now=java.time.Instant.parse("2026-10-23T16:00:00Z").toEpochMilli();
        Task t=new Task();t.title="Álgebra y Matemática";t.notes="Presentación del módulo";t.source="Curso de ciencias";t.category="Estudios";
        t.due=now+60*60*1000L;t.created=now-1000;
        check(AgendaFilters.matches(t,0,0,"algebra",null,now),"ignore accent in title");
        check(AgendaFilters.matches(t,0,0,"MATEMATICA",null,now),"ignore uppercase and accents");
        check(AgendaFilters.matches(t,0,0,"modulo",null,now),"match notes");
        check(AgendaFilters.matches(t,0,0,"ciencias",null,now),"match source");
        check(!AgendaFilters.matches(t,0,0,"literatura",null,now),"reject nonmatching search");
        check(AgendaFilters.matches(t,1,0,"",null,now),"urgent due soon");
        check(!AgendaFilters.matches(t,3,0,"",null,now),"not upcoming far deadline");
        check(AgendaFilters.matches(t,0,2,"",null,now),"Estudios category index");
        check(!AgendaFilters.matches(t,0,3,"",null,now),"other category");
        check(!AgendaFilters.matches(t,0,99,"",null,now),"out of bounds category");
        t.done=true;check(AgendaFilters.matches(t,4,0,"",null,now),"done filter");
        t.done=false;check(!AgendaFilters.matches(t,4,0,"",null,now),"not done filter");
        check(AgendaFilters.matches(t,0,0,"",Instant.ofEpochMilli(t.due).atZone(ZoneId.systemDefault()).toLocalDate(),now),"calendar date match");
        check(!ReviewFilters.matches("Examen","Curso","Mensaje",false,0,false,2,"",now),"overdue requires date");
        check(ReviewFilters.matches("Examen","Curso","Mensaje",false,0,false,1,"",now),"missing date");
        check(ReviewFilters.matches("Examen","Curso","Mensaje",true,now-1000,false,2,"",now),"overdue date");
        check(!ReviewFilters.matches("Examen","Curso","Mensaje",true,now+1000,false,2,"",now),"future not overdue");
        check(ReviewFilters.matches("Examen","Curso","Mensaje",true,now+1000,true,3,"",now),"historical");
        check(ReviewFilters.matches("Álgebra","Grupo","Necesitamos entrega",true,now+1000,false,4,"algebra",now),"future seven days and accent search");
        check(!ReviewFilters.matches("Álgebra","Grupo","Necesitamos entrega",true,now+8L*86400000L,false,4,"",now),"reject outside week");
        check(!ReviewFilters.matches("Examen","Grupo","texto",true,now+1000,false,0,"otro",now),"query filter");
        System.out.println("PASS: "+cases+" Phase 2.2 agenda and review matching checks");
    }
}
