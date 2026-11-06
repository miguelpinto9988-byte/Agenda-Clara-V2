# Agenda Clara — Android nativo

**Versión actual de la aplicación:** 3.15.6 (`versionCode 73`). El historial
de migraciones se mantiene hasta `updates/phase87`.

## Widgets disponibles y corrección de carga

La app declara cinco proveedores Android en `AndroidManifest.xml`:
`TaskWidget` (tareas), `StickyNotesWidget` (notas adhesivas),
`AcademicDayWidget` (Mi día académico), `AcademicWeekWidget` (horario y
evaluaciones) y `PhotoWidget` (fotografía fija).

En 3.15.2 los widgets académicos tenían separadores `<View />` en dos
diseños XML. Esa clase genérica **no está autorizada por el inflador Android
`RemoteViews`** y puede hacer que el lanzador muestre «No se puede cargar el
widget». La fase 84 sustituye ambos separadores por `<FrameLayout />` con
idénticas dimensiones y colores, preservando el diseño y los datos de usuario.

El flujo 3.15.3 verifica todas las clases XML, los cinco receptores del
manifiesto y la inflación de **13 diseños XML** usando `RemoteViews.apply`
en Android 15 (no solo la presencia de los proveedores). La verificación completa en **main**
[42173553585](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42173553585)
terminó correctamente: compilación, firma, instalación Android 15 y **13/13 diseños cargados**.
Los artefactos de esa ejecución incluyen la APK 3.15.3 y sus fuentes.
La actividad auxiliar de comprobación existe solo en el código `debug`.

## Compilación y pruebas de main

- Flujo principal: [Agenda Clara 3.15.6 — Widgets, OCR fotográfico y sílabos](.github/workflows/agenda-clara-ocr-photo-3151.yml).
- Los cambios de `updates/phase82/**`, `updates/phase83/**`, `updates/phase84/**`, `updates/phase85/**`, `updates/phase86/**`, `updates/phase87/**`
  y del propio flujo activan la compilación Android 3.15.6 en `main`.
- Se reconstruyen las fuentes, se prueban los datos académicos y el OCR,
  se usa la firma de desarrollo guardada en el secreto
  `SIGNING_JKS_BASE64`, y se valida la APK en emulador Android 15.
- El flujo antiguo [3.13.3](.github/workflows/agenda-clara-ci.yml)
  permanece disponible solo para ejecución manual.

El proyecto Android completo no está versionado como carpeta `AgendaClara/`:
las fuentes se reconstruyen a partir del ZIP base y las migraciones, y se
entregan como artefactos del flujo automatizado.

**Limitación de reproducibilidad:** el flujo toma fuentes 3.15.0 del
artefacto de GitHub Actions `42145182419`, con retención limitada. Antes
de caducar, sustituir esta dependencia por una fuente base permanente o
reconstrucción totalmente versionada.


## Lector contextual de sílabos (3.15.4)

La fase 85 complementa el lector de PDF/Word con correlación **conservadora y
trazable** de exámenes parciales numerados:

- Detecta primero, segundo, tercer parcial y ordinales hasta el décimo,
  incluidos algunos formatos numéricos y romanos.
- Relaciona referencias del mismo ordinal, aunque estén en páginas distintas:
  «Primer examen parcial» + «Primer examen: tema 5» + «Primer examen parcial,
  11/05/2026» se convierten en **una sola evaluación**, con tema y fecha
  demostrables en el documento.
- Una mención aislada «Examen, tema 14» o «Examen parcial» sin ordinal **no
  crea un examen parcial numerado**. Se conservan tipos independientes claros,
  como examen oral/final y productos finales.
- Las fechas exactas requieren día y mes explícitos, en la misma referencia
  o en una celda inmediatamente vinculada; una semana académica por sí sola
  nunca crea un día exacto.
- Si las fuentes del mismo parcial presentan fechas o temas incompatibles,
  queda marcado para revisión; nunca se elige una fecha por suposición.
- La lista resultante ordena primero, segundo y tercer examen por ordinal,
  no por el orden desordenado de las menciones ni por fechas supuestas.

Las pruebas combinan regresiones existentes (fases 79/80) con nuevos casos
sintéticos de la fase 85. La validación **directamente en `main`**
[42202717940](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42202717940)
terminó correctamente: pruebas de sílabos, compilación y firma APK 3.15.4,
instalación Android 15 y comprobación de widgets. Los artefactos de APK y
fuentes se publicaron en esa ejecución. **No se ha probado todavía la precisión
con un sílabo real proporcionado por el usuario**; los casos con OCR defectuoso
se deben revisar antes del guardado.


## Análisis de fotografías de horarios (3.15.5)

