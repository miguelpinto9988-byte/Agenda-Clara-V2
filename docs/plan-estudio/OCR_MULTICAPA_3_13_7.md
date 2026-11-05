# Agenda Clara 3.13.7 — Reconocimiento de horarios por fotografías

## Objetivo

Mejorar la **recuperación de cursos** de fotografías digitales e impresas sin introducir clases no corroboradas, perder detalles de días/horas ni fusionar dos asignaturas con un prefijo común.

## Problemas verificados en 3.13.6

- Si la detección de recuadros obtenía siquiera una clase, `ScheduleOcr` **descartaba completamente** las otras dos interpretaciones (columnas virtuales y lectura de texto). Una imagen parcialmente comprendida podía omitir cursos legibles.
- El detector geométrico reconocía principalmente **rectángulos blancos**, ignorando potencialmente recuadros de colores saturados o pastel.
- Las fotografías con solo **una columna** o **una franja horaria** no podían pasar las condiciones mínimas de los lectores por cuadrícula.
- La fotografía se decodificaba en `RGB_565` y se reducía a 2048 px de máximo; ello puede perjudicar letras pequeñas.
- Al confirmar dos lecturas de curso como idénticas, el software decidía automáticamente cuál de los nombres conservar.
- La revisión de anomalías describía erróneamente algunas sugerencias como líneas que no se habían importado, y las lecturas potenciales no se veían.

## Cambios implementados

### Interpretación multicapa

`ScheduleOcrFusion` combina, **sin convertir en verdad automáticamente**:
1. Tabla con recuadros;
2. Columnas y horarios estimados geométricamente;
3. Texto con día y rango horario explícitos.

La mejor lectura constituye el conjunto inicial. Las propuestas complementarias que aportan una sesión no verificada aparecen **sin marcar**, identificadas como «Lectura adicional» y con advertencias en la revisión. El usuario elige cuáles incluir. Una lectura exacta o prácticamente idéntica a una sesión ya detectada no se duplica. Un conflicto entre dos lecturas para el mismo día/hora se informa y se revisa.

Límite de seguridad: máximo **32 propuestas complementarias** por imagen. Las demás se indican como lecturas no incluidas y pueden agregarse manualmente.

### Recuadros de colores

`ScheduleColorTileDetector` identifica regiones rectangulares azules, verdes o pastel mediante segmentación cromática local y descarta encabezados, íconos minúsculos y fondos demasiado grandes. Complementa al detector anterior para recuadros claros, no lo sustituye. Se limita a un bitmap reducido, sin servicios externos.

### Curso completo y horarios

- Se admiten fotos parciales con **un día o un rango de horas** reconocidos.
- La lectura de imagen preserva más detalle: `ARGB_8888`, máximo de 2560 px en el lado largo con reducción de memoria por muestreo.
- Si se confirma que dos lecturas de curso equivalen, aparece un diálogo para elegir el **nombre completo** de la primera, de la segunda, o escribir uno manualmente. La decisión renombra todas sus sesiones conservando días, horas y datos originales.

### Conservación del flujo

**Subir imagen → revisar cursos y lecturas adicionales → confirmar coincidencias y anomalías → confirmar nombre del horario o escribirlo → crear categoría y guardar.**

No cambia el esquema de las bases de datos ni se asignan materias a un perfil diferente de forma automática.

## QA técnico

- `Phase77FusionTests.java`: tres lectores, coincidencias exactas, cursos recuperados, alternativas sin marcar, nombre canónico y horarios de un día.
- `Phase77ColorTests.java`: recuadros azules y verdes con texto; descarte de títulos y fondos decorativos.
- Regresiones de fases 76 y 77 de cursos truncados y de bloques duplicados.
- `updates/phase77/test_photo_intelligence.py`: verifica la integración real en las fuentes reconstruidas.
- GitHub Actions reconstruye las fuentes verificadas 3.13.6, aplica la fase 77 y ejecuta tests JVM antes de compilar la APK 3.13.7 y verificar la apertura en Android 15.

## Limitaciones

Sin un ejemplo concreto de la fotografía que falló, no se puede garantizar el OCR de cada letra, tabla inclinada, recorte, caligrafía o contraste. Las propuestas complementarias están desmarcadas deliberadamente para evitar que el sistema fabrique horarios. Una prueba de instalación o apertura **no sustituye** una importación completa con fotos reales y revisión humana.

Para una futura optimización basada en datos reales: añadir pruebas con fotografías anonimizadas de distintos formatos y comparar la cantidad de materias, sesiones y advertencias contra una transcripción de referencia.

Rama: `feat/ocr-fusion-cursos-3-13-7-20261105`.


## Resultado final verificado: 5 de noviembre de 2026

- **Código y JVM:** todas las pruebas de las fases 76 y 77 correctas; ejecución https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42016358575.
- **APK 3.13.7, compilación, firma y navegación Android 15:** correctas; ejecución https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42016503685, artefacto APK: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42016503685/artifacts/13408609660.
- **Prueba de fotografía sintética a través de la interfaz Android 15:** correcta; ejecución https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42018452189. El usuario automatizado abrió «Calendario > Plan de estudio > Nuevo horario > Subir imagen», seleccionó la foto desde el sistema y aguardó al OCR local.
- El OCR local reconstruyó **seis bloques**, incluyendo «Tendencias educativas», «Tendencias» e «Historia de la educación», y llegó a la revisión de cursos, **antes de solicitar el nombre del horario**.
- Al pulsar «Corroborar cursos y continuar», apareció el diálogo real «¿Son el mismo curso?» para **«Tendencias educativas» (lunes 08:00–09:00) y «Tendencias» (martes 08:00–09:00)**, con las decisiones «No · separados» y «Sí · mismo curso» visibles.
- Capturas del emulador: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42018452189/artifacts/13410038639.
- **Alcance de esta prueba:** se verificó la lectura de una foto sintética, la revisión visual y el diálogo de coincidencia; **no** se verificó la aceptación y escritura final de las seis clases ni se usaron fotografías reales del usuario. No afirmar que todos los tipos de horario funcionarán.

Siguiente mejora opcional: evitar mostrar «¿Son el mismo curso?» dos veces dentro del mismo cuadro (título de la ventana y subtítulo interno); es un detalle de presentación, no una falla de reconocimiento.
