# Agenda Clara — Fases 15 a 17: imágenes del encabezado

Estado: preparadas en rama independiente, sin ejecutar Gradle, compilar APK ni iniciar fases 18–19.
Rama: feat/mi-dia-header-15-17-no-build, derivada de 3.13.0.

## Fase 15 — Diagnóstico y causa raíz
El «08» de la captura del 4 de noviembre de 2026 está incrustado en el PNG bg_mi_dia_08.png, no en una vista de Android. La rotación cuenta días desde 2026-01-01 con módulo 30: 2026-11-04 selecciona el recurso número 08. Se inspeccionaron las 30 fotografías del paquete verificado: todas tienen una insignia numérica en la parte superior izquierda, a veces parcialmente fuera del marco. El encabezado posee actualmente un velo para legibilidad, pero carece de fundidos independientes en sus bordes superior e inferior.

## Fase 16 — Armonizar los bordes del paisaje
El script updates/phase64/apply_header_blends.py agrega dos gradientes blancos al componente MiDiaHeaderView.java, encima del fondo pero por debajo del saludo:
- Fundido superior de 68 dp para unir el paisaje con la cabecera blanca.
- Fundido inferior de 74 dp para conectar la imagen con la fecha flotante.
- Recorte activado únicamente en landscapeFrame; imageStack conserva la fecha sobresaliente.
- El escalado responsivo para teléfonos compactos/tabletas y el editor de saludo siguen operativos.

## Fase 17 — Limpieza de los 30 PNG con garantías
El script updates/phase65/normalize_backgrounds.py procesa únicamente las copias reconstruidas de bg_mi_dia_01.png a bg_mi_dia_30.png. Los recursos originales empaquetados en updates/phase51/artwork NO se sobrescriben.

La insignia se sustituye por un reflejo suave del paisaje vecino dentro de una región máxima 560 × 215 px. La zona hasta x=455,y=135 queda totalmente saneada, con transición en bordes. La parte central, la franja inferior y todos los píxeles fuera de esa esquina permanecen iguales. Se preserva el formato de paleta de 256 colores y la resolución original 1920 × 864, sin renombrar ni reordenar fondos.

El normalizador valida previamente las 30 huellas SHA-256 de los recursos aprobados. Si alguna no coincide, falla sin sobrescribir nada. Al finalizar genera un manifiesto privado de hashes para evitar conversiones duplicadas. El script updates/phase66/test_header_assets_static.py comprueba los recursos, los gradientes, los 30 fondos únicos y las 50 frases motivadoras.

## Comprobaciones realizadas sin APK
Con las 30 imágenes optimizadas extraídas del paquete de fuentes verificadas 3.12.0 se ejecutó localmente la misma transformación. Las 30 conservaron sus dimensiones, su formato de paleta y los píxeles fuera de la zona reparada. La comparación del fondo 08 y el mosaico de los 30 fondos se generaron como evidencias, no como capturas de una nueva APK.

Las 50 frases motivadoras, su rotación, los horarios, las tareas, las acciones rápidas y las cinco pestañas permanecen intactos.

## Pendientes, solo con confirmación
Fase 18: pruebas Android en emulador y dispositivo, revisión de las 30 imágenes, teléfonos pequeños y tabletas, accesibilidad, navegación y regresión. Existe una prueba antigua que no pudo encontrar el acceso «Más» durante el QA de 3.13.0; debe analizarse como parte de esa fase.

Fase 19: empaquetado, compilación, verificación de firma, APK y publicación después de completar la validación.

NO se incorpora la rama a los disparadores de CI ni se mezcla con main; no hay APK nueva.
