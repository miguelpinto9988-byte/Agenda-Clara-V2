# Agenda Clara 3.15.2 — Sincronización de widgets y conservación de Fotografía

## Alcance
- Parte de la rama 3.15.1, que ya añade confirmación humana de nombres detectados al importar un horario por fotografía.
- Corrige la pérdida de solicitudes de refresco si las tareas o los horarios cambian mientras los widgets se están actualizando.
- Si un proveedor de widget falla, el otro todavía puede actualizarse.
- Los archivos del widget de Fotografía, su configuración y el comportamiento de imagen fija no se modifican.
- Mantiene la asociación por perfil y curso de los widgets académicos; no crea ni modifica datos académicos del usuario.

## Archivos
- `AcademicWidgetSync.java`: versión de la clase con bandera `dirty` y repetición hasta procesar todos los cambios recibidos.
- `apply_widget_refresh_3152.py`: integración sobre fuentes 3.15.1 (versionCode 68); valida anclajes, preserva SHA-256 de cinco archivos del widget fotográfico e incrementa a 3.15.2 (versionCode 69).
- `qa_widget_sync.sh`: prueba JVM con actualización concurrente y fallo simulado de un proveedor.
- `.github/workflows/agenda-clara-ocr-photo-3151.yml`: cadena 3.15.0 → corrección OCR 3.15.1 → actualización de widgets 3.15.2, pruebas JVM, compilación y verificación Android.

## Verificaciones realizadas en una copia local de fuentes 3.15.0
- Correcta la prueba de concurrencia con `javac` y dos proveedores simulados.
- Válido el manifiesto de proveedores `AcademicDayWidget`, `AcademicWeekWidget` y `PhotoWidget`.
- Diseños XML de widgets académicos y notas analizados sin errores.
- Cinco archivos del widget fotográfico idénticos mediante comparación SHA-256 antes y después de simular el parche.
- Se inspeccionaron los anclajes reales del sincronizador original de 3.15.0.
- La ejecución 42145182419 de GitHub Actions terminó correctamente para la base 3.15.0.

## Validaciones aún necesarias
- El flujo CI de esta rama debe compilar, firmar e instalar efectivamente la APK 3.15.2; la existencia del flujo no demuestra su éxito.
- Colocar cada widget en el launcher y comprobar sus datos con horarios, tareas y evaluaciones de prueba (perfiles separados, cambios concurrentes, modo claro/oscuro y tamaños pequeños).
- Probar el reconocimiento OCR completo de una fotografía real con consentimiento del usuario, revisar coincidencias y confirmar guardado; pruebas sintéticas no garantizan precisión en cualquier imagen.
- Comprobar persistencia y cambio manual de fotografía en el widget sobre un dispositivo real.
- No fusionar con `main` ni afirmar «APK final» sin esas verificaciones.

Rama: `fix/widgets-3151-refresh-qa-20261105`.
