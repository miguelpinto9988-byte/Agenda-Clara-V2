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

/** Original Agenda Clara white/pastel visual language in Calendario > Plan de estudio. */
public final class CalendarStudyPanel {
    private static final int INK=0xff182746,MUTED=0xff61738f,BLUE=0xff3864f4;
    private CalendarStudyPanel(){}

    public static void render(MainActivity a){
        LinearLayout schedules=a.card(a.body);
        List<AcademicSchedules.Profile> profiles=AcademicSchedules.all(a);
        schedules.addView(a.text("Horarios",20,INK,true));
        schedules.addView(a.text("Organiza hasta 10 horarios con cursos y categorías independientes.",
                12,MUTED,false));
        a.gap(schedules,8);
        schedules.addView(a.text(profiles.size()+" de "+AcademicSchedules.LIMIT+" horarios",13,BLUE,true));
        a.gap(schedules,12);

        for(AcademicSchedules.Profile initial:profiles){
            AcademicSchedules.syncFromSessions(a,initial.id);
            AcademicSchedules.Profile p=AcademicSchedules.find(a,initial.id);
            LinearLayout card=a.column();
            card.setPadding(a.dp(14),a.dp(12),a.dp(14),a.dp(12));
            GradientDrawable bg=a.rounded(0xfff0f4ff,16);
            bg.setStroke(a.dp(1),0xffdce5fb);
            card.setBackground(bg);
            card.addView(a.text(p.name+"   ›",16,INK,true));
            card.addView(a.text(p.courses.size()+" cursos · "+
                    ScheduleDatabase.get(a).all(p.id).size()+" clases semanales",12,MUTED,false));
            card.setFocusable(true);card.setClickable(true);
            card.setContentDescription("Abrir horario "+p.name);
            card.setOnClickListener(v->details(a,p.id));
            schedules.addView(card);
            a.gap(schedules,8);
        }
        if(profiles.isEmpty()){
            schedules.addView(a.text("Aún no tienes horarios. Crea uno nuevo o importa una fotografía.",
                    13,MUTED,false));
            a.gap(schedules,12);
        }
        if(profiles.size()<AcademicSchedules.LIMIT)
            schedules.addView(a.button("＋  Nuevo horario",()->newSchedule(a,false)));
        else schedules.addView(a.text("Máximo de diez horarios alcanzado. Puedes gestionar los existentes.",
                13,BLUE,true));
        schedules.addView(a.button("Importar horario desde foto",()->importPhoto(a)));
        a.gap(a.body,15);

        LinearLayout exams=a.card(a.body);
        exams.addView(a.text("Exámenes y parciales",19,INK,true));
        a.gap(exams,5);
        exams.addView(a.text("Importación de sílabos, exámenes y recordatorios: Entrega B.",
                12,MUTED,false));
        a.gap(exams,10);
        exams.addView(a.text("Los cursos registrados aquí estarán disponibles para elegir al crear evaluaciones.",
                13,MUTED,false));
    }

    private static EditText field(MainActivity a,String hint,String value){
        EditText edit=new EditText(a);
        edit.setSingleLine(true);
        edit.setText(value);
        edit.setHint(hint);
        edit.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        return edit;
    }
    private static LinearLayout wrapper(MainActivity a,EditText edit){
        LinearLayout box=a.column();
        box.setPadding(a.dp(20),a.dp(4),a.dp(20),a.dp(6));
        box.addView(edit);
        return box;
    }
    private static void open(MainActivity a,AcademicSchedules.Profile p,boolean photo){
        AcademicSchedules.activate(a,p.id);
        Intent i=new Intent(a,ScheduleActivity.class);
        i.putExtra("profile_id",p.id);
        if(photo)i.putExtra("start_photo",true);
        a.startActivity(i);
    }

