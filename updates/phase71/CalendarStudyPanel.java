package pe.agendaclara.app;

import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.view.Gravity;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.List;

/** Calendar > Plan de estudio, using Agenda Clara's existing card/button primitives. */
public final class CalendarStudyPanel {
    private static final int INK=0xff182746;
    private static final int MUTED=0xff61738f;
    private static final int BLUE=0xff3864f4;
    private CalendarStudyPanel(){}

    public static void render(MainActivity a){
        LinearLayout heading=a.card(a.body);
        heading.addView(a.text("Horarios",20,INK,true));
        List<AcademicSchedules.Profile> profiles=AcademicSchedules.all(a);
        heading.addView(a.text("Organiza tus horarios con sus cursos · "+profiles.size()+
                " de "+AcademicSchedules.LIMIT,12,MUTED,false));
        a.gap(heading,12);
        for(AcademicSchedules.Profile p:profiles){
            LinearLayout row=a.column();
            row.setPadding(a.dp(12),a.dp(11),a.dp(12),a.dp(11));
            GradientDrawable background=a.rounded(0xfff0f4ff,15);
            background.setStroke(a.dp(1),0xffdce5fb);
            row.setBackground(background);
            row.addView(a.text(p.name,16,INK,true));
            row.addView(a.text(p.courses.size()+" cursos · Categoría: "+p.name,
                    12,MUTED,false));
            row.setOnClickListener(v->details(a,p));
            row.setFocusable(true);
            row.setContentDescription("Horario "+p.name+", "+p.courses.size()+" cursos. Abrir");
            heading.addView(row);
            a.gap(heading,7);
        }
        if(profiles.isEmpty()){
            heading.addView(a.text("Todavía no tienes horarios organizados. Crea uno para agrupar sus cursos.",
                    13,MUTED,false));
            a.gap(heading,10);
        }
        if(profiles.size()<AcademicSchedules.LIMIT){
            heading.addView(a.button("＋  Nuevo horario",()->newSchedule(a)));
        }else{
            heading.addView(a.text("Has alcanzado el máximo de 10 horarios.",13,MUTED,true));
        }
        a.gap(heading,8);
        heading.addView(a.button("Abrir horario de clases",()->
                a.startActivity(new Intent(a,ScheduleActivity.class))));
        a.gap(a.body,16);

        LinearLayout exams=a.card(a.body);
        exams.addView(a.text("Exámenes y parciales",19,INK,true));
        exams.addView(a.text("Importa un sílabo o registra evaluaciones por curso.",
                12,MUTED,false));
        a.gap(exams,12);
        exams.addView(a.text("La importación de sílabos y sus recordatorios se implementará en la Entrega B.",
                13,MUTED,false));
    }

    private static void newSchedule(MainActivity a){
        EditText field=new EditText(a);
        field.setSingleLine(true);
        field.setHint("Ej.: Educación 2026");
        field.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        LinearLayout wrapper=a.column();
        wrapper.setPadding(a.dp(18),0,a.dp(18),0);
        wrapper.addView(field);
        AlertDialog dialog=new AlertDialog.Builder(a)
                .setTitle("Confirmar nombre del horario")
                .setMessage("Este nombre identificará la categoría de sus cursos y tareas.")
                .setView(wrapper)
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Crear horario",null).create();
        dialog.setOnShowListener(unused->dialog.getButton(AlertDialog.BUTTON_POSITIVE)
                .setOnClickListener(v->{
                    try{
                        AcademicSchedules.create(a,field.getText().toString(),new ArrayList<>());
                        dialog.dismiss();a.render();
                    }catch(IllegalArgumentException|IllegalStateException ex){
                        field.setError(ex.getMessage());
                    }
                }));
        dialog.show();
    }

    private static void details(MainActivity a,AcademicSchedules.Profile profile){
        LinearLayout panel=a.column();
        panel.setPadding(a.dp(18),a.dp(4),a.dp(18),a.dp(4));
        panel.addView(a.text("Categoría: "+profile.name,15,INK,true));
        a.gap(panel,8);
        if(profile.courses.isEmpty())panel.addView(a.text(
                "Aún no hay cursos vinculados. Agrégalos manualmente.",13,MUTED,false));
        else for(String name:profile.courses)panel.addView(a.text("• "+name,14,INK,false));
        a.gap(panel,12);
        panel.addView(a.button("Agregar curso",()->addCourse(a,profile)));
        panel.addView(a.button("Cambiar nombre",()->rename(a,profile)));
        new AlertDialog.Builder(a).setTitle(profile.name).setView(panel)
                .setPositiveButton("Cerrar",null).show();
    }

    private static void addCourse(MainActivity a,AcademicSchedules.Profile profile){
        EditText field=new EditText(a);field.setSingleLine(true);
        field.setHint("Nombre del curso");
        AlertDialog d=new AlertDialog.Builder(a).setTitle("Nuevo curso en "+profile.name)
                .setView(field).setNegativeButton("Cancelar",null)
                .setPositiveButton("Guardar",null).create();
        d.setOnShowListener(x->d.getButton(-1).setOnClickListener(v->{
            String name=field.getText().toString().trim();
            if(name.length()<2){field.setError("Escribe el nombre del curso");return;}
            ArrayList<String> names=new ArrayList<>(profile.courses);
            for(String other:names)if(AcademicSchedules.key(other).equals(AcademicSchedules.key(name))){
                field.setError("Este curso ya existe en el horario");return;
            }
            names.add(name);
            AcademicSchedules.setCourses(a,profile.id,names);
            d.dismiss();a.render();
        }));
        d.show();
    }

    private static void rename(MainActivity a,AcademicSchedules.Profile profile){
        EditText field=new EditText(a);field.setSingleLine(true);field.setText(profile.name);
        AlertDialog d=new AlertDialog.Builder(a).setTitle("Editar nombre del horario")
                .setView(field).setNegativeButton("Cancelar",null)
                .setPositiveButton("Guardar",null).create();
        d.setOnShowListener(x->d.getButton(-1).setOnClickListener(v->{
            try{AcademicSchedules.rename(a,profile.id,field.getText().toString());
                d.dismiss();a.render();}
            catch(IllegalArgumentException ex){field.setError(ex.getMessage());}
        }));
        d.show();
    }
}
