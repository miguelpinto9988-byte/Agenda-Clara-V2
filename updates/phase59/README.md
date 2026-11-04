# Agenda Clara · Fases 9–11 (sin compilación)

Estado: **fuentes implementadas en rama aislada para revisión**, sin APK, sin emulador, sin build y sin fusión a main. No iniciar las fases 12–14 sin nueva aprobación.

## Fase 9 — Encabezado panorámico

El encabezado no utiliza una tarjeta con bordes redondeados para la fotografía. El paisaje ocupa **todo el ancho de Inicio**; el saludo se superpone sobre un degradado más transparente y la fecha queda flotante en el borde inferior. La altura responde a la anchura del dispositivo, toma como referencia la proporción original 1920×864 y está limitada para que el saludo siga siendo legible en teléfono. Los indicadores y demás tarjetas mantienen margen interior. Se conservan los 30 fondos diarios y las 50 frases.

Archivos: phase56/MiDiaHeaderView.java y phase56/apply_hero.py.

## Fase 10 — Clase en curso o próxima

La tarjeta principal bajo «Mi día» deja de sugerir «Conectar calendario»: ahora consulta exclusivamente el **horario local existente** en ScheduleDatabase (class_schedule.db), con las sesiones recurrentes de ScheduleEntry.

El motor MiDiaNextClass:
- omite clases inactivas o inválidas;
- usa día ISO (lunes=1, domingo=7) y hora local;
- muestra primero una sesión en curso cuando inicio <= ahora < fin;
- de lo contrario elige la siguiente clase hasta siete días adelante;
- muestra curso, fecha, franja horaria, aula y profesor disponibles;
- abre el horario actual de clases al pulsar la tarjeta;
- no inventa clases y no necesita acceso al calendario del sistema.

Las estadísticas de Eventos y la pestaña Calendario original permanecen sin cambios. La tarjeta se actualiza al volver a Inicio y con la actualización periódica que ya tiene MainActivity.

Archivos: phase57/MiDiaNextClass.java, MiDiaClassCard.java, apply_schedule.py.

## Fase 11 — Actividades del curso, del día y pendientes

«Actividad del curso» muestra solo tareas vinculadas explícitamente por el usuario al curso de la clase seleccionada. **No se infiere la vinculación por coincidencia aproximada de texto.** El botón «Vincular tarea al curso» permite elegir una tarea pendiente existente; el botón «×» quita solo esa asociación, sin borrar la tarea.

La vinculación se guarda en un archivo privado nuevo de SharedPreferences, independiente de las bases de datos actuales. Se almacena el ID de tarea y la identidad normalizada de curso según ScheduleCourseColors.identity. Si el curso o tarea desaparece, su vinculación no produce falsos positivos ni altera los datos originales. No hay migración de datos.

«Actividades del día» muestra tareas programadas para hoy y tareas completadas hoy. «Actividades pendientes» muestra todas las tareas todavía sin completar, incluso atrasadas, futuras o sin fecha. Se puede marcar una tarea desde Inicio usando Store.save, Reminders y TaskWidget originales, o abrir sus detalles. Ambos apartados tienen estados vacíos reales.

La frase motivadora de las **mismas 50 frases** sigue al final, después del progreso, sin ninguna alteración del texto ni rotación.

Archivos: phase58/MiDiaCourseLinks.java, MiDiaActivitiesUi.java, apply_activities.py.

## Orden futuro de migraciones (no ejecuta build en esta rama)

1. Reconstruir las fuentes 3.12.0 y aplicar actualizaciones hasta phase55, como el flujo actual.
2. python3 updates/phase56/apply_hero.py
3. python3 updates/phase57/apply_schedule.py
4. python3 updates/phase58/apply_activities.py
5. python3 updates/phase59/test_9_11_static.py
6. Solo después de autorizar la etapa final: compilar Android, probar en emulador y revisar la firma.

El flujo CI en esta rama incluye los pasos futuros de preparación, pero **los pushes a esta rama no activan GitHub Actions**. Tampoco se modifica la versión de la aplicación en estas fases.

## Control de calidad sin compilación

- Se verificó localmente la aplicación secuencial de los tres cambios sobre las fuentes originales verificadas 3.12.0: los anclajes de fase 9, fase 10 y fase 11 aparecen exactamente una vez.
- Se verificaron 30 imágenes PNG diferentes y las 50 frases conservadas en el paquete de fuentes.
- Los archivos base ScheduleDatabase.java, ScheduleEntry.java, Store.java y Task.java quedan sin modificaciones.
- Se verificó la estructura Java (balance de llaves, paréntesis y literales) de los nuevos componentes, sin ejecutar javac.
- La nueva prueba estática se ejecutará cuando se autorice integrar la rama; **todavía falta comprobar la compilación Java, el render en emulador, las transiciones de horario y las interacciones reales.**

## Revisión antes de continuar

Confirmar la presentación del panorama en tableta horizontal y teléfono vertical. Tras su aprobación se iniciarán las fases 12–14 para incorporar acciones rápidas, revisar progreso/frases sin cambiarlas y completar optimización y pruebas. La APK se compilará solamente cuando el usuario lo autorice.
