# Agenda Clara — Android nativo

**Versión integrada de la rama principal:** 3.15.2 (`versionCode 69`).

La rama `main` contiene el historial de migraciones hasta la fase 83, incluidas
las correcciones de los widgets académicos, la revisión del reconocimiento de cursos
mediante fotografía y la conservación del widget fotográfico de imagen fija.

## Compilación activa de main

- **Flujo principal:** [Agenda Clara 3.15.2 — Widgets y OCR fotografía](.github/workflows/agenda-clara-ocr-photo-3151.yml).
- Ante cambios de `updates/phase82/**`, `updates/phase83/**` o del propio flujo
  en `main`, GitHub Actions reconstruye las fuentes, ejecuta pruebas y compila
  la APK Android 3.15.2.
- El flujo usa el secreto `SIGNING_JKS_BASE64` para firmar la APK de desarrollo
  (la clave privada no está en el repositorio), verifica versión, firma y
  proveedores de los widgets, y comprueba la apertura de la app en Android 15.
- **Última ejecución integral aprobada antes de la integración en main:**
  [42164898395](https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/42164898395),
  con `compilar-y-probar` y `android` correctos.
- El flujo anterior [3.13.3](.github/workflows/agenda-clara-ci.yml) se conserva
  solo para activación manual: no genera una APK antigua automáticamente al
  actualizar `main`.

## Reconstrucción de fuentes y limitaciones conocidas

La arquitectura del repositorio sigue siendo **basada en migraciones**:
el archivo `Agenda-Clara-1.3.0-Fuentes-Sin-Clave.zip` contiene el proyecto
inicial, y los scripts `updates/**` conservan los cambios posteriores. El
árbol completo de Android 3.15.2 se reconstruye durante CI y se publica como
artefacto de fuentes, no como un árbol de archivos `AgendaClara/` en Git.

**Dependencia temporal de CI:** el flujo 3.15.2 descarga las fuentes
3.15.0 de la ejecución GitHub Actions `42145182419`. Dicho artefacto tiene
retención limitada; antes de su caducidad debe sustituirse por una fuente base
permanente o por una reconstrucción íntegra a partir del ZIP inicial y las
migraciones. No debe afirmarse que la compilación será reproducible
indefinidamente mientras dependa de un artefacto temporal.

## Cambios de la versión 3.15.2

- Los widgets del día y de la semana mantienen los datos del perfil académico
  seleccionado; las tareas están asociadas a su curso y las evaluaciones sin
  fecha no reciben fechas inventadas.
- La sincronización conserva las solicitudes de actualización concurrentes y
  aísla los fallos de cada proveedor de widget.
- Las evaluaciones semanales se priorizan globalmente entre cursos por
  proximidad de fecha, antes de limitar las líneas visibles.
- El importador OCR solicita revisar las coincidencias significativas entre
  nombres de cursos, sin fusionarlos silenciosamente.
- Los cinco archivos principales del widget fotográfico (código,
  configuración y recursos) se conservan sin modificación en esta fase.
- La migración Python 3.15.2 es repetible y revierte escrituras incompletas.

Consulte el [informe técnico de la fase 83](updates/phase83/README.md).

## Validación pendiente de interfaz

La ejecución automatizada prueba JVM, compilación, firma, instalación y
apertura en Android 15. Para una entrega final al usuario sigue siendo
recomendable probar los tamaños reales de los widgets en el lanzador,
el comportamiento con varios perfiles, la persistencia de la fotografía
seleccionada y el OCR con fotografías reales y consentimiento.
