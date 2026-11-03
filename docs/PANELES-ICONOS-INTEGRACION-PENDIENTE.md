# Iconografía de paneles — Agenda Clara (Exámenes, Horarios, Cursos y Mi día)

La rama construye **cuatro iconos nuevos** (PNG con transparencia) en lugar de reutilizar las imágenes antiguas de esos cuatro recursos. La generación y sustitución ocurren **después** del catálogo de 500 iconos, antes de la compilación de la APK.

## Recursos y secciones

| Panel | Recurso Android | PNG Full HD |
| --- | --- | --- |
| Exámenes | `ic_adapt_ui_exam_review.png` | `icon_library_500/panel_fhd_2048/ic_adapt_ui_exam_review.png` |
| Horarios | `ic_adapt_ui_class_schedule.png` | `icon_library_500/panel_fhd_2048/ic_adapt_ui_class_schedule.png` |
| Cursos | `ic_adapt_ui_course_add.png` | `icon_library_500/panel_fhd_2048/ic_adapt_ui_course_add.png` |
| Mi día | `ic_adapt_ui_my_guide.png` | `icon_library_500/panel_fhd_2048/ic_adapt_ui_my_guide.png` |

- Generador reproducible: `updates/phase54/render_panels.py`.
- Estilo buscado: formas 3D redondeadas, colores sólidos variados, bordes reforzados, reflejos blancos localizados; transparencia RGBA y sin fondo degradado.
- Originales: **2048 × 2048** píxeles.
- Versiones Android: **256 × 256** píxeles, optimizadas para controles pequeños.
- El generador elimina los cuatro recursos antiguos antes de crear sus reemplazos.
- Los demás 496 recursos continúan disponibles para las funciones que dependen de ellos.

**Nota:** los cuatro PNG del generador son aproximaciones nuevas en geometría y color al estilo de referencia. No son las cuatro imágenes exactas generadas anteriormente en la conversación; esas imágenes no se han transferido como binarios a GitHub.

## Puertas de calidad

- Ejecutar `updates/phase53/test_500.py` después del reemplazo.
- Verificar los cuatro PNG finales y su canal alfa, hashes distintos y resoluciones en CI.
- Comprobar instalación y navegación de la APK en emulador Android 15.
- Revisar visualmente los paneles en la APK antes del merge.
- Conservar `main` sin cambios hasta completar la revisión.

Los archivos resultantes se publican como artefacto de GitHub Actions `Agenda-Clara-Paneles-4-Iconos-FHD-2048`; el ensamblado Android incluye las versiones reducidas dentro de la APK.
