# Agenda Clara · Fases 6, 7 y 8 — Diseño listo para revisión

**Estado:** implementación de fuentes preparada en una rama aislada. **No se ha compilado ni publicado una APK de estas fases.** No fusionar a main hasta la aprobación visual.

## Fase 6 — Contenido de Mi día

- Cuatro indicadores compactos de Tareas, Eventos, Estudio y Progreso, con adaptación a pantallas estrechas o texto ampliado.
- Lista de hasta tres tareas de hoy y atrasadas, incluyendo tareas completadas durante el día, con casillas conectadas al guardado y los recordatorios existentes.
- Próximo evento de los calendarios seleccionados y autorizados; sin nuevos permisos.
- Progreso **diario**: completadas hoy / (completadas hoy + pendientes para hoy o atrasadas). Cuando no hay actividades muestra ausencia de datos, no 100 %.
- Frase diaria al final, reutilizando las 50 frases locales; los 30 PNG siguen rotando sin Internet.

Archivos: updates/phase53/MiDiaDayMetrics.java, MiDiaDashboard.java, apply_dashboard.py, test_dashboard_static.py y MiDiaDayMetricsTests.java.

## Fase 7 — Cinco pestañas sin perder funcionalidades

La barra inferior ofrece **Inicio, Tareas, Estudio, Calendario y Más**. El interior de la aplicación conserva sus rutas de la versión 3.11.3:

| Pestaña | Destino |
| --- | --- |
| Inicio | Inicio — Mi día, con datos actuales |
| Tareas | Página original de tareas y categorías, con acceso visible al menú de creación |
| Estudio | Resumen de tareas académicas y acceso al horario existente |
| Calendario | Calendario original |
| Más | Hub hacia revisión de propuestas, WhatsApp, calendarios vinculados, notas, voz y ajustes |

Las antiguas páginas internas page=2 (Revisión) y page=3 (Conexiones) siguen existiendo. El widget y los enlaces profundos de notas siguen llevando a las tareas correspondientes; no se cambian tablas, permisos ni claves.

Archivos: updates/phase54/MiDiaNavigation.java, MiDiaStudyPage.java, MiDiaMorePage.java, apply_navigation.py y test_navigation_static.py.

## Fase 8 — Ajustes finales de diseño y calidad sin compilar

- Márgenes de Inicio más compactos y blanco uniforme; otras páginas conservan sus componentes.
- Cuatro indicadores por fila en teléfonos normales; dos filas si la pantalla es estrecha o la fuente está ampliada.
- Iconos vectoriales nativos en las cinco pestañas y áreas táctiles diferenciadas.
- El menú de nueva tarea, nota y dictado queda anclado al botón **visible** de Tareas cuando la barra antigua está oculta.
- Adaptación de las pruebas históricas de navegación (phase22, phase26, phase30), sin eliminar sus verificaciones funcionales.
- Comprobaciones estáticas de rutas, fuentes Java, 30 imágenes, 4 iconos y 50 frases.

Archivos: updates/phase55/apply_polish.py, test_release_readiness_static.py y esta guía.

## Orden de aplicación, cuando se autorice

Tras reconstruir la versión 3.11.3 y aplicar las fases anteriores:

1. python3 updates/phase53/apply_dashboard.py
2. python3 updates/phase54/apply_navigation.py
3. python3 updates/phase55/apply_polish.py
4. python3 updates/phase53/test_dashboard_static.py
5. python3 updates/phase54/test_navigation_static.py
6. python3 updates/phase55/test_release_readiness_static.py

El orden ya está preparado en el flujo de GitHub Actions **solo en la rama de diseño**. La rama está excluida de activación automática; no hay solicitud de integración.

## Antes de publicar la APK final

1. **Aprobación visual del usuario** de la previsualización de las cinco pestañas. El prototipo HTML usa datos ficticios y no constituye una prueba del ejecutable Android.
2. Integración autorizada a main.
3. Compilación de una única APK de actualización con el certificado anterior; ajustar versionCode si corresponde.
4. Pruebas reales en Android 15: navegación, casillas, dictado, notas, WhatsApp, calendario, accesibilidad y actualización sin pérdida de datos.
5. Resolver cualquier error de compilación o prueba y verificar la firma antes de entregar la APK.

**Restricciones respetadas:** sin Gradle, sin javac, sin APK, sin instalación, sin emulador para estas fases y sin cambios en main.
