# Widget de notas adhesivas · Agenda Clara 3.9.1

El nuevo widget de inicio utiliza las dimensiones mínimas y de redimensionamiento del widget de tareas: 250 × 160 dp, con mínimos de redimensionado de 180 × 110 dp y ajuste horizontal y vertical.

- Botón **＋**: abre directamente el editor de notas, no la creación de tareas.
- Tarjetas desplazables: muestran PNG adhesivo del color de cada nota y texto **en negrita**, con título, contenido y **fecha de la nota**.
- Al pulsar una tarjeta se abre esa nota para editarla. No se crean tareas ni alarmas.
- El encabezado abre la categoría «Notas» en Agenda Clara.
- Las modificaciones y eliminaciones actualizan las instancias del widget.
- Compatible con Android 8–11 (RemoteViewsService) y Android 12+ (RemoteCollectionItems), con alternativa a servicio para colecciones extensas.
- Las dimensiones y el contenido visible dependen del launcher Android. Se muestran tantas notas como quepan; la lista es desplazable.
- No se guardan capturas ni contenidos de notas en registros de diagnóstico.

**Comprobaciones:** ejecutar la reconstrucción secuencial de la aplicación, pruebas Python y Gradle, instalar en emulador y confirmar que Android detecta el proveedor. La interacción con un widget colocado en un launcher real requiere validación manual adicional.

Prueba manual: mantener presionada la pantalla de inicio → Widgets → Agenda Clara → Notas adhesivas. Ajustar el tamaño horizontal y vertical, añadir una nota con el botón ＋, elegir una fecha y un color, guardar, comprobar actualización y pulsar la tarjeta para editarla.
