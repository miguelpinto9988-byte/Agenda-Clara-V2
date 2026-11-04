# Agenda Clara · Fase 24.5 · 28 iconos complementarios

**Estado:** conjunto de arte terminado y archivado, sin integración Android ni compilación APK.

## Entregables verificados

- **28 íconos PNG individuales**, todos en **256 × 256 píxeles**, vista frontal y canal alfa real (transparencia), creados como 28 composiciones **SVG vectoriales distintas** con colores y degradados variados. No son recortes de una lámina.
- Se incluyen los **28 SVG fuente**, junto con `inventario.csv`, `manifest.json` (incluye SHA-256 por PNG), README y previsualización elaborada **a partir de los PNG finales**.
- **28/28 PNG RGBA** y huellas SHA-256 distintas. Las esquinas son transparentes; pruebas de integridad ZIP superadas.
- Estilo: **ilustración vectorial frontal con efectos de profundidad y brillo 3D**, no renderizado volumétrico físico. Las piezas deberán superar la prueba de legibilidad a 24–40 dp en la fase 25.
- Los símbolos usados como base provienen de los contornos de **Font Awesome 4.7.0** (licencia SIL OFL para la fuente, consultable en https://fontawesome.com/v4/license/); no se redistribuye ningún archivo de fuente.

## Descargas confirmadas

- [ZIP de 28 PNG + fuentes SVG + inventario](https://drive.google.com/file/d/1E4cWuUhLbpbyJY1GrFeOrcE4rSFeXeaY/view?usp=drivesdk)
- [Previsualización de los 28 iconos](https://drive.google.com/file/d/1tSo4MlF64pgnFc5wsjUdI8_rA-57AImj/view?usp=drivesdk)
- [Carpeta completa en Google Drive](https://drive.google.com/drive/folders/1IZFC4ExG2yN9iS2gDsjd_0EpMYW1h09z)

## Inventario exacto

| Archivo | Uso |
|---|---|
| `ic_activity_course.png` | Actividad del curso |
| `ic_activity_today.png` | Actividades del día |
| `ic_activity_pending.png` | Actividades pendientes |
| `ic_activity_overdue.png` | Actividades atrasadas |
| `ic_state_no_link.png` | Sin actividad vinculada |
| `ic_state_empty_today.png` | Sin actividades hoy |
| `ic_state_all_done.png` | Sin pendientes |
| `ic_quick_task.png` | Tarea rápida por voz |
| `ic_quick_new_task.png` | Nueva tarea |
| `ic_quick_new_note.png` | Nueva nota |
| `ic_action_link_course.png` | Vincular al curso |
| `ic_state_empty_schedule.png` | Horario sin clases |
| `ic_activity_completed.png` | Actividad completada |
| `ic_activity_exam.png` | Examen |
| `ic_activity_homework.png` | Tarea académica |
| `ic_activity_reading.png` | Lectura |
| `ic_activity_practice.png` | Práctica |
| `ic_activity_presentation.png` | Exposición |
| `ic_activity_group.png` | Trabajo grupal |
| `ic_activity_lab.png` | Laboratorio |
| `ic_activity_project.png` | Proyecto |
| `ic_study_session.png` | Sesión de estudio |
| `ic_activity_workshop.png` | Taller |
| `ic_activity_debate.png` | Debate |
| `ic_study_resources.png` | Recursos de estudio |
| `ic_study_progress.png` | Progreso |
| `ic_class_virtual.png` | Clase virtual |
| `ic_calendar_academic.png` | Evento académico |

## Contexto de las fases anteriores

La fase 24.4 produjo 40 íconos individuales de materias. Este lote de 28 íconos complementarios eleva el catálogo disponible a **40 + 28 = 68 archivos PNG distintos**, repartidos en paquetes separados. La documentación anterior del proyecto, los recursos Android existentes, los 30 paisajes y las 50 frases motivadoras no han sido modificados por esta fase.

## Siguiente trabajo, aún no realizado

1. **Fase 24.6**: consolidar los 40 PNG de materias y los 28 PNG complementarios en un ZIP unificado, y detectar colisiones de nombres.
2. **Fase 25**: verificar legibilidad en 24, 32 y 40 dp; contrastes pastel y consistencia visual entre las dos colecciones.
3. **Fase 26**: integrar PNG aprobados en `app/src/main/res/drawable-nodpi` con selección semántica, fallback genérico y preservación de acciones.
4. **Fase 27**: pruebas de Android y compilación solo con autorización correspondiente.

**No se modificaron archivos Java/XML de la aplicación ni se inició GitHub Actions.**
