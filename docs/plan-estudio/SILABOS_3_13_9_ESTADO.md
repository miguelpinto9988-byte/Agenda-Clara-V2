# Agenda Clara 3.13.9 — Mejora del apartado Sílabos

## Objetivo aprobado

Mejorar la comprensión documental, la vinculación a cursos y la revisión de exámenes y productos finales, sin introducir fechas inventadas ni guardar eventos sin consentimiento.

## Entrega A: comprensión documental

Se incorpora `SyllabusReviewIntelligence`, una etapa conservadora que procesa los eventos del lector 3.13.8 y descarta menciones de actividades ordinarias, bibliografía, metodologías y descripciones de sistemas de evaluación que no constituyen eventos. Conserva exámenes orales, escritos, prácticos, parciales, finales, sustitutorios, de recuperación, prácticas calificadas y controles de lectura; también proyectos, trabajos, productos, portafolios y sustentaciones finales. Distingue semanas académicas romanas y numéricas y ponderaciones de 0 a 100 %.

No calcula un día a partir de una semana sin evidencia explícita: el vencimiento sigue pendiente.

## Entrega B: integración académica

Se conserva la identificación del curso y horario de la versión 3.13.8: el usuario debe confirmar un curso de uno de los horarios existentes. La revisión filtra los eventos **antes** de que se muestren y antes de guardar. La persistencia y el control de duplicados existentes no se modifican para proteger tareas ya guardadas.

## Entrega C: experiencia y QA

Se mantiene el formulario de revisión, edición de título y fecha, selección de recordatorios y confirmación final. Se han añadido casos JVM de regresión para exámenes, finales, semanas, porcentajes, duplicados y exclusiones. El flujo de importación de PDF real y su guardado en SQLite requiere pruebas adicionales: una prueba de apertura de la app no demuestra ese recorrido.

## Archivos

- `updates/phase79/SyllabusReviewIntelligence.java`
- `updates/phase79/apply_syllabus_review.py`
- `updates/phase79/Phase79ReviewTests.java`
- `.github/workflows/agenda-clara-syllabus-319-source.yml`
- `.github/workflows/agenda-clara-syllabus-319-final.yml`

## Próximas mejoras propuestas, aún no aplicadas

1. Reconstrucción de tablas complejas con encabezados repetidos y celdas combinadas; evitar que una fecha de una fila se atribuya a otra evaluación.
2. Vista de procedencia que permita abrir directamente la página del PDF junto al evento detectado.
3. Comparación de versiones de sílabos con diálogo de cambios antes de actualizar fechas existentes.
4. Validación de extremo a extremo con PDF reales, varios perfiles homónimos y verificación SQLite.

Las mejoras 1–4 no se consideran implementadas por el mero hecho de haber mejorado el clasificador.
