# Agenda Clara 3.14.0 — Fases restantes del lector de sílabos

## A. Comprensión documental
- Lectura complementaria de cronogramas tabulados con columnas separadas por tabuladores, barras verticales o espacios amplios.
- Fechas leídas exclusivamente de la misma fila. Ante fechas contradictorias se deja pendiente la fecha exacta.
- Exclusión de foros y tareas ordinarias: solo exámenes y productos finales.
- Conservación de página, texto fuente, semana y porcentaje en la revisión.

## B. Integración académica
- Se mantiene la selección explícita de curso y horario, incluso para cursos homónimos.
- Comparación local de importaciones sucesivas del mismo documento y horario.
- Diálogo de diferencias: eventos nuevos, fechas modificadas y eventos ausentes.
- No se borran ni reprograman tareas anteriores automáticamente.

## C. Experiencia y calidad
- El usuario ve evidencia de la página antes de incorporar una evaluación.
- Los eventos sin fecha exacta siguen sin recordatorio inventado.
- Pruebas JVM para tablas, fechas por fila, versiones y filtros.
- Compilación y emulador Android 15 sujetos a validación independiente.

## Limitaciones conocidas
- Las tablas escaneadas con celdas fusionadas y OCR desordenado requieren pruebas con sílabos reales.
- La comparación de versiones advierte de cambios, pero no reemplaza ni elimina tareas automáticamente.
- La prueba de apertura de la app no prueba por sí sola la importación completa y persistencia en SQLite.
- No se considera terminado el recorrido de extremo a extremo hasta superar la importación de PDF real, confirmación del curso, guardado y consulta posterior.

## Mejoras adicionales recomendadas
1. Añadir fixtures de PDF reales anonimizados de varias universidades para medir falsos positivos y negativos.
2. Permitir que el usuario seleccione una fila de evaluación y vea resaltada su posición exacta en el PDF.
3. Agregar una operación transaccional de actualización de tareas existentes con confirmación y reprogramación de avisos.

## Evidencia de QA de esta entrega

- Pruebas JVM del pipeline, fechas por fila, semana, filtros y comparador: exitosas en [run 42119808558](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42119808558).
- APK 3.14.0 compilada, firmada, instalada y abierta en Android 15: [run 42119808566](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42119808566). APK: artifact 13458975146.
- Prueba de importación de un PDF sintético: [run 42121071993](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42121071993). **No superada**: el selector de documentos del emulador no mostró el PDF copiado a Descargas; no se llegó al lector de PDF ni al guardado. Esta incidencia de automatización no demuestra un error del parser, pero impide certificar el flujo completo.
- **Pendiente**: validar importación de un sílabo real, asignación a un curso, persistencia y reimportación con cambios.
