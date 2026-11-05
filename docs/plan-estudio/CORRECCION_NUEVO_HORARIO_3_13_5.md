# Corrección de «Nuevo horario» — Agenda Clara 3.13.5

## Incidencia reproducida

En la pantalla **Calendario > Plan de estudio**, la pulsación del botón **«＋ Nuevo horario»** seguía abriendo un diálogo de título que decía «Confirma el nombre que identificará su categoría y sus cursos» y mostraba el teclado. Este error permanecía en la APK **3.13.4**, aunque la acción secundaria «Crear horario desde foto» había sido corregida. La captura proporcionada por el usuario era correcta: existían **dos rutas diferentes**.

## Comportamiento requerido

La acción primaria debe presentar una ventana con las opciones **«Subir imagen del horario»** y **«Agregar cursos manualmente»**. No debe solicitar ningún nombre ni crear una categoría al entrar.

**Fotografía:** elegir/tomar imagen → detectar sesiones con OCR → seleccionar, corregir y corroborar los cursos y sus posibles duplicados → sugerir el título OCR cuando exista (incluida «Semana N») → confirmar esa propuesta o escribir otro nombre → crear categoría/horario e importar clases.

**Manual:** abrir edición de cursos → agregar clases con días y horas en memoria → revisar/corroborar cursos → escribir el nombre al final → crear categoría/horario y guardar las sesiones. Ninguna categoría vacía antes de terminar.

En ambos casos, cancelar sin guardar conserva los datos anteriores. Crear un horario adicional respeta el máximo de diez y las categorías existentes.

## Evidencia de la corrección

- `updates/phase75/apply_creation_entry.py` parchea tanto el botón principal como la pantalla inicial de un perfil vacío.
- `updates/phase75/test_creation_entry.py` comprueba **la cadena exacta y la llamada** que provocaban el error, y verifica ambos caminos antes de persistir.
- `updates/phase75/qa_emulator_creation.py` está diseñado para pulsar realmente el botón Nuevo horario y comprobar, vía jerarquía de accesibilidad de Android, el selector de método y las primeras pantallas de foto y manual.
- La primera prueba Android descubrió que `AlertDialog.Builder.setItems()` ocultaba ambas opciones bajo el tema actual, a pesar de mostrar el título y Cancelar. Se reemplazó con **dos botones reales en `setView()`** para garantizar su visibilidad.
- La validación de compilación e interacción real se realiza en `.github/workflows/agenda-clara-entry-final.yml`.

## Alcance de verificación

El test automatizado verifica el selector y los comienzos de ambos caminos. La corroboración con una **fotografía real**, la interpretación OCR de diferentes diseños y la creación final de una categoría tras la revisión deberán complementarse con pruebas prácticas en un dispositivo.

El número de versión pasa a `3.13.5` (`versionCode 61`) para distinguirlo de las APK 3.13.3 y 3.13.4. No se altera la base de datos de horarios existente.
