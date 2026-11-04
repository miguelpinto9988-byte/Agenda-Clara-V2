# Fase 20 — Auditoría de iconografía

**Base verificada:** Agenda Clara 3.13.1, rama feat/mi-dia-header-15-19-validated-apk (commit 6fa894bbe86c8fa4135e4468b784fb4d5c00a24c). Análisis de los recursos PNG y componentes Java existentes. Este documento no modifica la app.

## Inventario real

Se inspeccionaron **98 PNG** en AgendaClara/app/src/main/res/drawable-nodpi. Desglose:

| Familia | Archivos | Tamaño observado | Decisión |
|---|---:|---|---|
| Paisajes bg_mi_dia_01…30 | 30 | 1920×864 px | Conservar, no son íconos |
| Fondos sticky_* de notas | 6 | 800×460 px | Conservar |
| Indicadores ic_midia_* | 4 | 256×256 px | Conservar como referencia 3D |
| Categorías ic_ref_cat_* | 12 | 96×96 px, salvo Estudio 72×72 | Conservar preferencias del usuario |
| Iconos y arte de widgets ic_ref_widget* | 11 | 72, 256 y 900×110 px | Reutilizar |
| Otros ic_ref_* y botón superior | 35 | 72, 144, 196 y 256 px | Reutilizar según significado |
| **Total** | **98** | | **62 piezas de iconografía / decoración, además de paisajes y notas** |

Los íconos son transparentes (RGBA o paleta con alfa). Los paisajes son opacos. No hay una colección de iconos individuales por asignatura del tipo ic_subject_*. La iconografía actual combina PNG y símbolos lineales dibujados por código.

## Ubicaciones verificadas

| Componente fuente | Estado actual | Acción futura | Prioridad |
|---|---|---|---|
| MiDiaClassCard.java | Graduación genérica con UiDesign.OutlineIcon, 31 dp | Mostrar símbolo específico del curso y respaldo genérico | **P0** |
| ScheduleActivity.java | Listados de cursos con texto y glifos generales | Visualizar la misma materia sin modificar el horario | **P0** |
| MiDiaActivitiesUi.java | Encabezados y estados vacíos sin ilustración | Íconos de actividad vinculada, del día, pendiente y sin tareas | **P0** |
| MiDiaQuickActions.java | Check, notes y bell lineales, 26 dp | Íconos PNG consistentes para Tarea, Nota y Recordatorio | **P0** |
| MiDiaStudyPage.java | Graduación genérica, ~30 dp | Reforzar materia y estudio donde realmente se diferencian | P1 |
| MiDiaMorePage.java | Glifos lineales, ~30 dp | Evaluar sustituciones selectivas; evitar sobrecarga | P2 |
| MiDiaDashboard.java | Los 4 ic_midia_* ya ilustran métricas | **No cambiar** | Mantener |
| MainActivity.java / ApprovedPng.java / CategoryRegistry.java | Categorías y menú ya tienen PNG configurables | **No reemplazar indiscriminadamente** | Mantener |
| Calendario y widgets | Recursos existentes específicos | Reusar antes de pedir duplicados | P2 |

**Detalle de implementación:** ApprovedPng.java resuelve muchos recursos por nombre dinámico usando getIdentifier; buscar solamente referencias R.drawable no encuentra todos los usos. Los colores y sesiones de ScheduleEntry no deben alterarse para seleccionar una ilustración. ScheduleCourseColors.identity normaliza nombres para vincular datos; no debe convertirse en una base de equivalencias visuales imprecisas.

## Diagnóstico y riesgos

- **Curso dinámico:** se pueden escribir asignaturas libres, con abreviaturas y sufijos, por ejemplo «TENDENCIAS EDUCATIVAS (E)». Una lista cerrada no cubre todos los títulos. Usar taxonomía + icono genérico.
- **Semántica:** examen, práctica y exposición son tipos de actividad y no deben sustituir automáticamente al icono del curso.
- **Compatibilidad:** conservar los 30 fondos diarios, las 50 frases, el menú de cinco pestañas, las tareas, las notas, los horarios, los colores personalizados y los recordatorios.
- **Accesibilidad:** las casillas de tareas, etiquetas y descripciones de los botones siguen siendo los elementos interactivos. El PNG solo ilustra.

**Resultado:** mapa de brechas y priorización completados. No se han creado PNG ni modificado fuentes Android.
