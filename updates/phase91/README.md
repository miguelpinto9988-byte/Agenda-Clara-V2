# Agenda Clara 3.15.10 — Notas adhesivas desde Canva

Fuente de diseño: Canva `DAHaMuEkoQk`, página 1, versión aprobada por el usuario el 6 de noviembre de 2026.

## Ámbito

- Paisaje original de la composición de Canva, fondo translúcido de lectura, cabecera, contador y botón de creación.
- Seis colores originales de notas, ilustraciones PNG separadas y chinchetas decorativas.
- El color de cada nota corresponde al color ya guardado en `StickyNotesStore`; no se crean categorías, tareas ni acciones ficticias.
- Cuadrícula de 2 columnas para widgets normales; lista legible para tamaños pequeños.
- Título, texto y fecha se recuperan dinámicamente de la base de datos; los textos de ejemplo de Canva no se incrustan.
- Tocar una tarjeta abre el editor existente; tocar `＋` crea una nueva nota; tocar el título abre la sección de notas.
- Los PNG se incluyen en el repositorio dentro de `assets.zip`; no dependen de enlaces de Canva.
- El código y los recursos de `Mi día académico`, `Mi horario`, tareas, fotografía y la base de datos de notas quedan intactos.

## QA

```bash
python3 updates/phase91/apply_canva_sticky_31510.py
python3 updates/phase91/apply_canva_sticky_31510.py  # idempotencia
python3 updates/phase91/qa_canva_sticky.py
cd AgendaClara && ./gradlew :app:assembleDebug
```

Los artefactos firmados y las pruebas Android se generan en GitHub Actions, no en Canva.
