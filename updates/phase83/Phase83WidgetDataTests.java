package pe.agendaclara.app;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.List;

/** Data fixtures: one course/profile must not leak into another widget. */
public final class Phase83WidgetDataTests {
    private static void check(boolean success,String message){
        if(!success)throw new AssertionError(message);
    }
    public static void main(String[] args){
        LocalDate day=LocalDate.of(2026,11,5);
        AcademicWidgetModels.ClassSession own=new AcademicWidgetModels.ClassSession(
            "profile-a","mathematics","Matemática","B-201",4,
            LocalTime.of(9,0),LocalTime.of(11,0));
        AcademicWidgetModels.ClassSession other=new AcademicWidgetModels.ClassSession(
            "profile-b","mathematics","Matemática","A-203",4,
            LocalTime.of(8,0),LocalTime.of(10,0));
        List<AcademicWidgetModels.TaskItem> tasks=Arrays.asList(
            new AcademicWidgetModels.TaskItem(1,"profile-a","mathematics","Tarea actual",day,false),
            new AcademicWidgetModels.TaskItem(2,"profile-a","mathematics","Tarea futura",day.plusDays(2),false),
            new AcademicWidgetModels.TaskItem(3,"profile-a","history","Otra materia",day,false),
            new AcademicWidgetModels.TaskItem(4,"profile-b","mathematics","Perfil distinto",day,false),
            new AcademicWidgetModels.TaskItem(5,"profile-a","mathematics","Completada",day,true));
        AcademicWidgetModels.Day widget=AcademicWidgetModels.day(
            "profile-a",day,LocalTime.of(8,30),Arrays.asList(own,other),tasks);
        check(widget.nextClass==own,"Next class must belong to selected profile");
        check(widget.tasks.size()==1&&widget.tasks.get(0).id==1,
            "Tasks must match profile, course, pending state and selected day");
        AcademicWidgetModels.Evaluation unknown=new AcademicWidgetModels.Evaluation(
            "profile-a","mathematics","Matemática","Examen parcial","PARCIAL",null,14);
        AcademicWidgetModels.Evaluation outsider=new AcademicWidgetModels.Evaluation(
            "profile-b","mathematics","Matemática","Evaluación externa","PARCIAL",day,14);
        check(unknown.when().contains("Fecha por confirmar"),"Never invent academic dates");
        List<AcademicWidgetModels.Evaluation> evaluations=
            AcademicWidgetModels.evaluationsForCourse(
                "profile-a","mathematics",Arrays.asList(unknown,outsider));
        check(evaluations.size()==1&&evaluations.get(0)==unknown,
            "Assessments cannot leak across profiles or courses");
        System.out.println("PASS: next class and tasks are course/profile scoped");
        System.out.println("PASS: completed, future and unrelated tasks excluded");
        System.out.println("PASS: evaluation dates remain unknown until corroborated");
    }
}
