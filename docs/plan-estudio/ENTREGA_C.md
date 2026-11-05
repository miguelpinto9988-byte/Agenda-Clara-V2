# Agenda Clara — Entrega C: integración final y APK 3.13.3

**Base:** fuentes verificadas de Agenda Clara 3.13.2, con entregas A y B aplicadas secuencialmente.

## Alcance de la entrega

- Calendario y Plan de estudio con dos pestañas en la estética de Agenda Clara.
- Hasta diez horarios independientes, con cursos, categorías y recuperación de sesiones anteriores.
- Selección y confirmación de curso en tareas manuales y por voz, incluida coincidencia parcial.
- Importación local de sílabos PDF, DOC y DOCX, reconocimiento de PDF escaneados, revisión de exámenes, fechas, horas y recordatorios antes de guardar.
- Avisos de 10 días y 12 horas o siete días antes de una evaluación.

## QA y compilación

La Entrega C es la **primera** en compilar los cambios de las entregas A y B, conforme a la decisión del usuario. El flujo independiente `.github/workflows/agenda-clara-c-final.yml`:

1. Recupera fuentes previamente verificadas, sin clave privada.
2. Aplica A y B, ejecuta pruebas de regresión y preflight C.
3. Compila con Android Gradle, recuperando la clave desde GitHub Secrets (no se añade al repositorio).
4. Verifica la estructura, el identificador de paquete y la firma.
5. Publica la APK como artefacto descargable en GitHub Actions.
6. Instala y abre la APK en un emulador Android 15 y adjunta una captura.

**Ejecución de referencia:** https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41945081534

## Límites del QA

La apertura en emulador es una prueba de humo, no una certificación de todos los flujos. Conviene comprobar manualmente un sílabo real en PDF, uno en DOCX y otro en DOC, así como fechas ambiguas, reimportaciones, restauración de datos, permisos de notificaciones y confirmaciones por voz. No declarar como superadas pruebas que no se han ejecutado.

La APK se publica como artefacto de GitHub Actions; no se crea automáticamente una Release pública permanente. La validez del artefacto depende de las políticas de retención de GitHub.
