# Agenda Clara 3.10.0 · Estabilidad de ventanas, WhatsApp y avisos

Esta actualización no modifica las notas adhesivas, los diseños PNG ni los cuatro iconos de navegación inferior.

## Historial de WhatsApp
- La opción de mensajes anteriores verifica la selección y conexión activa antes de enviar la solicitud.
- El estado del grupo distingue solicitud, espera de conexión, error y resultado de lectura.
- No se confunde **solicitud enviada** con **historial realmente recibido**: WhatsApp puede entregar solo parte del historial o ninguno.
- La paginación limitada no elimina automáticamente propuestas previas de ese grupo.
- Se mantiene la autorización explícita y la revisión de propuestas; no se crean tareas sin aprobación.

## Teclado y diálogos
- Las ventanas flotantes vuelven a altura natural al ocultar el teclado.
- Los observadores de tamaño se retiran al cerrar el diálogo, evitando acumulación.
- El reloj no reconstruye doce vistas cada vez que cambia la hora; solo actualiza selección y textos.

## Avisos y notificaciones
- El diagnóstico detecta también canales de notificación bloqueados y ofrece acceso directo a ajustes de Android.
- «Completar» y «Posponer» presentan una confirmación en el panel de notificaciones.
- Las notificaciones de clases ofrecen «Ver horario» y «En 10 min», sin alterar la próxima alarma semanal.
- La entrega de alarmas depende también de los permisos y las restricciones de batería del dispositivo.

## Validación
Se ejecutan pruebas de estructura/migración, compilación y firma. Los comportamientos reales de teclado, servicio vinculado WhatsApp y entrega del sistema de alarmas requieren validación adicional en el dispositivo; no puede simularse el servidor de WhatsApp en CI.
