# Agenda Clara — Biblioteca de 500 íconos transparentes Full HD

## Objetivo y alcance

La rama \`feat/icon-library-500-fullhd-reflections\` amplía la biblioteca de 328 a **500 claves semánticas**. Agrega 172 identificadores \`ic_adapt_ui_*.png\` para elementos de interfaz, conserva las 328 claves existentes e incluye reflejos especulares blancos, colores variados de pigmentos sólidos y fondo RGBA transparente. Las ilustraciones se basan en imágenes 3D con licencia MIT de Microsoft Fluent Emoji y composiciones adicionales. **Las 500 imágenes resultantes son diferentes por contenido/hash, pero no se afirma que provengan de 500 dibujos fuente independientes.**

## Formatos

- **Biblioteca Full HD:** PNG RGBA 2048 × 2048 px, un archivo por identificador. No se incluye una textura de fondo rectangular. Los maestros se generan en CI y se publican como artefacto ZIP; la receta reproducible queda en Git.
- **Android:** PNG RGBA 256 × 256 px en \`app/src/main/res/drawable-nodpi/\`, para evitar cargar imágenes de 2048 px en botones pequeños. Presupuesto máximo conjunto de 15 MB.
- **Registro:** \`app/src/main/assets/adaptive_icon_catalog.json\` y el índice Java \`AdaptiveIconIndex.java\` enumeran los 500 nombres y recursos.
- **Auditoría:** los manifiestos JSON contienen SHA-256, dimensión, bytes y origen de cada imagen.

Los PNG tienen reflejos adicionales y una paleta discretizada; **no se dibujan fondos con degradados**. Las imágenes originales de terceros son ilustraciones tridimensionales y pueden mantener variaciones tonales como parte de la forma. La resolución 2048 garantiza tamaño de lienzo, **no crea detalles de origen ausentes** si una imagen fuente era más pequeña.

## Orden de integración

1. Reconstruir el catálogo 3.12.1 de 328 imágenes.
2. Ejecutar \`python updates/phase53/build_500.py --mode mobile\`. Verifica 500 archivos con hashes diferentes, genera el registro y el índice.
3. Ejecutar \`python updates/phase53/integrate_ui_icons.py\`. Vincula las acciones existentes mediante \`FeatureIconLibrary\` y personaliza los íconos de las cuatro tarjetas de inicio y los encabezados relevantes.
4. Ejecutar \`python updates/phase53/test_500.py\`, compilar Android y ejecutar las pruebas del emulador de la rama.
5. Para la biblioteca de alta resolución: \`python updates/phase53/build_500.py --mode fullhd\`. El flujo \`icon-library-500.yml\` la construye, revisa dimensiones/transparencia y publica una muestra y paquete ZIP.

## Integración visual existente

El enrutador reconoce botones de tareas, notas, calendario, horario, exámenes, sílabos, grabación de voz, notificaciones, WhatsApp, widgets, exportación/importación, copia cifrada, configuración y controles generales. Las actividades de cursos conservan \`AdaptiveIconLibrary\` para sus nombres y categorías.

La adición **no crea módulos funcionales nuevos** ni cambia bases de datos, notas, tareas, permisos, claves de firma o navegación. Las 172 claves incluyen posibles estados/controles de estas funciones; no se muestran todas al mismo tiempo en pantalla.

## Calidad y seguimiento

La validación automatizada cubre dimensiones, nombres, transparencias, integridad por hash, compilación y presupuesto. Para autorizar publicación definitiva todavía conviene revisar manualmente la legibilidad de los diseños en fondos claros y oscuros, precisión de símbolos para cada acción y tamaños Android de 20 a 48 dp. La semejanza estética con la referencia aportada debe evaluarse visualmente; la coincidencia artística exacta **no está certificada** por los tests.

## Fuente y licencia

Los recursos fuente se obtienen de Microsoft Fluent Emoji 3D, licencia MIT. El texto de licencia se incluye en los artefactos y en los assets Android. Los derivados añaden tratamiento de color, reflejos y composiciones.

Los artefactos de GitHub Actions son temporales (retención configurada de 30 días); el generador versionado es la fuente reproducible.
