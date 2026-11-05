# Agenda Clara 3.13.4 — Confirmación del nombre después de la foto

## Orden de creación desde fotografía

1. El usuario elige **Crear horario desde foto**, sin crear previamente ninguna categoría.
2. Abre una imagen de la galería o utiliza la cámara.
3. Agenda Clara interpreta los bloques, días, horas y nombres de cursos con su OCR local.
4. El usuario **revisa los cursos**, corrige bloques, descarta los incorrectos y responde a las ventanas de coincidencias entre cursos.
5. Solo después de esta corroboración, el OCR propone un **nombre de horario** si encuentra un encabezado explícito o una mención de semana (por ejemplo, `Horario: Educación 2026`, `Semana 4`).
6. El usuario puede **aceptar** el nombre sugerido o responder **No, escribir otro**. Si no hay nombre fiable, aparece directamente el campo de nombre manual.
7. Tras aceptar o escribir un nombre válido y distinto de los existentes, se crea exactamente un horario y su categoría, y se importan las sesiones corroboradas.
8. Si se cancela antes de confirmar el nombre, no se crea ningún horario ni categoría nueva.

## Casos especiales

- Hasta **diez horarios**: al alcanzar el límite se presenta un diálogo, sin crear otra categoría.
- Si se fotografía un horario ya existente desde su ficha, se añaden las clases al perfil seleccionado **sin renombrarlo automáticamente**.
- Si el OCR propone un nombre ya usado, no se crea un duplicado: debe escribirse otro.
- Si la lectura no reconoce un nombre, no se inventa uno a partir de cursos aislados.
- Si se desea agregar una clase manual durante la revisión de OCR, permanece en memoria hasta confirmar el nombre final.
- El fallo de actualización de avisos, tras persistir las clases, no provoca la creación de un perfil duplicado.

## Evidencia y limitaciones

La fase implementa cambios aditivos en `updates/phase74/apply_photo_first.py`, pruebas de fuente y pruebas JVM de nombres. Las funciones preexistentes (cinco pestañas, tareas, sílabos y otros horarios) permanecen en las fuentes verificadas 3.13.3.

La compilación 3.13.4 utiliza el mismo identificador de paquete y clave de desarrollo. La prueba de apertura en emulador no sustituye una prueba completa con fotografías reales y dispositivos físicos.

**Ruta:** `fix/horario-foto-primero-3-13-4-20261104`.
