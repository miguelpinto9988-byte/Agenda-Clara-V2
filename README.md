# Agenda Clara — Android nativo

**Versión actual de la aplicación:** 3.15.3 (`versionCode 70`). El historial
de migraciones se mantiene hasta `updates/phase84`.

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

- Flujo principal: [Agenda Clara 3.15.3 — Widgets y OCR](.github/workflows/agenda-clara-ocr-photo-3151.yml).
- Los cambios de `updates/phase82/**`, `updates/phase83/**`, `updates/phase84/**`
  y del propio flujo activan la compilación Android 3.15.3 en `main`.
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

## Estado de funcionamiento

- **Verificado por CI:** generación APK 3.15.3, firma de desarrollo,
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
