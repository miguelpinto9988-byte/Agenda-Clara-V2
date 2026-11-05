# Agenda Clara 3.13.9 — Lectura de sílabos: fases A, B y C

## Base y seguridad de datos

Rama: `feat/silabos-integrales-3-13-9-20261105`, derivada de `feat/silabos-examenes-finales-3-13-8-20261105`. Versión Android `3.13.9`, `versionCode 65`. Conserva `applicationId`, firma de desarrollo y bases de datos; no se eliminan ni migran tablas existentes.

Toda la interpretación se realiza localmente. Un PDF puede contener datos erróneos, ambiguos o sin fecha: ninguna semana por sí sola programa recordatorios ni se crea una tarea sin confirmar un curso y su horario.

## Fase A: comprensión de documentos

- `SyllabusAssessmentExtractor` examina la evaluación y sus celdas de contexto: fecha, semana académica y ponderación pueden aparecer en líneas anteriores o posteriores.
- Evita heredar la fecha o porcentaje perteneciente a otro examen; las cabeceras de la próxima semana no se asignan al examen anterior.
- Detecta rangos de fechas entre meses, por ejemplo *del 28 de noviembre al 3 de diciembre de 2026*, además de semanas en numeración romana.
- Un día de la semana con semestre anclado puede proporcionar una **fecha sugerida**, pero el usuario debe pulsar **Confirmar fecha sugerida** para programarla.
- Sólo se ofrecen exámenes de diversos tipos y trabajos/proyectos/productos finales (se conserva el filtro 3.13.8). Las menciones generales sobre ponderaciones y sin programación se descartan cuando es posible; otras apariciones sin fecha o semana se dejan **sin marcar**.
- Conserva separadores de celdas y filas DOCX (XML `w:tc`/`w:tr`), para mejorar la asociación de columnas.
- En PDF con indicios de cuadrícula escaneada aunque exista un encabezado digital corto, ejecuta OCR local en páginas admisibles; mantiene límites de archivo y páginas.

## Fase B: curso, horario y reimportación

- `SyllabusCourseResolver` compara el encabezado del sílabo y el nombre de archivo con los cursos de **todos** los horarios. El destino siempre requiere confirmación en un diálogo con nombres de horarios visibles.
- `SyllabusReimportPlanner` compara sólo evaluaciones asociadas al **UUID de horario y curso elegido**. Distingue `NEW`, `UNCHANGED`, `CHANGED` y `AMBIGUOUS`.
- Para cambios de fecha o eventos similares, el usuario puede elegir **Actualizar evaluación existente** o **Registrar como evento distinto**. Cuando hay más de un registro posible, debe escogerlo expresamente.
- Cambiar el curso de destino invalida los vínculos de actualización previamente seleccionados; evita sobrescribir tareas de otro horario.
- Las actualizaciones conservan el ID y la identidad de la tarea original, así como sus subtareas; se reprograman las notificaciones asociadas, sin duplicar tareas idénticas.
- Eventos sin fecha exacta se pueden guardar en su curso con `due=0`, sin alarma.

## Fase C: revisión, seguimiento y recordatorios

- La pantalla muestra nombre, tipo, página de origen, descripción del período, contexto de la fecha, porcentaje detectado, fecha sugerida y estado de reimportación.
- Fecha e inicio de semana inferidos se diferencian de una fecha confirmada.
- Se ofrecen recordatorios individuales de **10 días y 12 horas**, **7 días** o la configuración general, únicamente para evaluaciones con fecha exacta confirmada.
- Se incorpora un panel **Mis evaluaciones académicas**, que muestra hasta 15 exámenes/entregables agrupados visualmente por su nombre de curso, con estados **Fecha pendiente**, **Programado** y **Completado**. Las fechas pendientes se pueden fijar posteriormente mediante diálogo y confirmación.
- Se exige confirmación final con cantidad de tareas nuevas, actualizadas y pendientes de fecha.

## Verificación

- `updates/phase79/Phase79SyllabusTests.java`: tablas con celdas de contexto, semanas XII–XIII, rango noviembre–diciembre, ponderación, fecha sugerida y clasificación de reimportaciones.
- `updates/phase79/test_syllabus_139.py`: comprobaciones de integración real de fuentes.
- `.github/workflows/agenda-clara-syllabus-139-source.yml`: QA de fuentes y JVM.
- `.github/workflows/agenda-clara-syllabus-139-final.yml`: compilación APK firmada y verificación Android 15.
- `.github/workflows/agenda-clara-syllabus-139-pdf-qa.yml`: PDF sintético real a través del selector de documentos y verificación de la base SQLite (requiere ejecución satisfactoria).

## Límites conocidos

- El lenguaje natural de cualquier sílabo puede expresar evaluaciones de forma indirecta o en tablas con encabezados incompletos. Las propuestas deben revisarse.
- El calendario de semanas se ancla sólo cuando el documento da una fecha de inicio fiable. Las vacaciones o interrupciones que cambien la **numeración** de semanas no se trasladan automáticamente sin evidencia exacta.
- Las ponderaciones son informativas; no constituyen calificaciones.
- Actualizaciones sobre tareas antiguas editadas manualmente deben aprobarse; la coincidencia de título no garantiza identidad.
- No se han enviado documentos a servicios externos. Los PDF escaneados de poca calidad pueden necesitar revisión manual.
