package pe.agendaclara.app;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class AcademicWidgetModelsTests {
    private static void check(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    public static void main(String[] args){
        LocalDate day=LocalDate.of(2026,11,5);
        AcademicWidgetModels.ClassSession course=new AcademicWidgetModels.ClassSession(
                "horario-a","curso-a","Tendencias educativas","204",4,
                LocalTime.of(9,0),LocalTime.of(11,0));
        AcademicWidgetModels.ClassSession other=new AcademicWidgetModels.ClassSession(
                "horario-b","curso-a","Tendencias educativas","105",4,
                LocalTime.of(8,0),LocalTime.of(10,0));
        List<AcademicWidgetModels.TaskItem> tasks=Arrays.asList(
                new AcademicWidgetModels.TaskItem(1,"horario-a","curso-a","Exposición",day,false),
                new AcademicWidgetModels.TaskItem(2,"horario-b","curso-a","Ajena",day,false),
                new AcademicWidgetModels.TaskItem(3,"horario-a","curso-a","Terminada",day,true),
                new AcademicWidgetModels.TaskItem(4,"horario-a","curso-a","Futura",day.plusDays(2),false));
        AcademicWidgetModels.Day snapshot=AcademicWidgetModels.day("horario-a",day,
                LocalTime.of(8,30),Arrays.asList(other,course),tasks);
        check(snapshot.nextClass==course,"wrong profile selected");
        check(snapshot.tasks.size()==1&&snapshot.tasks.get(0).id==1,"task leakage");
        AcademicWidgetModels.Evaluation pending=new AcademicWidgetModels.Evaluation(
                "horario-a","curso-a","Tendencias educativas","Proyecto final",
                "FINAL",null,15);
        check(pending.when().contains("Fecha por confirmar"),"invented date");
        check(AcademicWidgetModels.evaluationsForCourse("horario-b","curso-a",
                Collections.singletonList(pending)).isEmpty(),"evaluation leakage");
        System.out.println("PASS: profile isolation, class, tasks, pending evaluation");
    }
}