La fase 86 corrige un incidente en que varias sesiones de **Tendencias
educativas** aparecían divididas en grupos diferentes por descriptores OCR
duplicados y por un nivel `I` potencialmente confundido. El comparador anterior
también ofrecía unir **Tutoría educativa** e **Investigación educativa** al
compartir la palabra genérica «educativa».

El nuevo proceso aplica una limpieza muy limitada de palabras repetidas
después de códigos de curso, descarta coincidencias basadas solo en conectores
y adjetivos genéricos, compara los conceptos específicos y respeta las
distinciones de niveles `I`/`II` y grupos explícitos. Los casos ambiguos
siguen requiriendo confirmación humana: **no existe una fusión automática de
materias diferentes por similitud superficial**.

La pantalla de revisión añade una vista previa temporal de la fotografía con
contornos geométricos aproximados, una auditoría final de cursos y sesiones,
y la acción **«Revisar nombres duplicados del OCR»** dentro de «Mis cursos».
Esta última permite corregir grupos previamente guardados, únicamente por
aprobación explícita y mediante una transacción de SQLite que conserva sus
sesiones, días, horas y aulas. Actualizar la APK **no cambia retroactivamente**
los datos ya guardados.

Las reglas están documentadas en
[la fase 86](updates/phase86/README.md). El detector usa ML Kit OCR local,
geometría y reglas de similitud; **no es un modelo general de visión artificial**
y la captura de la pantalla de cursos por sí sola no permite validar el
reconocimiento de una fotografía original.

La verificación [3.15.5 en `main`, ejecución 42207474190](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42207474190)
concluyó satisfactoriamente: regresiones de nombres, limpieza OCR,
protección de niveles, auditoría de sesiones, compilación/firma de APK y
emulador Android 15 (incluido el ensayo `RemoteViews` de los widgets).
La ejecución publicó la APK de desarrollo y las fuentes reconstruidas.
No sustituye una prueba del flujo completo con la fotografía original del
horario mostrado en la incidencia.

## Aprendizaje adaptativo de fotografías (3.15.6)

Agenda Clara guarda **únicamente la confirmación explícita de una persona**
sobre dos nombres de cursos: «son el mismo curso» con el nombre canónico
elegido, o «son distintos». No aprende de lecturas OCR sin corregir.

**Secuencia:** foto y OCR → propuestas de cursos → aceptación o separación
explícita → guardado exitoso del horario → aprendizaje local. En la próxima
fotografía, si se encuentra **exactamente la misma pareja de nombres**
(normalizada por espacios, tildes y mayúsculas), la app puede reutilizar
esa confirmación. Una regla negativa evita sugerir repetidamente la unión
rechazada. Una regla positiva reutiliza solo el nombre canónico confirmado.
Las agrupaciones resultantes se muestran en el resumen antes del guardado.

**Límites de seguridad:** no se generaliza automáticamente una decisión a
otras asignaturas; los niveles I/II, los grupos explícitos, nombres
incompatibles y las coincidencias nuevas siguen bajo revisión. Si la
persona cambia de opinión, la última confirmación sustituye la anterior.
Se conservan días, horas y aulas. La memoria se limita a 80 decisiones.

**Privacidad y control:** la memoria usa preferencias privadas del
dispositivo; la app no envía fotografías ni reglas a un servidor para
aprender. En «Mis cursos» y en la revisión de fotos se puede entrar en
«Aprendizaje local» para visualizar las decisiones, pausarlas, borrar
una regla o limpiar todas. Las reglas aprendidas no modifican por sí
solas horarios antiguos. El uso de copias de seguridad del sistema
operativo depende de la configuración de Android.

Se mantiene ML Kit OCR local. Esta mejora aprende **correcciones de nombres
confirmadas**, pero no entrena por su cuenta un modelo visual capaz de
reconocer cualquier formato de horario. La precisión con fotos reales y
el funcionamiento después de restaurar copias del dispositivo requieren
pruebas adicionales.

## Estado de funcionamiento

- **Verificado por CI (base):** generación APK 3.15.4, firma de desarrollo,
  instalación/apertura en Android 15, 13/13 diseños `RemoteViews`,
  pruebas académicas y de OCR sintético.
- **No verificado todavía:** presentación de datos reales en el lanzador
  del teléfono del usuario, todos los tamaños de pantalla, interacción de
  los botones y colecciones en los widgets, persistencia de una foto real
  tras reiniciar y precisión OCR con fotografías reales. Un resultado
  13/13 de inflación no demuestra que todo el comportamiento sea perfecto.

Se mantienen las mejoras de la 3.15.2: filtrado por perfil y curso,
actualizaciones concurrentes, fechas de evaluación confirmadas y revisión
humana de coincidencias OCR. La fase 84 no modifica el contenido del
widget fotográfico.