    private static void newSchedule(MainActivity a,boolean photo){
        EditText input=field(a,"Ej.: Educación 2026","");
        AlertDialog dialog=a.dialogBuilder().setTitle("Nuevo horario")
                .setMessage("Confirma el nombre que identificará su categoría y sus cursos.")
                .setView(wrapper(a,input)).setNegativeButton("Cancelar",null)
                .setPositiveButton("Crear horario",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{
                AcademicSchedules.Profile p=AcademicSchedules.create(a,input.getText().toString(),
                        new ArrayList<String>());
                dialog.dismiss();
                open(a,p,photo);
            }catch(IllegalArgumentException|IllegalStateException err){
                input.setError(err.getMessage());
            }
        }));
        dialog.show();
    }
    private static void importPhoto(MainActivity a){
        List<AcademicSchedules.Profile> profiles=AcademicSchedules.all(a);
        if(profiles.isEmpty()){newSchedule(a,true);return;}
        ArrayList<String> options=new ArrayList<>();
        for(AcademicSchedules.Profile p:profiles)options.add(p.name);
        if(profiles.size()<AcademicSchedules.LIMIT)options.add("＋ Crear horario nuevo");
        a.dialogBuilder().setTitle("¿A qué horario pertenece la foto?")
                .setItems(options.toArray(new String[0]),(dialog,which)->{
                    if(which==profiles.size()){newSchedule(a,true);return;}
                    open(a,profiles.get(which),true);
                }).setNegativeButton("Cancelar",null).show();
    }
    private static void details(MainActivity a,String profileId){
        AcademicSchedules.Profile p=AcademicSchedules.find(a,profileId);
        if(p==null){a.render();return;}
        LinearLayout box=a.column();
        box.setPadding(a.dp(18),a.dp(5),a.dp(18),a.dp(5));
        box.addView(a.text("Categoría: "+p.category,14,BLUE,true));
        a.gap(box,8);
        if(p.courses.isEmpty())
            box.addView(a.text("Todavía no hay cursos registrados.",13,MUTED,false));
        else for(String course:p.courses)box.addView(a.text("• "+course,14,INK,false));
        a.gap(box,12);
        box.addView(a.button("Abrir clases de este horario",()->open(a,p,false)));
        box.addView(a.button("Agregar curso",()->addCourse(a,p.id)));
        box.addView(a.button("Cambiar nombre",()->rename(a,p.id)));
        box.addView(a.button("Eliminar este horario",()->confirmDelete(a,p.id)));
        a.dialogBuilder().setTitle(p.name).setView(box).setPositiveButton("Cerrar",null).show();
    }
    private static void addCourse(MainActivity a,String id){
        AcademicSchedules.Profile p=AcademicSchedules.find(a,id);
        if(p==null)return;
        EditText input=field(a,"Nombre del curso","");
        AlertDialog dialog=a.dialogBuilder().setTitle("Curso de "+p.name)
                .setView(wrapper(a,input)).setNegativeButton("Cancelar",null)
                .setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            String name=input.getText().toString().trim();
            if(name.length()<2||name.length()>120){
                input.setError("Indica un nombre de 2 a 120 caracteres");return;
            }
            for(String existing:p.courses)if(AcademicSchedules.key(existing).equals(
                    AcademicSchedules.key(name))){
                input.setError("El curso ya existe en este horario");return;
            }
            ArrayList<String> courses=new ArrayList<>(p.courses);courses.add(name);
            AcademicSchedules.setCourses(a,p.id,courses);
            dialog.dismiss();a.render();
        }));
        dialog.show();
    }
    private static void rename(MainActivity a,String id){
        AcademicSchedules.Profile p=AcademicSchedules.find(a,id);
        if(p==null)return;
        EditText input=field(a,"Nombre del horario",p.name);
        AlertDialog dialog=a.dialogBuilder().setTitle("Renombrar horario")
                .setMessage("La categoría académica se actualizará sin borrar las tareas existentes.")
                .setView(wrapper(a,input)).setNegativeButton("Cancelar",null)
                .setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{AcademicSchedules.rename(a,p.id,input.getText().toString());
                dialog.dismiss();a.render();
            }catch(IllegalArgumentException|IllegalStateException err){
                input.setError(err.getMessage());
            }
        }));
        dialog.show();
    }
    private static void confirmDelete(MainActivity a,String id){
        AcademicSchedules.Profile p=AcademicSchedules.find(a,id);
        if(p==null)return;
        a.dialogBuilder().setTitle("¿Eliminar el horario «"+p.name+"»?")
                .setMessage("Se eliminarán sus sesiones de clase y avisos semanales. "
                    +"Sus tareas y notas se conservarán en la categoría General. "
                    +"Esta acción no puede deshacerse.")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Eliminar horario",(x,y)->{
                    AcademicSchedules.deleteConfirmed(a,id);
                    a.render();
                }).show();
    }
}
