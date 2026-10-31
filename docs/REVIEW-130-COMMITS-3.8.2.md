# Agenda Clara 3.8.2 — revisión de integración y rendimiento

Comparación inicial: **130 commits por delante de main**, base de6636c.
El conjunto contiene un rediseño acumulado; NO es un cambio aislado de iconos.

| Fases | Cambios | Riesgo |
|---|---|---|
| 19–20 | Botón +, retirada Compose | Editor y dependencias |
| 21–23 | Categorías, calendario, modales | Persistencia y recordatorios |
| 24–25 | Negrita, colores, insets | Contraste y recortes |
| 26–27 | PNG, selectores y recurrencia | Estado visual, recursos |
| 28 | Contornos de la barra inferior, cachés | Selección azul/gris, render |

La compilación **ya invoca** 19–28 mediante runpy desde
updates/phase18/apply_3_8_2.py. Sus tests se invocan desde
updates/phase18/test_3_8_2.py. No se deben añadir llamadas duplicadas
al workflow: las migraciones no son idempotentes.

## Validación
- Compilar desde ZIP y conservar firma, datos y migraciones históricas.
- Ejecutar pruebas de regresión, JVM, APK y emulador Android.
- Recorrer Agenda/Calendario/Revisar/Conexiones, botón + y formularios.
- Recoger frames con gfxinfo y memoria PSS con meminfo.
- Comparar versiones únicamente con dispositivos, refresh y escenario iguales.
- Validar en un teléfono físico; no está disponible en el runner de GitHub.
- Revisar el diff completo de main antes del merge (cambios visuales y funcionales).

## Prueba física manual
Con Android SDK/ADB, aplicación instalada y depuración USB autorizada:

    python3 updates/phase29/performance_qa.py --mode physical --serial SERIAL --out local-device-qa/rendimiento.json

El script no instala APK ni extrae información personal. La prueba se completa
manualmente en el teléfono; aquí NO se afirma haberla ejecutado. El informe
de emulador se adjunta en screenshots/16-rendimiento.json y .md.
Sin un perfil anterior comparable, las métricas no prueban mejoras porcentuales.
La revisión de riesgos clasifica el alcance; no es una auditoría línea a línea
de cada uno de los 130 commits.
