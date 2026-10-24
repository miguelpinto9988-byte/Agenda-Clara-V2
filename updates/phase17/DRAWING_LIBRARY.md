# Agenda Clara — biblioteca de dibujo y acabados v1
Fecha: 2026-10-24. Objetivo: catálogo propio de técnicas, fuentes y compatibilidad, sin descargar recursos de terceros ni añadir dependencias sin revisión.

| ID | Técnica | Uso | Tecnología | Android | Estado |
|---|---|---|---|---|---|
| DRAW-01 | Canvas vectorial | símbolos, trazados | Compose Canvas/DrawScope | compatible con minSdk del proyecto | código integrado |
| DRAW-02 | Gradientes lineales | tarjetas y botones | Brush / LinearGradient | compatible | código integrado |
| DRAW-03 | Gradientes radiales | halos | Brush / RadialGradient | compatible | código integrado |
| DRAW-04 | Partículas estáticas | destellos discretos | Canvas | compatible | código integrado |
| DRAW-05 | Bordes redondeados | superficies | drawWithCache / Drawable | compatible | código integrado |
| DRAW-06 | Material Symbols | iconos semánticos | SVG a VectorDrawable | compatible | pendiente de selección/licencia por recurso |
| DRAW-07 | AGSL shaders | efectos de iluminación | RuntimeShader | Android 13+ (API 33) | investigación, NO integrado |
| DRAW-08 | Paper Shaders | malla, ruido, texturas | AGSL | Android 13+ | investigación, NO integrado |
| DRAW-09 | Vico | gráficos estadísticos | Compose | revisar versión y dependencias | opcional, NO integrado |
| DRAW-10 | Fuentes locales | jerarquía tipográfica offline | res/font | compatible | pendiente de selección |

## Estrategia
1. Base universal: Canvas y recursos vectoriales, sin red y sin dependencias externas.
2. Centralizar paleta y tamaños en tokens; no introducir una nueva estética sin comparación de capturas.
3. Evitar dibujar decoraciones sobre áreas táctiles; mantener etiquetas accesibles.
4. Usar efectos GPU únicamente con fallback para API < 33.
5. Respetar la escala de animaciones del sistema y el consumo de batería.
6. Validar contraste, modo oscuro, densidades de pantalla, RTL, tamaños de fuente y rendimiento.
7. Medir tiempos de render y capturar pantallas antes de aprobar fidelidad.
8. Registrar procedencia, licencia y versión de cualquier icono, fuente o biblioteca añadida.

## Fuentes verificables
- https://developer.android.com/develop/ui/compose/graphics/draw/overview
- https://developer.android.com/develop/ui/compose/graphics/draw/brush
- https://developer.android.com/develop/ui/views/graphics/agsl
- https://developer.android.com/develop/ui/compose/resources
- https://developer.android.com/develop/ui/compose/text/fonts
- https://developers.google.com/fonts/docs/material_symbols
- https://github.com/AndreFrelicot/paper-shaders-android
- https://github.com/patrykandpatrick/vico

## Estado
Los archivos AgendaDraw.java y AgendaGraphics.kt se copian al proyecto con apply_4_3_0.py. Se aplica el degradado a tarjetas de comunidades. Los componentes Compose restantes están disponibles para integrar pantalla por pantalla. No afirmar integración de shaders, fuentes ni paquetes externos.
