# Agenda Clara · Fase 24.4 — 40 íconos de cursos

**Estado:** conjunto gráfico independiente, sin cambios al APK. Se conservan el encabezado, las 50 frases y las funciones de la aplicación.

## Entrega

- **40 archivos PNG individuales**, uno por asignatura, todos de **256 × 256 px**, RGBA, fondo realmente transparente y orientación frontal.
- **40 SHA-256 individuales** y manifiesto JSON/CSV en el ZIP.
- **36 escenas vectoriales SVG individuales nuevas**, conservadas en el ZIP para reproducibilidad; las **4 materias anteriormente aprobadas** (Tendencias educativas, Matemáticas, Investigación y Programación) se reutilizan como PNG propios. Ningún icono fue recortado de la hoja de previsualización.
- Los motivos nuevos son **ilustraciones vectoriales de apariencia 3D suave**, con gradientes, volumen ligero y colores variados; no se afirma que sean modelos tridimensionales renderizados.
- El ZIP contiene las carpetas `png/` y `svg/`, `inventario.csv`, `manifest.json` y `README.md`.

## Paquete alojado en Google Drive

- [ZIP — 40 PNG y fuentes SVG](https://drive.google.com/file/d/18x0uSFApNiD76Mh_IWDVIDCpJcadQ8Hc/view)
- [Previsualización de los 40 cursos](https://drive.google.com/file/d/1ecmLxinXduVGmsXAPPDIjHHGpWVMw-6-/view)
- [Carpeta de la fase 24.4](https://drive.google.com/drive/folders/1HP5bvPGBkKEk1qMmr3y8qOrIc5osaksq)

## Inventario de recursos Android

01. `ic_subject_general.png`
02. `ic_subject_tendencias_educativas.png` (ilustración individual previamente aprobada)
03. `ic_subject_pedagogia.png`
04. `ic_subject_psicologia.png`
05. `ic_subject_investigacion.png` (ilustración individual previamente aprobada)
06. `ic_subject_tecnologia_educativa.png`
07. `ic_subject_matematicas.png` (ilustración individual previamente aprobada)
08. `ic_subject_comunicacion.png`
09. `ic_subject_ciencias.png`
10. `ic_subject_historia.png`
11. `ic_subject_biologia.png`
12. `ic_subject_quimica.png`
13. `ic_subject_fisica.png`
14. `ic_subject_ingles.png`
15. `ic_subject_programacion.png` (ilustración individual previamente aprobada)
16. `ic_subject_arte.png`
17. `ic_subject_geografia.png`
18. `ic_subject_economia.png`
19. `ic_subject_filosofia.png`
20. `ic_subject_literatura.png`
21. `ic_subject_lectura.png`
22. `ic_subject_escritura.png`
23. `ic_subject_educacion_fisica.png`
24. `ic_subject_didactica.png`
25. `ic_subject_evaluacion_educativa.png`
26. `ic_subject_educacion_inclusiva.png`
27. `ic_subject_sociologia.png`
28. `ic_subject_estadistica.png`
29. `ic_subject_robotica.png`
30. `ic_subject_diseno.png`
31. `ic_subject_administracion.png`
32. `ic_subject_contabilidad.png`
33. `ic_subject_derecho.png`
34. `ic_subject_ciencias_salud.png`
35. `ic_subject_marketing.png`
36. `ic_subject_musica.png`
37. `ic_subject_fotografia.png`
38. `ic_subject_deporte.png`
39. `ic_subject_emprendimiento.png`
40. `ic_subject_ingenieria.png`

## Pruebas de archivos

- 40/40 son PNG RGBA, 256 × 256 px.
- 40/40 muestran transparencia alfa real (mínimo 0; máximo 255; esquina superior izquierda transparente).
- 40 archivos con huella SHA-256 distinta; compresión ZIP probada sin errores.
- Los nombres son minúsculas ASCII compatibles con recursos Android.

## Próximas fases (no autorizadas aún)

- Producción/comprobación adicional de los **iconos complementarios** del catálogo de fase 23.
- Fase 25: comprobar legibilidad en 24–40 dp, contraste y tamaño en móviles compactos.
- Fase 26: integrar únicamente los PNG aprobados en `drawable-nodpi`, preservando datos y estados existentes.
- Fase 27: pruebas Android, capturas y compilación si el usuario lo autoriza.

**No se ha compilado ninguna APK, ni fusionado cambios a main.**
