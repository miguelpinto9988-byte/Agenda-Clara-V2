# Agenda Clara 3.15.1 — Confirmación de cursos por fotografía

La comparación de nombres de curso ignoraba una palabra común cuando aparecía en posiciones distintas; además, la fusión OCR podía descartar variantes ortográficas antes de mostrar la revisión.

**Regla:** una palabra académica significativa en común, incluso una sola y aunque esté en cualquier posición, dispara la pregunta «¿Son el mismo curso?». No cuentan por sí solas conectores gramaticales (de, la, en, y). No se modifica ningún curso sin confirmar. La persona puede aceptar, rechazar o volver a corregir. Conservar niveles explícitos I/II y grupos separados manualmente previene deshacer decisiones anteriores.

Las alternativas OCR conservan su estado desmarcado hasta selección expresa. Se preservan sesiones, días, horas, aula, widgets y la fotografía fija.

**Archivos:** apply_photo_course_confirmation.py, Phase82PhotoCourseTests.java, qa_photo_course_confirmation.py.

**QA pendiente:** validar fotografías reales con nombres partidos, textos degradados y cursos con diferencias tipográficas fuertes; una prueba sintética no garantiza la precisión total del reconocimiento visual.