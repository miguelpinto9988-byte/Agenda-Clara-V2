# Ajuste previo a iconografía 3D · Acciones rápidas de «Mi día»

**Estado:** fuentes Android preparadas en rama aislada; **sin compilación, sin APK, sin fusión a main**. Se conserva el trabajo documental de fases 20–23. Este cambio se puede integrar en la próxima compilación autorizada, sin necesidad de producir la iconografía nueva primero.

## Solicitud aprobada como referencia visual

Se reemplaza la presentación de «Acciones rápidas» de Inicio por **tres tarjetas horizontales de ancho completo, apiladas verticalmente**, siguiendo el menú actual de creación del usuario, con PNG existentes, títulos y descripciones:

| Orden | Título | Descripción | PNG ya presente | Acción real (sin cambiar pestaña) |
|---|---|---|---|---|
| 1 | **Tarea rápida** | Dictar con comandos · sin grabación guardada | ic_ref_voice_microphone.png | VoiceQuickTask.show(activity) — reconocimiento por voz |
| 2 | **Nueva tarea** | Registrar una actividad | ic_ref_save.png | activity.openEditor(-1, null, null) — editor completo |
| 3 | **Nueva nota** | Nota adhesiva con fecha | ic_ref_sticky_note.png | StickyNotesUi.showEditor(activity, null) — nota original con fecha |

El anterior formulario reducido de «Tarea rápida» y el botón específico «Recordatorio» **desaparecen solo de estas tres tarjetas de Inicio**. El sistema de recordatorios dentro de tareas, los permisos y el menú «+» original **no se eliminan**. Las notas continúan usando el almacenamiento StickyNotesStore y la selección de fecha existente.

## Composición visual

- Título de sección «⚡ Acciones rápidas» conservado.
- Tarjetas blancas con borde suave y ligera elevación; icono PNG a 36–45 dp a la izquierda, título en negrita, descripción breve y flecha de acceso a la derecha.
- Tarjetas con alto adaptativo y descripción limitada a dos líneas para pantallas compactas.
- Se utilizan los PNG **ya incluidos en la APK**. No se crea, convierte ni reemplaza ninguna imagen.
- El resto de Inicio sigue intacto: horario actual, actividad del curso, actividades del día y pendientes, métricas, progreso y frase motivadora diaria original.

## Archivos modificados o agregados en esta rama

- updates/phase69/MiDiaQuickActions.java — implementación del panel.
- updates/phase69/apply_home_quick_actions.py — reemplazo seguro del módulo durante reconstrucción.
- updates/phase69/test_home_quick_actions_static.py — verificaciones del orden, las tres rutas, recursos PNG y funciones conservadas.
- .github/workflows/agenda-clara-ci.yml — agrega **pasos futuros** para aplicar y verificar el módulo después de la versión 3.13.1; esta rama **no** está incluida entre los disparadores automáticos.
- docs/iconografia/fases-20-23/fase23_catalogo_complementario.csv y fase23_mapa_integracion.md — corrigen los tres iconos P0 propuestos para la futura producción (micrófono, nueva tarea, nueva nota).

## Verificación y criterios pendientes

Se revisaron las tres entradas en el código 3.13.1 verificado: CreationChoices usa las mismas acciones e iconos; ApprovedPng contiene las claves y el recurso drawable-nodpi existe para las tres. Las comprobaciones estáticas se preparan para la reconstrucción; **no se afirman pruebas de emulador ni compilación Java de este nuevo cambio**.

Para la versión APK posterior a tu aprobación:
1. Reconstruir fuentes 3.13.1 y aplicar fases previas.
2. Ejecutar python3 updates/phase69/apply_home_quick_actions.py y python3 updates/phase69/test_home_quick_actions_static.py.
3. Compilar y ejecutar pruebas de emulador en 280/320/360 dp y tableta, comprobar voz con permiso de micrófono, nueva tarea y nota con fecha.
4. Revisar visualmente el panel y conservar la frase motivadora al final. Publicar solo tras QA satisfactorio.

**La nueva iconografía 3D multicolor continúa pendiente** de la producción/aprobación visual específica; no se ha iniciado todavía su integración en el APK.
