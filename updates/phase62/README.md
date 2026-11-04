# Agenda Clara 3.13.0 · Fases 9–14 · Entrega aprobada

## Alcance

Esta rama contiene las fases 9–11 previamente revisadas y las fases 12–14 aprobadas para compilación:

- **9:** paisaje panorámico a todo el ancho de Inicio, con fecha flotante.
- **10:** clase en curso o próxima clase desde ScheduleDatabase, sin inventar horarios ni modificar el calendario Android.
- **11:** vinculación explícita tarea–curso, actividades del día y actividades pendientes.
- **12:** acciones rápidas en Inicio: tarea sin fecha (creación inmediata), nota mediante editor existente y recordatorio con elección explícita de fecha/hora y avisos existentes.
- **13:** ajuste específico de la imagen para teléfonos pequeños, fuentes y fecha adaptables; en tabletas se conserva el paisaje panorámico. El progreso diario y las 50 frases originales rotatorias quedan al final.
- **14:** controles estáticos, pruebas unitarias Java de horarios, comprobación de tamaños 320 y 360 dp, paisaje horizontal en emulador Android 15, firma y APK de actualización.

## Compatibilidad y privacidad

Identificador de paquete sin cambios: pe.agendaclara.app. Nueva versión 3.13.0, versionCode 56, firmada con el mismo certificado de desarrollo del proyecto; no se modifica la estructura de las bases de datos existentes.

La vinculación de tareas con cursos sigue en SharedPreferences locales privados, independientes de Store SQLite. No se introducen permisos nuevos para el horario. Los 30 paisajes y las 50 frases funcionan sin Internet.

La nueva tarea rápida se crea sin fecha; el recordatorio exige seleccionar una fecha y hora futuras. Al crear ambos se usa Store.save, Reminders y TaskWidget.refresh. Las notas usan StickyNotesUi.showEditor, sin duplicar ni reemplazar el editor aprobado.

## Pruebas y limitaciones

Las pruebas de GitHub Actions verifican la reconstrucción de todas las fases, módulos Java, 30 paisajes, 50 frases, persistencia, compilación Android, firma y arranque de la aplicación con varias configuraciones de pantalla. Las pruebas de interacción y usabilidad deben complementarse con una revisión en un teléfono real, especialmente la visualización de clases y la creación de recordatorios con permisos de Android.

La APK se publica en GitHub Releases con la etiqueta v3.13.0-mi-dia-preview, como **versión preliminar** hasta completar la revisión funcional. No desinstalar una versión anterior con datos; realizar previamente una copia de seguridad de la app.

## Recomendaciones futuras (no aplicadas)

1. Incluir asociaciones curso-tarea en el mecanismo existente de exportación cifrada: permite restaurar también los vínculos.
2. Añadir un filtro académico por curso en Tareas: permite localizar rápidamente todas las actividades de una materia.
3. Mejorar pruebas de accesibilidad con TalkBack y tamaño de texto extremo: eleva compatibilidad sin modificar datos.
