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
