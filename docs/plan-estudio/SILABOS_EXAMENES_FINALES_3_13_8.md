# Agenda Clara 3.13.8 — Sílabos: exámenes, productos finales y semanas

## Objetivo

Limitar la lectura académica a **exámenes de todo tipo y trabajos, proyectos o productos finales**, interpretando fechas en español y conectando los eventos con un curso ya registrado en cualquiera de los horarios existentes.

## Clasificación de eventos

El sistema reconoce, entre otros, exámenes parciales, finales, orales, escritos, prácticos, sustitutorios, extraordinarios, de recuperación, controles de lectura, prácticas calificadas y evaluaciones explícitamente parciales o finales. También identifica productos finales, proyectos finales o integradores, portafolios finales, trabajos finales, sustentaciones finales y entregables finales.

Se excluyen tareas regulares, informes semanales, evaluaciones continuas genéricas, foros y menciones de bibliografía. Un nombre dudoso puede corregirse en la revisión; nunca se crea un evento antes de aprobarlo.

## Fechas complejas y semanas

`SyllabusDateInterpreter` distingue:
- Fecha completa numérica (día/mes/año) o ISO;
- Fechas con meses escritos en español, incluido el año posterior si está fundamentado en el calendario;
- Rangos de días dentro de un mes o que cruzan meses;
- Semanas académicas numéricas y romanas (ej. `SEMANA XII`, `Sem. 8`, `Semanas 13–14`);
- Fecha de inicio de clases o de la primera semana **explícitamente indicada en el documento**, para calcular intervalos de semanas posteriores.

**No se inventa el día del examen.** Con «Semana XII», si el sílabo indica el comienzo del periodo, se calcula la ventana orientativa de esa semana; si no existe inicio, se conserva solo el número. Los eventos por semana o rango sin día exacto se guardan como tareas de **fecha pendiente** (`due=0`) en el curso seleccionado, sin notificación programada. El usuario puede establecer la fecha posteriormente.

## Destino: curso y horario

`SyllabusCourseResolver` inspecciona los encabezados del sílabo (por ejemplo `CURSO:` o `ASIGNATURA:`), compara títulos completos y parciales con el catálogo académico y utiliza el nombre del archivo como evidencia auxiliar. Se consultan **todos los perfiles**, no solamente el horario actualmente seleccionado.

Si «Tendencias educativas» existe en dos horarios, aparecen dos opciones independientes con el nombre de su horario: el usuario debe confirmar cuál corresponde al sílabo. Si no hay coincidencias, se solicita seleccionar un curso. No se crea automáticamente un curso inexistente y **no se guarda nada sin una selección explícita**.

Cada tarea se registra con la categoría del horario seleccionado y un vínculo persistente al UUID de ese horario y curso. Se previenen duplicados por identificador de origen y se preservan las tareas anteriores.

## Lectura de PDF escaneados

Se mantiene el procesamiento local PDFBox/ML Kit. La extracción organiza el texto por posición y aplica OCR también a páginas con poco texto que pueden contener tablas como imagen. Se conservan el encabezado textual y la lectura visual, con límites de archivo, páginas y procesamiento para evitar consumo excesivo de memoria.

El lector de DOC/DOCX conserva compatibilidad; las reglas de clasificación académica se comparten.

## Control de calidad

- `updates/phase78/apply_syllabus.py`: reconstrucción de las fuentes sin tocar el esquema de bases de datos;
- `updates/phase78/test_syllabus.py`: comprobaciones estáticas;
- `updates/phase78/SyllabusAcademicTests.java`: fechas, semanas, exámenes/finales, negativas y coincidencia de un curso con dos horarios;
- `.github/workflows/agenda-clara-syllabus-source.yml`: pruebas Java sin Android;
- `.github/workflows/agenda-clara-syllabus-final.yml`: compila, firma e instala la APK 3.13.8 en Android 15;
- `.github/workflows/agenda-clara-syllabus-pdf-ui.yml`: prueba de importación completa con un PDF sintético, dos perfiles homónimos y verificación SQLite. Esta prueba no utiliza documentos personales.

## Limitaciones conocidas

La extracción de un sílabo puede verse afectada por tablas particularmente complejas, páginas borrosas, cronogramas expresados solo como «evaluación final al concluir el ciclo» o PDFs con demasiadas páginas escaneadas. Una semana académica no determina un día exacto sin otras evidencias; por eso se registran pendientes sin recordatorios.

Rama: `feat/silabos-examenes-finales-3-13-8-20261105`.


## Resultado de verificación y límites

- QA del analizador y fechas: **superado**, incluyendo semanas, fechas complejas y cursos iguales en varios horarios. Ejecución: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42092767475.
- APK 3.13.8: compilación, firma, instalación y apertura en Android 15 **superadas**. Ejecución: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42093209511; artefacto APK: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42093209511/artifacts/13446875917.
- Importación completa de PDF hasta verificar SQLite: aún no certificada. Los primeros ensayos quedaron bloqueados en el selector de documentos del emulador; esto no demuestra que el lector falle en el teléfono. No se declara ese test como aprobado.
- Ningún sílabo personal fue usado ni se modificaron agendas personales.
