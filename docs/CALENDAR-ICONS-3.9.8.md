# Agenda Clara 3.9.8 — dos iconos PNG nuevos en Calendario

Se reemplazan **únicamente** los caracteres tipográficos decorativos delante de «Ir a hoy» (▣) y «Horario de clases» (▦) por dos recursos PNG transparentes nativos de **192 × 192 píxeles**.

- **Ir a hoy:** calendario azul con el día señalado, 28 dp junto al texto «Ir a hoy»; separación de 12 dp y altura táctil de 54 dp.
- **Horario de clases:** calendario/horario con bloques de colores y reloj, 32 dp dentro de una celda de 36 dp; 12 dp de separación al título en negrita.
- Los PNG se instalan en `drawable-nodpi` y son recursos independientes del texto. Así se mantienen nítidos en cualquier densidad de pantalla.
- Se respeta la paleta azul, el texto en negrita y las funciones existentes de los botones. **No se modifica ninguno de los cuatro iconos de navegación inferior.**
- Código original y prueba de reproducción en `updates/phase38/generate_calendar_png.py`; imágenes finales en `updates/phase38/assets/`.
- Regresiones: se verifica la existencia de los PNG reales, sus dimensiones, la separación de icono/texto y que desaparezcan ambos glifos antiguos del Calendario. Se añade captura de emulador en `screenshots/25-calendario-dos-iconos-png.png`.

**Nota de pruebas:** se corrige además el acceso de la QA anterior al editor de clases: se abre mediante la interfaz de la app en lugar de intentar lanzar directamente una actividad Android no exportada. No cambia la visibilidad de la actividad ni los permisos de la aplicación.

**Recomendación opcional:** verificar contraste y legibilidad de ambos iconos con fuente Android al 130–160 % en un dispositivo físico. No se considera completada esa comprobación sin ejecutarla.
