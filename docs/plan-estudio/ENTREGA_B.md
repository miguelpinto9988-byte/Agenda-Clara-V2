# Agenda Clara — Entrega B (etapas 5 a 7)

**Estado:** implementada y verificada a nivel de código fuente en la rama `feat/plan-estudio-entrega-b-20261104`. **No se ha compilado una APK** ni se han ejecutado pruebas instrumentadas de Android, por decisión expresa del usuario. El primer compilado de estas entregas se reserva para la Entrega C.

## Qué se integra

### Tareas y cursos

- Las tareas manuales incorporan un selector de los cursos existentes, agrupados por horario.
- Se reconocen menciones parciales de nombres (p. ej. «tendencias» para «Tendencias educativas»), con normalización de mayúsculas y tildes.
- La voz reutiliza el reconocimiento offline existente y muestra **un diálogo obligatorio de confirmación** al encontrar un candidato. Cuando hay varias coincidencias, el usuario elige el curso y el horario.
- Cada tarea confirmada conserva su categoría académica y un vínculo persistente por ID de tarea + UUID de horario + curso en `AcademicTaskLinks`, sin alterar los registros anteriores de la base de tareas.
- Se permite guardar sin asignar curso o cancelar el guardado.

### Sílabos y evaluaciones

- Panel «Exámenes y parciales» de Calendario > Plan de estudio: botones para subir PDF/DOC/DOCX o registrar una evaluación manual.
- Lectura local acotada a 12 MB y 120 páginas, con extracción PDFBox-Android, `DOC` con Apache POI HWPF y `DOCX` por el XML dentro del archivo ZIP.
- PDF escaneados: reconocimiento local ML Kit en hasta 20 páginas sin texto recuperable.
- Extracción conservadora de parciales, exámenes, prácticas y entregas, con fechas expresadas en números o meses completos en español. «Semana 8» sin día explícito queda **pendiente de corrección**, nunca se inventa.
- Lista de revisión con selección de eventos, edición de título, curso, fecha, hora y anticipación. Para Word se indica origen documental sin prometer número físico de página.
- Confirmación final antes de crear tareas. Anticipación predeterminada: 10 días y 12 horas (**15.120 minutos**); alternativa de siete días (**10.080 minutos**).
- Reutiliza `Store`, `Reminders` y `TaskWidget`, evita duplicados exactos con `originKey` y vincula cada tarea a su horario/curso.

## Integración técnica

Aplicar secuencialmente sobre las fuentes verificadas 3.13.2:

```sh
python3 updates/phase71/apply_plan_a.py
python3 updates/phase71/test_plan_a.py
python3 updates/phase72/apply_plan_b.py
python3 updates/phase72/test_plan_b.py
```

Estos comandos son **transformaciones de código fuente**; no ejecutan Gradle ni generan una APK. La nueva actividad `SyllabusImportActivity` queda declarada en AndroidManifest y se agregan dependencias de PDFBox-Android y POI a Gradle para evaluación en fase C.

## QA realizado

La acción «QA de fuentes sin APK» ejecuta pruebas estáticas y pruebas JVM de reconocimiento de cursos y extracción de fechas. Su segundo trabajo toma las **fuentes ya verificadas 3.13.2**, aplica A+B y verifica los anclajes reales. Ambos trabajos han terminado satisfactoriamente en la ejecución:

https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41942095897

## Límites de verificación para la Entrega C

- Android y Gradle **aún no han compilado estas modificaciones**; dependencias de PDF y Word, manifest, comportamiento real, memoria, permisos y OCR requieren pruebas Android.
- El documento puede contener fórmulas, tablas complicadas, imágenes poco legibles, meses abreviados o cronogramas expresados solo por semanas; los eventos inciertos se revisan o se introducen manualmente.
- Comprobar funcionamiento en pantallas pequeñas y que el diálogo de confirmación no produzca una tarea duplicada ante varios toques.
- Verificar alarmas y notificaciones con permisos/restricciones del dispositivo: un aviso cuyo momento programado ya pasó no se puede enviar retroactivamente.
- Probar edición de un sílabo reimportado con fechas cambiadas; la prevención actual de duplicados es exacta por curso, título normalizado y fecha, no un motor avanzado de conciliación de versiones.
- La información académica se procesa localmente en la implementación preparada, sin subir archivos a un servidor.
- Para migración, backups, restauración y borrado de tareas/horarios, completar regresiones instrumentadas antes de publicar.

**Prohibición vigente:** no activar la compilación de APK, la firma o la publicación en las ramas A o B. La Entrega C debe realizar la validación final y pedir autorización antes de distribuir la APK.
