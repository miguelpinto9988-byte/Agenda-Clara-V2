# Agenda Clara 3.9.2: iconos PNG de categorías
Las tarjetas de Mis categorías ya usan el símbolo almacenado en CategoryRegistry, en lugar de un OutlineIcon fijo de carpeta. El estilo y los colores elegidos se mantienen.

- Tamaño PNG de chip: 28 dp; separación icono-texto: 11 dp; altura: 54 dp.
- Márgenes de la tarjeta: 14 dp izquierdo y 16 dp derecho, además de 10 dp entre tarjetas.
- Los nombres mantienen su negrita y una sola línea con elipsis si el espacio es insuficiente.
- Gestión de categorías: icono de 32 dp con margen derecho de 12 dp.
- El encabezado del formulario de tareas usa el icono real, incluso al cambiar la selección.
- Categorías antiguas sin icono o con antiguo símbolo folder: PNG neutro other. Notas usa sticky_note.
- No se eliminan scripts de migración antiguos, ya que son necesarios para reconstruir la app.
- Los cuatro iconos de navegación inferior y la lógica de tareas/notas no se alteran.

Pruebas: reconstrucción secuencial, asserts de regresión, compilación Gradle y revisión en emulador.