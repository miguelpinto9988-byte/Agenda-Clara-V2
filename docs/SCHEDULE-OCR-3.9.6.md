# Agenda Clara 3.9.6 · Comprensión de fotografías de horarios

**Objetivo:** evitar que el OCR convierta cada aparición de una materia en un curso nuevo. Una materia conserva **varias sesiones** con sus propios días, horas, aulas y docentes.

## Motor de detección

- Comparación exacta con normalización de tildes y plurales, detección de errores de OCR de pocos caracteres y **títulos truncados por palabra completa**, como **«Tendencias» ↔ «Tendencias Educativas»**.
- No fusiona automáticamente materias diferentes ni nombres de grupos, niveles romanos o números distintos: «Historia I» no equivale a «Historia II». Materias genéricas como «Historia» frente a «Historia Universal» se mantienen independientes, salvo edición manual.
- Informa tanto los **bloques** como los nombres OCR y una **estimación provisional** de cursos posibles. Esta última no es un resultado definitivo.
- La ventana de corroboración permite **✓ Sí · mismo curso** (tarjeta verde con degradado suave) o **papelera roja No · separados** (tarjeta roja suave). Existe la opción de cancelar toda la importación.
- Cuando acepta una coincidencia, conserva el nombre más completo del curso y mantiene separadas las sesiones de diferentes días u horas. Si son dos lecturas OCR del mismo bloque horario, se deduplica la sesión antes de guardar.
- Si niega una coincidencia entre nombres diferentes, conserva ambos nombres. Si el OCR muestra el mismo nombre para dos cursos realmente distintos, usa «(grupo 2)» para diferenciarlos, sin borrar sesiones.
- El reconocimiento sigue siendo **local** mediante ML Kit; no sube la imagen ni se guarda nada sin aprobación.

## Control de calidad

La suite usa horarios sintéticos, incluyendo dos sesiones obtenidas de posiciones de fotografía y nombres recortados. También comprueba nombres distintos, sufijos romanos, errores de OCR y aceptación o rechazo sin perder horas. Se ejecuta junto a las pruebas históricas de 14 bloques / 8 cursos y la compilación Android.

**Limitaciones:** no se garantiza que toda fotografía se interprete perfectamente: sombras, celdas mal delimitadas, textos superpuestos y cursos realmente simultáneos pueden requerir edición manual. La confirmación permite resolver ambigüedades antes de importar.
