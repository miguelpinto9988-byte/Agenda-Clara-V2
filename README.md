# Agenda Clara — Android nativo

Versión de compilación: **3.8.2 (versionCode 30)**.

## Compilación única

El único flujo de GitHub Actions activo es `.github/workflows/agenda-clara-ci.yml`. Comprueba migraciones, pruebas JVM, genera la APK con firma privada y valida su instalación en el emulador Android 15. Reutiliza la firma existente; no guarda claves en el repositorio.

**Importante:** la fuente inicial sigue en `Agenda-Clara-1.3.0-Fuentes-Sin-Clave.zip`. Los scripts secuenciales `updates/apply_*.py` y `updates/phase*/apply_*.py` **todavía se ejecutan en orden**. Por tanto no son código muerto y eliminarlos rompería la reconstrucción de la app. El último paso `updates/phase18/apply_3_8_2.py` elimina clases Java obsoletas solo si ya no existen referencias de producción.

Se retiraron los flujos de compilación y publicación de versiones 2.x–3.7 antiguas, además de scripts de inspección y emulador que dependían exclusivamente de ellos. Esto reduce las rutas de CI redundantes, pero **no implica que todo el código histórico de migraciones se pueda borrar**. El historial de Git conserva los archivos retirados para una recuperación si fuese necesaria.

Los archivos `WhatsAppNative.java`, el módulo nativo de WhatsApp, los motores OCR, la agenda, el calendario, la base de datos, los componentes Android y las pruebas de regresión se conservan mientras estén integrados en la aplicación.

## Resultado de limpieza 3.8.2

- Solo un flujo de compilación y pruebas.
- Retiradas las clases finales sin uso `AcademicAnnouncementInterpreter.java` y `ScheduleMultiDays.java` (tras comprobación de referencias).
- Se excluyen del ZIP de fuentes los informes temporales de `AgendaClara/build/`.
- La compilación falla si reaparecen clases obsoletas, si se eliminan módulos activos o si la versión no coincide.
- La compilación en Android y las pruebas de emulador deciden si un cambio es válido; esta limpieza no garantiza por sí sola mejoras de FPS o memoria.
