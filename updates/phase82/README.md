# Agenda Clara 3.15.1 — Confirmación obligatoria de cursos desde fotografía

Corrige el lector OCR de horarios **sin tocar el widget de Fotografía fija**.

## Error identificado

El emparejador anterior consultaba principalmente nombres con el mismo inicio, y tras aceptar una coincidencia el flujo podía saltarse otras preguntas para la misma sesión. Además, al agregar fotografías a un horario existente no pedía reconciliar con los cursos ya guardados, y la fusión de lecturas OCR podía descartar variantes tipográficas sin presentarlas.

## Nueva regla

- Una palabra significativa compartida, en cualquier posición (principio, medio o final), activa **¿Son el mismo curso?**, incluso si aparecen numeraciones o grupos diferentes.
- Se ignoran únicamente conectores gramaticales, números sueltos y etiquetas estructurales («de», «la», «y», «grupo», etc.). «Educación», «Historia» e «Investigación» sí son relevantes.
- **Sí:** ambas lecturas reciben un nombre de curso confirmado, y se conservan los días, horas y aulas de cada sesión.
- **No:** los cursos permanecen distintos; si los títulos eran idénticos, se asigna un grupo explícito para impedir una unión involuntaria.
- Una respuesta sobre un par no cancela las preguntas pendientes sobre otras coincidencias del mismo curso.
- Al importar otra foto en un horario existente se consulta también contra los cursos **del mismo perfil**, antes de guardar.
- Las variantes OCR que antes podían omitirse quedan visibles como propuestas complementarias, inicialmente sin seleccionar.
- No se crean cursos, perfiles ni asociaciones de tareas hasta que el usuario finalice la revisión.

## Verificación

`bash updates/phase82/qa_photo_course_confirm.sh` prueba coincidencias con una palabra en medio/final, rechazo y aceptación, varias sesiones, grupos, propuestas OCR, y ausencia de saltos en las decisiones. La compilación de Android y la prueba en emulador se ejecutan mediante GitHub Actions. Las capturas de prueba sintética NO sustituyen la validación de la fotografía real que motivó el reporte.

Versión: **3.15.1, versionCode 68**. Rama: `fix/ocr-confirmar-cursos-3-15-1-20261105`.
