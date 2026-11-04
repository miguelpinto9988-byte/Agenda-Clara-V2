# Fase 23 — Iconos complementarios y mapa de integración

**Alcance:** 28 propuestas de iconografía adicional, priorizadas por necesidad real. Son especificaciones; no se ha creado ningún PNG. El listado está también en CSV para la futura producción.

Prioridades: **P0=11**, **P1=11**, **P2=6**. Las piezas marcadas «revisar reutilización» deben compararse primero con los PNG 3D y los recursos actuales para no generar duplicados.

| Recurso propuesto | Zona objetivo | Símbolo previsto | Prioridad | Decisión |
|---|---|---|---|---|
| ic_activity_course.png | Tarjeta Actividad del curso | Carpeta de curso con lista | P0 | crear |
| ic_activity_today.png | Encabezado de hoy | Calendario pequeño con lista | P0 | crear |
| ic_activity_pending.png | Encabezado pendientes | Reloj con lista sin alarma agresiva | P0 | crear |
| ic_activity_overdue.png | Detalle de vencimientos | Reloj y punto ámbar | P0 | crear |
| ic_state_no_link.png | Curso sin tareas vinculadas | Cuaderno abierto con clip vacío | P0 | crear |
| ic_state_empty_today.png | Nada para hoy | Calendario limpio y destello suave | P0 | crear |
| ic_state_all_done.png | No hay tareas pendientes | Lista completada y estrella | P0 | crear |
| ic_quick_task.png | Tarea rápida (voz) | Micrófono 3D multicolor | P0 | revisar_reutilizacion |
| ic_quick_new_task.png | Nueva tarea | Disquete azul o lista 3D multicolor | P0 | revisar_reutilizacion |
| ic_quick_new_note.png | Nueva nota | Nota amarilla 3D con chincheta | P0 | revisar_reutilizacion |
| ic_action_link_course.png | Vincular tarea al curso | Cadena suave entre libro y lista | P0 | crear |
| ic_state_empty_schedule.png | Horario sin cursos | Libro académico y calendario sin marcas | P1 | crear |
| ic_activity_completed.png | Tarea ya completada | Sello de verificación 3D | P1 | revisar_reutilizacion |
| ic_activity_exam.png | Examen guardado por usuario | Hoja con sello y bolígrafo | P1 | crear |
| ic_activity_homework.png | Tarea académica | Cuaderno con lápiz | P1 | crear |
| ic_activity_reading.png | Lectura asignada | Libro abierto con marca de página | P1 | crear |
| ic_activity_practice.png | Práctica del curso | Herramientas pequeñas y cuaderno | P1 | crear |
| ic_activity_presentation.png | Exposición | Atril con diapositiva sin texto | P1 | crear |
| ic_activity_group.png | Trabajo grupal | Tres avatares con una carpeta | P1 | crear |
| ic_activity_lab.png | Laboratorio | Microscopio y matraz | P1 | crear |
| ic_activity_project.png | Proyecto | Carpeta con diagrama | P1 | crear |
| ic_study_session.png | Sesión de estudio | Libro con cronómetro | P1 | crear |
| ic_activity_workshop.png | Taller | Pincel y herramientas | P2 | crear_si_se_usa |
| ic_activity_debate.png | Debate | Dos burbujas de diálogo | P2 | crear_si_se_usa |
| ic_study_resources.png | Recursos de estudio | Estantería pequeña y carpeta | P2 | revisar_reutilizacion |
| ic_study_progress.png | Progreso académico | Gráfico de avance y diploma | P2 | reutilizar_antes_de_crear |
| ic_class_virtual.png | Clase virtual | Laptop con libro | P2 | crear_si_se_usa |
| ic_calendar_academic.png | Evento académico | Calendario y birrete | P2 | revisar_reutilizacion |

## Orden de integración **futuro** (no implementado)

1. En Inicio, colocar un PNG semántico de asignatura en MiDiaClassCard. En MiDiaActivitiesUi, añadir iconos de cabecera (Curso / Hoy / Pendientes) y una ilustración contextual solo para los estados vacíos; no retirar las casillas que permiten marcar tareas.
2. En MiDiaQuickActions, mantener los accesos **Tarea rápida (voz), Nueva tarea (editor completo), Nueva nota (nota adhesiva con fecha)** ya preparados con los PNG existentes. En una fase posterior, sustituir únicamente el arte por los PNG 3D multicolor propuestos, respetando clics, micrófono, formularios y etiquetas accesibles. Conservar el diseño de tres tarjetas verticales legibles también en teléfonos estrechos; la creación de recordatorios permanece disponible por las funciones originales de tareas.
3. Reutilizar el mismo icono de materia en MiDiaStudyPage y ScheduleActivity para que una asignatura se reconozca en Inicio, Estudio y Horario. Conservar los colores de los cursos elegidos por el usuario.
4. Ampliar solo si aporta información: tipos de actividad (Examen, Lectura, Práctica, Exposición, Trabajo grupal), y estados especiales (Atrasadas, Clase virtual). No deducir automáticamente el tipo a partir de cualquier palabra del título.
5. Revisar Calendar y More antes de añadir arte nuevo: ya existen iconos aprobados específicos, y la barra inferior debe mantenerse uniforme y comprensible.

## Archivos fuente a revisar cuando autorices la fase 26

- MiDiaClassCard.java — icono genérico de graduación reemplazable por icono de asignatura.
- MiDiaActivitiesUi.java — tres paneles, estados vacíos, enlace curso-tarea; checkbox nativo intocable.
- MiDiaQuickActions.java — tres accesos directos con PNG existentes (micrófono, nueva tarea y nueva nota); en fase 26 cambiar solo el arte.
- MiDiaStudyPage.java y ScheduleActivity.java — icono consistente entre Estudio y la lista de cursos.
- MiDiaMorePage.java y pantalla Calendario — sustituciones solo si no hay PNG ya apropiado.
- ApprovedPng.java, CategoryRegistry.java y ScheduleCourseColors.java — revisar compatibilidad, **no alterar equivalencias ni migrar datos por un icono**.

## Criterios de compatibilidad y accesibilidad

Los recursos nuevos serán exclusivamente decorativos: no cambiarán tareas, colores, categorías, clases, notificaciones, widgets, notas o WhatsApp. Los cuatro PNG de métricas de Inicio ya son correctos y no se reemplazarán. La frase motivadora y los 30 fondos panorámicos tampoco forman parte del rediseño de iconos. En 280–320 dp, no colocar ilustraciones de estados vacíos si provocan desbordamiento de texto o duplicación de controles.

**Cierre de fase 23:** zonas faltantes, recursos potenciales, prioridades, casos de reutilización y puntos de integración futura registrados. Las fases 24–27 quedan explícitamente fuera de esta entrega.
