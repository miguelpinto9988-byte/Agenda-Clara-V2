#!/usr/bin/env python3
"""Add action-specific PNG bindings after creating 500 mobile resources.
Runs after phase53/build_500.py --mode mobile. Preserves data and navigation.
"""
from pathlib import Path
import json, re
BASE=Path('AgendaClara/app/src/main')
JAVA=BASE/'java/pe/agendaclara/app'
ASSETS=BASE/'assets'
RES=BASE/'res/drawable-nodpi'
catalog=json.loads((ASSETS/'adaptive_icon_catalog.json').read_text(encoding='utf8'))
assert catalog['count']==500
assert len(list(RES.glob('ic_adapt_*.png')))==500
src=JAVA/'UiDesign.java'
text=src.read_text(encoding='utf8')
needle='public static void actionIcon(Button b,String caption) {'
assert text.count(needle)==1,'Action-button hook changed'
text=text.replace(needle,needle+'\n        if(FeatureIconLibrary.apply(b,caption))return;')
src.write_text(text,encoding='utf8')

# Mappings intentionally cover existing on-screen actions, not speculative features.
resolver=r'''package pe.agendaclara.app;

import android.graphics.drawable.Drawable;
import android.widget.Button;

/** Semantic PNG routing for existing interface actions. Zero network requests. */
public final class FeatureIconLibrary {
    private FeatureIconLibrary(){}
    private static final String[][] ACTIONS={
        {"ui_my_guide","mi dia|resumen de hoy|mi jornada|mi guia"},
        {"ui_course_add","mis cursos|nuevo curso|agregar curso|anadir curso|crear curso"},
        {"ui_course_edit","editar curso|modificar curso"},
        {"ui_exam_schedule","calendario de examenes|proximos examenes|fechas de examen"},
        {"ui_exam_results","resultados de examen|notas de examenes|calificaciones"},
        {"ui_study_progress","progreso de estudio|avance diario|progreso del dia"},
        {"ui_class_today","clases de hoy|mis clases hoy"},
        {"ui_class_week","horario semanal|clases de la semana"},
        {"ui_class_schedule","horario de clases|crear editar horario|ver horario|mis horarios|horarios"},
        {"ui_exam_add","anadir examen|agregar examen|nuevo examen"},
        {"ui_exam_review","examenes|mis examenes|evaluaciones|revisar examen"},
        {"ui_pdf_import","analizar silabo|importar pdf|documento pdf|importar silabo"},
        {"ui_new_task","nueva tarea|agregar tarea|crear tarea|anadir tarea"},
        {"ui_edit_task","editar tarea|modificar tarea"},
        {"ui_complete_task","completar tarea|terminar tarea"},
        {"ui_delete_task","eliminar tarea|borrar tarea"},
        {"ui_task_archive","papelera de tareas|archivar tareas"},
        {"ui_task_filter","filtrar tareas|filtro de tareas"},
        {"ui_task_search","buscar tareas"},
        {"ui_new_note","nueva nota|crear nota|anadir nota"},
        {"ui_notes_gallery","mis notas adhesivas|ver notas"},
        {"ui_calendar_today","ir a hoy|ver calendario hoy"},
        {"ui_calendar_add","nuevo evento|anadir evento"},
        {"ui_calendar_schedule","calendario y actividades|ver calendario"},
        {"ui_calendar_sync","google calendar|sincronizar calendario"},
        {"ui_study_plan","plan de estudio|mi guia"},
        {"ui_voice_mic","microfono|tarea por voz|dictar"},
        {"ui_voice_record","grabar voz|grabar audio"},
        {"ui_voice_stop","detener grabacion"},
        {"ui_notify_settings","activar o revisar notificaciones|configurar notificaciones"},
        {"ui_notify_test","probar una notificacion"},
        {"ui_notify_snooze","posponer notificacion"},
        {"ui_whatsapp_link","vincular whatsapp"},
        {"ui_whatsapp_connect","reanudar conexion|conectar whatsapp"},
        {"ui_whatsapp_disconnect","desvincular"},
        {"ui_whatsapp_history","historial sincronizado|historial ultimos"},
        {"ui_whatsapp_import","importar conversacion"},
        {"ui_whatsapp_message","abrir whatsapp|ver mensaje original"},
        {"ui_whatsapp_sync","actualizar grupos|actualizar diagnostico"},
        {"ui_whatsapp_filter","revisar propuestas"},
        {"ui_widget_tasks","widget de tareas"},
        {"ui_widget_notes","widget de notas"},
        {"ui_widget_voice","widget de voz"},
        {"ui_widget_add","anadir widget"},
        {"ui_backup_create","exportar copia cifrada"},
        {"ui_backup_restore","restaurar copia cifrada"},
        {"ui_data_export","exportar mis tareas|exportar tareas"},
        {"ui_data_import","restaurar tareas|importar tareas"},
        {"ui_data_cleanup","borrar mensajes|limpieza de datos"},
        {"ui_privacy_policy","licencias y codigo fuente|politica de privacidad"},
        {"ui_app_settings","preferencias visuales|configuracion|ajustes"},
        {"ui_action_save","guardar"},
        {"ui_action_cancel","cancelar|volver"},
        {"ui_action_retry","reintentar|solicitar otro codigo"},
        {"ui_action_share","compartir"},
        {"ui_action_copy","copiar"},
        {"ui_action_edit","editar"},
        {"ui_action_delete","borrar|eliminar"},
        {"ui_action_add","agregar|anadir|nuevo"},
        {"ui_action_search","buscar"},
        {"ui_action_done","completar|finalizar"},
    };
    public static boolean apply(Button button,String caption){
        if(caption==null||caption.trim().length()<4||caption.trim().equals("＋"))return false;
        String normalized=AdaptiveIconLibrary.normalize(caption);
        if(normalized.isEmpty())return false;
        String key=null;
        outer:for(String[] rule:ACTIONS)for(String query:rule[1].split("\\|")){
            if(normalized.contains(query)){key=rule[0];break outer;}
        }
        if(key==null)return false;
        int id=button.getResources().getIdentifier("ic_adapt_"+key,"drawable",button.getContext().getPackageName());
        if(id==0)return false;
        Drawable icon=button.getContext().getDrawable(id);
        if(icon==null)return false;
        int px=UiDesign.dp(button.getContext(),22);
        icon.setBounds(0,0,px,px);
        button.setCompoundDrawables(icon,null,null,null);
        button.setCompoundDrawablePadding(UiDesign.dp(button.getContext(),8));
        // Text labels remain intact for accessibility and screen readers.
        return true;
    }
}
'''
# The regex in Java must be \\|, not a literal pipe alternation.
resolver=resolver.replace('split("\\\\|")','split("\\\\|")')
(JAVA/'FeatureIconLibrary.java').write_text(resolver,encoding='utf8')
home=JAVA/'HomeDashboard.java'
text=home.read_text(encoding='utf8')
changes={
 'String[] concepts={"educacion","tarea","examen","notas"};':
 'String[] concepts={"ui_class_schedule","ui_new_task","ui_exam_review","ui_new_note"};',
 'AdaptiveIconLibrary.icon(a,"planificacion",37)':
 'AdaptiveIconLibrary.icon(a,"ui_study_plan",37)',
 'AdaptiveIconLibrary.icon(a,"horario",42)':
 'AdaptiveIconLibrary.icon(a,"ui_class_schedule",42)',
 'AdaptiveIconLibrary.icon(a,"examen",42)':
 'AdaptiveIconLibrary.icon(a,"ui_exam_review",42)'
}
for old,new in changes.items():
    assert text.count(old)==1,(old,text.count(old))
    text=text.replace(old,new)
home.write_text(text,encoding='utf8')
print('PASS 500-icon UI binding: panels Mi dia, Examenes, Horarios, Cursos; actions and dashboard')
