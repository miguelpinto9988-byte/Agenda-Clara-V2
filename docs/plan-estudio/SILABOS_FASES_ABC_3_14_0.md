# Agenda Clara 3.14.0 — Sílabos, fases A/B/C

## Entrega implementada

**Fase A. Lectura documental.** Se utilizan las reglas de fechas académicas de 3.13.8, la detección conservadora de exámenes y productos finales de 3.13.9 y una reconstrucción adicional de tablas (`SyllabusTableNormalizer`). Para PDFs con texto nativo, `SyllabusColumnTextStripper` mantiene separaciones significativas por posición horizontal; en DOCX se preserva la separación de celdas. Cuando una tabla presenta cabecera identificable, se pueden recomponer filas incluso si las celdas aparecen en líneas sucesivas. Las tablas sin indicios fiables no se reconstruyen de forma especulativa.

**Fase B. Integración académica.** Se mantiene la vinculación al curso y perfil de horario elegido explícitamente. `SyllabusImportPolicy` genera identificadores estables que excluyen fechas mutables; al reimportar un sílabo, la revisión muestra registros existentes y cambios. Un registro existente solo se actualiza si el usuario marca «Actualizar esta evaluación». Los registros anteriores de 3.13.8/3.13.9 se comparan solo cuando existe una coincidencia única en el mismo perfil/curso. Las coincidencias ambiguas requieren revisión: no se sobrescriben automáticamente.

**Fase C. Revisión y panel.** Los eventos se muestran con fuente documental y página, calendario académico, ponderación si está disponible y estado de fecha. Cada evaluación fechada puede usar el aviso general o uno individual (10 días y 12 horas, 7 días, 3 días o 1 día). La pantalla «Mis evaluaciones por curso» consulta tareas realmente vinculadas al perfil elegido, muestra «Fecha pendiente», «Programado» o «Completado», y permite confirmar fechas con un diálogo antes de programar recordatorios.

## Salvaguardas

- No se inventa el día a partir de una semana académica.
- No hay guardado sin curso y horario confirmados.
- No hay actualizaciones automáticas por reimportar un documento.
- Los eventos sin fecha no generan alarmas.
- No se cambia el esquema de `agenda_clara.db`, `academic_task_links.db` ni las sesiones de los horarios.
- Se ejecuta preflight antes de modificar las fuentes, y se revisa el versionCode (66 / 3.14.0).
- La prueba del emulador usa PDF generado con datos ficticios, dos perfiles que contienen el mismo curso y comprobación de SQLite.

## Código y pruebas

- `updates/phase80/SyllabusTableNormalizer.java`
- `updates/phase80/SyllabusColumnTextStripper.java`
- `updates/phase80/SyllabusImportPolicy.java`
- `updates/phase80/apply_syllabus_complete.py`
- `updates/phase80/Phase80EndToEndTests.java`
- `updates/phase80/qa_syllabus_314_pdf.py`
- `.github/workflows/agenda-clara-syllabus-314-source.yml`
- `.github/workflows/agenda-clara-syllabus-314-final.yml`

## Límites importantes

Las celdas combinadas, PDFs muy deformados o escaneos con OCR ilegible pueden requerir corrección manual; la reconstrucción deliberadamente no asigna fechas cuando carece de evidencia estructural. La vinculación retroactiva de tareas con identidades de versiones antiguas solo se hace si es inequívoca. Los avisos requieren que Android tenga permisos adecuados.

La compilación y las pruebas de código son condiciones necesarias, pero la validación final de importación con documentos reales de distintos centros educativos y el flujo de cambios al reimportar deberían seguir probándose en dispositivos reales. No confundir una prueba con un PDF sintético con cobertura universal de formatos.
