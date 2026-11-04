# Agenda Clara — Fase 24: producción completa de iconografía PNG

**Estado:** completada como paquete descargable de arte. **La APK y los recursos actuales del proyecto Android no se han modificado.**

## Entregable verificado

- **68 iconos PNG diferentes:** 40 correspondientes a materias/cursos y 28 complementarios para actividades, acciones rápidas, estados vacíos, Estudio y calendario.
- **136 archivos PNG:** un maestro individual de **1024 × 1024 px RGBA** y una exportación optimizada de **256 × 256 px RGBA** por cada icono.
- Transparencia alfa real, esquinas transparentes, nombres únicos compatibles con Android y SHA-256 individual registrados en el manifiesto.
- **8 iconos 3D de generación individual** en la muestra estética aprobada; **60 iconos 3D vectoriales elaborados como recursos individuales** (no son recortes ampliados de un cartel).
- Paquete ZIP y tres láminas de previsualización proporcionados como archivos adjuntos de la conversación donde se completó esta fase. **Los binarios PNG todavía no se han subido a este repositorio**, para mantener separada la producción artística de la integración Android.

**Comprobación del ZIP final:** 142 entradas (68 maestros + 68 exportaciones + README + manifiesto JSON + catálogo CSV + 3 vistas previas). Prueba de integridad ZIP satisfactoria.

**SHA-256 del paquete ZIP:** `63f1fe90c6e745cce7f7b1939e92d02d371a9183c73faafa0cb1dc7abb421984`.

## Tres accesos rápidos aprobados

Se han reservado las versiones visuales originales en PNG de:

1. `ic_quick_task.png` — **Tarea rápida por voz** (micrófono multicolor).
2. `ic_quick_new_task.png` — **Nueva tarea**, con editor completo.
3. `ic_quick_new_note.png` — **Nueva nota adhesiva con fecha**.

Sus funciones fueron preparadas por separado en `updates/phase69/`; esta fase 24 produce **solamente arte** y no modifica esas acciones.

## Producción y uso

El ZIP adjunto contiene:

- `maestros_1024_rgba/`: 68 PNG para archivo y futuras exportaciones.
- `android_drawable_nodpi_256/`: 68 PNG destinados a la futura integración en `res/drawable-nodpi`.
- `manifest.json`: nombres, familias, origen, dimensiones, peso y SHA-256 de cada par de archivos.
- `catalogo.csv`: inventario completo editable.
- `vistas_previas/`: catálogo de cursos, complementarios y ocho recursos originales.

El arte generado vectorialmente usa siluetas de **Font Awesome 4.7.0**, con atribución e información de licencia disponibles en https://fontawesome.com/v4/license/. No se redistribuyen fuentes.

## Límites y siguiente fase

**Fase 24 cerrada.** No se ha realizado QA de legibilidad de cada icono en dispositivos Android (fase 25), ni mapeado dinámico curso↔icono, ni pruebas de rendimiento con todos los recursos (fase 26), ni compilación APK y emulador (fase 27).

La fase 25 debe revisar el aspecto y reconocimiento a 24, 32, 40 y 56 dp, contraste sobre tarjetas pastel, nitidez en pantallas de alta densidad, posibles similitudes semánticas y preferencia del usuario entre los diseños 3D originales y las variantes vectoriales. **No modificar silenciosamente estos archivos de arte sin autorización.**
