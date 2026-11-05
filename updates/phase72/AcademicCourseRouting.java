package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import java.util.ArrayList;
import java.util.List;

/** Confirmation UI for manual and voice tasks. Never silently chooses a course. */
public final class AcademicCourseRouting {
    private AcademicCourseRouting(){}
    public interface Decision {
        /** null means the user explicitly saved without a course. */
        void decided(AcademicCourseMatcher.Course course);
    }
    public static List<AcademicCourseMatcher.Course> catalog(Activity activity) {
        ArrayList<AcademicCourseMatcher.Course> courses=new ArrayList<>();
        for(AcademicSchedules.Profile profile:AcademicSchedules.all(activity)) {
            for(String name:profile.courses)
                courses.add(new AcademicCourseMatcher.Course(profile.id,profile.category,name));
        }
        return courses;
    }
    public static void review(Activity activity,String phrase,String chosenCategory,
                              Decision onConfirm) {
        List<AcademicCourseMatcher.Match> matches=AcademicCourseMatcher.matches(phrase,catalog(activity));
        if(matches.isEmpty()) {
            // No speculative assignment: preserve the editor's selected category.
            onConfirm.decided(null);return;
        }
        ArrayList<AcademicCourseMatcher.Match> prioritized=new ArrayList<>();
        for(AcademicCourseMatcher.Match match:matches)
            if(chosenCategory!=null && match.course.category.equalsIgnoreCase(chosenCategory))
                prioritized.add(match);
        if(!prioritized.isEmpty())matches=prioritized;
        final List<AcademicCourseMatcher.Match> options=matches;
        String[] labels=new String[options.size()];
        for(int i=0;i<labels.length;i++){
            AcademicCourseMatcher.Course c=options.get(i).course;
            AcademicSchedules.Profile profile=AcademicSchedules.find(activity,c.profileId);
            labels[i]=c.name+" · "+(profile!=null?profile.name:c.category);
        }
        final int[] selected={0};
        AlertDialog dialog=new AlertDialog.Builder(activity,R.style.DialogTheme)
                .setTitle("¿A qué curso pertenece esta tarea?")
                .setMessage("Se detectó una posible coincidencia. Confirma antes de guardarla.")
                .setSingleChoiceItems(labels,0,(d,which)->selected[0]=which)
                .setNegativeButton("Volver",null)
                .setNeutralButton("Guardar sin curso",(d,w)->onConfirm.decided(null))
                .setPositiveButton("Confirmar curso",(d,w)->onConfirm.decided(
                        options.get(selected[0]).course))
                .create();
        dialog.show();
        WindowLayout.boundDialog(activity,dialog);
    }
    public static void chooseAny(Activity activity,Decision onConfirm) {
        List<AcademicCourseMatcher.Course> options=catalog(activity);
        if(options.isEmpty()){
            new AlertDialog.Builder(activity,R.style.DialogTheme)
                    .setTitle("Todavía no tienes cursos")
                    .setMessage("Crea un horario con cursos en Calendario > Plan de estudio.")
                    .setPositiveButton("Entendido",null).show();
            return;
        }
        String[] names=new String[options.size()];
        for(int i=0;i<options.size();i++){
            AcademicCourseMatcher.Course c=options.get(i);
            AcademicSchedules.Profile profile=AcademicSchedules.find(activity,c.profileId);
            names[i]=c.name+" · "+(profile==null?c.category:profile.name);
        }
        new AlertDialog.Builder(activity,R.style.DialogTheme)
                .setTitle("Elegir curso y horario")
                .setItems(names,(d,index)->onConfirm.decided(options.get(index)))
                .setNegativeButton("Cancelar",null).show();
    }
}
