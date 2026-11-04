# Fase 21 — Sistema visual y reglas técnicas PNG

**Objetivo:** definir la familia de iconos 3D de Agenda Clara antes de generar recursos. Esta fase es solo una especificación; no crea PNG ni cambia la app.

## Identidad aprobada

- Estética 3D suave, limpia y colorida, coherente con los cuatro PNG existentes de Inicio (ic_midia_tareas, ic_midia_eventos, ic_midia_estudio e ic_midia_logros).
- Objeto principal reconocible más, como máximo, un elemento de apoyo. Material de aspecto pulido, contorno suave, luz superior izquierda y sombras ligeras integradas en el alfa.
- Fondo **transparente de verdad**, sin placa, recuadro, círculo ni fondo blanco pintado. El fondo pastel lo aporta la tarjeta Android.
- Colores distinguibles también por forma: usar como referencias azul #1675D1, violeta #7447DB y verde #10B95A, no obligatoriamente como únicos colores.
- No incluir nombres, letras, números pequeños, logos de terceros, marcas de agua ni detalles imposibles de leer a 24 dp.
- La asignatura mantiene su nombre y color configurados; el icono no cambia datos ni reemplaza la descripción textual.

## Resolución y exportación prevista (fase 24)

| Producto | Tamaño físico | Uso |
|---|---|---|
| **Maestro** | **1024×1024 px, PNG RGBA** | Alta resolución, archivo fuente; no se empaqueta en la APK |
| Grande | 512×512 px RGBA | Ilustraciones excepcionales de 64–96 dp |
| **Estándar** | **256×256 px RGBA** | Icono normal para Android en drawable-nodpi |
| Pequeño | 128×128 px RGBA | Solo si un icono lo requiere y supera QA |

«Full HD» describe normalmente imágenes panorámicas de 1920×1080. Para símbolos cuadrados a escala Android es más adecuado un maestro de 1024×1024 y exportación optimizada de 256×256; a 48 dp y densidad 4× se necesitan 192 píxeles.

**Parámetros gráficos:** sRGB; 8 bits por canal; alfa suave sin halos; relación 1:1; el objeto visible debe ocupar 74–82 % del cuadrado dejando 9–13 % de margen por lado; sin deformación ni recorte del objeto. No ampliar mecánicamente los actuales 72 px, porque no se gana detalle.

## Tamaños en interfaz Android

| Contexto | Tamaño recomendado | Reglas |
|---|---:|---|
| Lista compacta | 24–28 dp | FIT_CENTER; junto al texto |
| Próxima clase / clase en curso | **34–40 dp** | Alineación vertical y texto de dos líneas |
| Mis cursos / Estudio | 30–36 dp | Respetar colores de curso |
| Acciones rápidas | 28–36 dp | Ajustar filas en pantallas menores de 320 dp |
| Cabecera de bloque | 24–32 dp | Icono discreto, nunca desplazar el título |
| Estado vacío ilustrado | 44–56 dp | Una ilustración sin recargar |
| Banner especial | 64–80 dp | Solo si la vista tiene espacio |

Utilizar drawable-nodpi, ImageView.ScaleType.FIT_CENTER, LayoutParams basados en dp y márgenes apropiados. Los PNG no llevan texto de accesibilidad redundante cuando el contenedor ya tiene una descripción. Comprobar 280, 320, 360 y 412 dp, tableta, modo horizontal y tipografía 1.3×/1.6×.

## Nombre de archivo

- Asignaturas: **ic_subject_<concepto>.png** (por ejemplo ic_subject_tendencias_educativas.png).
- Actividades: **ic_activity_<concepto>.png**.
- Estados: **ic_state_<concepto>.png**.
- Acciones rápidas: **ic_quick_<concepto>.png**.
- Funciones de estudio: **ic_study_<concepto>.png**.

Usar solo minúsculas ASCII, números y guiones bajos; nombres únicos sin tildes ni espacios. **No sobrescribir** los PNG existentes ic_ref_*, ic_midia_* o ic_top_plus_animated.

## Reglas de correspondencia futuras (fase 26, NO implementadas)

1. Selección manual de un icono por curso, si existe, tiene prioridad absoluta.
2. Como propuesta inicial, identificar categorías por palabras clave inequívocas del nombre normalizado; «Tendencias educativas (E)» podría usar tendencias_educativas. No borrar sufijos del nombre original.
3. Si hay ambigüedad, mostrar **ic_subject_general**. No asignar materias erróneas ni realizar coincidencia difusa.
4. Una tarea vinculada a un curso comparte su símbolo de materia; el tipo de actividad puede mostrarse con un icono adicional diferente.
5. Los vínculos curso-tarea, el color del curso y el almacenamiento permanecen inalterados.

## Criterios para aprobar el arte en la fase 24

Iconos individuales realmente transparentes; un mismo lenguaje 3D; reconocibilidad a 24 y 40 dp; contraste en fondos pastel; peso de archivo optimizado; sin recortes; posibilidad de reproducir el mismo estilo para nuevos cursos. Presentar primero una hoja de previsualización con variedad de materias y 3 tamaños, obtener aprobación y solo después exportar el lote completo.

**Estado:** fase 21 completada en documentación; no se han generado imágenes.
