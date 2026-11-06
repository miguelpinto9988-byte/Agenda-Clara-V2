# Agenda Clara 3.15.5 — Revisión semántica del OCR fotográfico

## Incidente reproducido
La fotografía de horario generó grupos distintos para:
- `TENDENCIAS EDUCATIVAS (E) EDUCATIVA I`
- `TENDENCIAS EDUCATIVAS (E) EDUCATIVA`
- `TENDENCIAS EDUCATIVAS (E)`

Además, el comparador 3.15.4 proponía unir `Tutoría educativa` e
`Investigación educativa` porque ambas contenían la palabra genérica
«educativa». La lista «Mis cursos» agrupaba por nombres normalizados exactos,
por lo que un descriptor repetido creaba una categoría adicional.

## Flujo 3.15.5
1. La fotografía se decodifica en el teléfono y se producen lecturas OCR
   mediante geometría de cuadrícula, columnas y texto.
2. Se genera una **vista previa en memoria**, acotada en resolución, con
   contornos aproximados de los bloques geométricos detectados. Los contornos
   no asignan por sí mismos una clase a un curso.
3. Las propuestas con un descriptor repetido **después de un código entre
   paréntesis**, p. ej. `(E) EDUCATIVA`, pueden limpiar ese duplicado. Se
   registra una advertencia que muestra el texto original y el propuesto.
4. Se conserva el estado desmarcado de lecturas OCR complementarias, incluso
   después de limpiar un nombre. No se importan sin selección expresa.
5. El comparador revisa primero identidad de nombres, niveles romanos,
   grupos explícitos, abreviaciones, palabra inicial distintiva, conceptos
   compartidos útiles y errores ortográficos. Adjetivos como «educativa» y
   conectores no bastan por sí solos para sugerir una unión.
6. Una diferencia de nivel explícito **I/II** se conserva. Si solo una de
   las lecturas indica un nivel, la coincidencia es *incierta* y requiere
   aceptación humana; nunca se fusiona sin confirmar.
7. Antes de guardar, se ejecuta una auditoría que comprueba sesiones
   inválidas, nombres posiblemente fragmentados y bloques idénticos. La
   pantalla final muestra el número de cursos y sesiones y los puntos de
   revisión encontrados.
8. Para corregir registros **ya guardados**, «Mis cursos» incorpora la
   acción «Revisar nombres duplicados del OCR». Ofrece sugerencias y solo
   modifica los nombres cuando la persona confirma. La base de datos aplica
   todos los cambios del perfil en una transacción, sin eliminar ni
   reprogramar sesiones manualmente.

## Garantías
- No se cambia ningún horario almacenado al actualizar la APK.
- No se mezclan cursos de perfiles diferentes.
- No se pierden sesiones, días, horas o aulas en una unión aprobada.
- No se modifica el widget de fotografía fija.
- El procesamiento de fotos sigue siendo local, sin subir la imagen.
- Un nivel I real y otro nivel II real jamás se fusionan automáticamente.

## Límites y validación pendiente
Estas mejoras son **heurísticas de visión geométrica y análisis contextual**
sobre ML Kit OCR, no un modelo general de visión artificial que comprenda
cualquier fotografía. Requieren comprobación con fotos reales, OCR de texto
inclinado, abreviaciones raras y clases de distintas asignaturas que comparten
un mismo concepto. La previsualización marca zonas candidatas, pero no da
una confianza de clasificación aprendida ni etiquetas por cada píxel.

La prueba Java `Phase86SemanticPhotoTests.java` reproduce los casos
observados y revisa las regresiones de niveles, grupos, horas y
normalizaciones. GitHub Actions debe aprobar esas pruebas, la APK y
Android 15 antes de integrar esta rama en `main`.
