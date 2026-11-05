# Agenda Clara — Entrega A (fases 1–4)

**Estado del código fuente:** implementado en rama aislada `feat/plan-estudio-entrega-a-20261104`.

**Regla de publicación:** no generar, firmar, publicar ni distribuir una nueva APK de las entregas A o B. La compilación final queda reservada para la entrega C, tras autorización del usuario. La rama se excluyó de los disparadores de compilación de GitHub Actions.

## Alcance integrado

1. Navegación: dos pestañas «Calendario» y «Plan de estudio» dentro del destino Calendario existente. Se conservan las cinco pestañas inferiores.
2. Interfaz: eliminación del botón cuadrado grande «+» en el encabezado; los flujos de creación de tareas y notas conservan rutas alternativas.
3. Horarios: registro persistente de hasta diez perfiles con UUID, nombre editable, selección de perfil y cursos independientes. Confirmación emergente de nombres y avisos de eliminación.
4. Datos: migración no destructiva de SQLite de versión 1 a 2 mediante `schedule_id`, con las clases anteriores conservadas y asignación a un perfil heredado.
5. Cursos y categorías: cada horario crea una categoría académica mediante `CategoryRegistry`; se protegen los nombres asociados frente a cambios o eliminaciones desde el editor general.
6. Entrada manual: creación de cursos y sesiones dentro del perfil activo, con aislamiento de clases, colores y detección de conflictos.
7. Importación fotográfica: reutilización del OCR existente, sugerencia conservadora del nombre del horario y ventana emergente obligatoria para confirmar o corregir antes de guardar. La sincronización de cursos se efectúa tras la importación.
8. Copias de seguridad: formato de horarios v2 con perfiles y cursos; admite restaurar copias v1.
9. Pruebas estáticas: `updates/phase71/test_plan_a.py` verifica estructura, migración, OCR, categorías, pestañas y conservación de rutas existentes.

## Archivos clave

- `updates/phase71/AcademicSchedules.java`
- `updates/phase71/CalendarStudyPanel.java`
- `updates/phase71/CalendarStudyTabs.java`
- `updates/phase71/ScheduleDatabase.java`
- `updates/phase71/ScheduleEntry.java`
- `updates/phase71/ScheduleBackup.java`
- `updates/phase71/ScheduleTitleParser.java`
- `updates/phase71/patch_android_ui.py`
- `updates/phase71/apply_plan_a.py`
- `updates/phase71/test_plan_a.py`

## Límite de la verificación

El código de la Entrega A está preparado en GitHub. No se declara una APK de Entrega A validada o entregada. La verificación final en dispositivo y las pruebas instrumentadas de regresión se realizarán en la Entrega C, junto con la compilación. No confundir esta situación con una instalación en el teléfono.

## Continuación — Entrega B

Vincular tareas manuales y por voz con perfiles/cursos, confirmar coincidencias parciales mediante diálogos, importar PDF/DOC/DOCX y revisar exámenes y entregas antes de crear tareas, con recordatorios configurables. Preservar las estructuras de la Entrega A y mantener la prohibición de compilar APK hasta la Entrega C.
