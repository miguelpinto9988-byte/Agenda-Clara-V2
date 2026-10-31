# Agenda Clara 3.9.7 — Horarios por día, 12 horas

Se mantiene **sin cambios** toda la sección superior de selección de color (72 tonos, mezclador HSV, catálogo 360 colores) y los cuatro iconos de navegación inferior.

En el editor de clases se sustituyen las horas compartidas por tarjetas independientes por día. Cada tarjeta contiene su propia hora de inicio y fin, con controles **AM** y **PM** individuales y selector horario Android de 12 horas. Se pueden añadir días nuevos y quitar sesiones existentes con confirmación antes de borrarlas. El color del curso sigue siendo común para todos los días, pero las horas no se copian al guardar.

La persistencia original conserva el esquema `ScheduleEntry` de minutos desde medianoche (`0..1440`). Así los calendarios, las alarmas y la importación de fotografías siguen usando horarios sin ambigüedad. Las conversiones especiales son `12:00 AM = 00:00`, `12:00 PM = 12:00`, `04:30 PM = 16:30`; se rechazan intervalos invertidos o de más de 12 horas.

Si se edita un curso guardado, el editor reúne sus sesiones de días distintos sin fusionar registros diferentes del mismo día. Si se quita una sesión, se pide confirmación y se cancela únicamente su aviso. En una importación OCR, la corrección modifica solo el bloque seleccionado y respeta otras detecciones.

La interfaz se adapta a pantallas estrechas apilando los dos campos horarios, sin superponer botones AM/PM y texto. La tipografía en negrita permanece.

**Pruebas**: test de conversión Java, regresión estructural Python, compilación Gradle/Android en CI y comprobación en emulador de la presencia de los controles y su captura de pantalla. Los cambios se guardan en una rama independiente de `main`.
