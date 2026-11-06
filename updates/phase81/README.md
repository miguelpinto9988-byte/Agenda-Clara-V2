# Agenda Clara — Widgets 3.15.0, estructura de implementación

## Diseño aprobado

1. **Mi día académico**: próxima clase + tareas del mismo curso, filtradas por horario. Una tarea sin curso no se atribuye a una clase.
2. **Horario semanal y evaluaciones**: clases por día y evaluaciones parciales/finales por curso; las fechas desconocidas se muestran como pendientes.
3. **Mis tareas**: conservar las funciones existentes y evolucionar filtros por curso/horario, progreso y completado seguro.
4. **Notas adhesivas**: reemplazar visualmente el papel antiguo por un tablero de tarjetas pastel organizadas. Mantener creación, edición, almacenamiento y accesos existentes.
5. **Fotografía**: no tocar el código, configuración ni comportamiento. La imagen seleccionada sigue fija hasta que el usuario la cambie.
6. **Accesos rápidos**: excluidos expresamente del alcance.

## Archivos preparados

- `AcademicWidgetModels.java`: modelos de clases, evaluaciones, tareas y selección por perfil/curso. Sin inventar fechas.
- `AcademicWidgetModelsTests.java`: regresión de aislamiento entre perfiles y fechas pendientes.
- `WidgetAppearance.java`: preferencias independientes por instancia de widget.
- `widget_academic_day.xml`: diseño de Mi día académico.
- `widget_academic_week.xml`: diseño de Horario semanal y evaluaciones.
- `widget_notes_board.xml`, `widget_notes_board_row.xml`: tablero de notas.
- `widget_academic_background.xml`, `widget_note_card_yellow.xml`: recursos visuales.
- `qa_widget_models.sh`: pruebas JVM y análisis sintáctico XML.

## Pendientes técnicos antes de una APK funcional

1. Mapear los modelos con los almacenes reales `AcademicSchedules`, `AcademicTaskLinks`, `Store` y el origen de evaluaciones del sílabo.
2. Crear los `AppWidgetProvider` y `RemoteViews` de los dos widgets académicos y el adaptador del tablero de notas; definir configuración de horario por instancia.
3. Integrar layouts y drawables en `AgendaClara/app/src/main/res`, declarar receptores y metadatos en AndroidManifest.
4. Implementar `PendingIntent` seguros para abrir curso/tarea/nota y refresco tras cambios.
5. Mantener la experiencia anterior hasta validar que los nuevos widgets no provocan regresiones.
6. Validar dimensiones pequeñas, medianas y grandes, modo claro/oscuro y accesibilidad.
7. Compilar APK firmada y probar widgets en Android 15 y en un launcher real.

**Estado:** estructura inicial y pruebas de modelos; no declarar widgets integrados o listos para instalar. No se modificó Fotografía.
