# Agenda Clara · Iconografía 3D — Fases 20 a 23

**Estado:** documentación completa para revisión. **No se han producido PNG, cambiado archivos Java/XML, iniciado una APK ni empezado las fases 24–27.**

**Rama de diseño:** design/iconografia-fases-20-23. Derivada de Agenda Clara 3.13.1 validada (commit 6fa894bbe86c8fa4135e4468b784fb4d5c00a24c). Análisis realizado sobre el paquete de fuentes verificadas 3.13.1; se han mantenido todas las funciones existentes.

## Entregables

| Fase | Archivos | Resultado |
|---|---|---|
| **20 — Auditoría** | fase20_auditoria.md | 98 PNG existentes clasificados; pantallas exactas y brechas priorizadas |
| **21 — Sistema visual** | fase21_sistema_visual.md | Estilo premium 3D, transparencia PNG, maestros de 1024 px, exportación Android 256 px y medidas dp |
| **22 — Cursos** | fase22_catalogo_cursos.md + fase22_catalogo_cursos.csv | 40 conceptos de materias (39 específicos + 1 genérico), con metáforas 3D y prioridades |
| **23 — Complementarios** | fase23_mapa_integracion.md + fase23_catalogo_complementario.csv | 28 candidatos para acciones, actividades, estados vacíos, Estudio y otras zonas |

## Resumen cuantitativo de la auditoría y los catálogos

- Existentes en la APK 3.13.1: **98 archivos PNG**; 30 fondos de Inicio, 6 fondos de notas y 62 piezas de iconografía/decoración. No tocar los 4 iconos de métricas 3D ya aprobados.
- Propuestas de curso: **40** (16 P0, 16 P1, 8 P2).
- Propuestas complementarias: **28** (11 P0, 11 P1, 6 P2).
- **68 nombres PNG futuros, distintos entre sí** y con nombres de recurso Android válidos. No son 68 imágenes ya creadas ni 68 recursos obligatorios: para los marcados como «revisar reutilización» se usará un icono existente cuando tenga calidad/semántica suficientes.
- Prioridad inmediata a evaluar al producir: 27 propuestas P0, pero conviene validar primero una muestra artística antes de exportar el conjunto.

## Garantías de alcance

1. Los cursos reales se seguirán leyendo de ScheduleDatabase; los nombres con sufijos o abreviaturas no perderán su identidad.
2. Las tareas asociadas a un curso continúan vinculándose manualmente; un icono nunca modifica esa asociación.
3. Los 30 paisajes, las 50 frases motivadoras, los datos de tareas/notas, el menú inferior, calendario, WhatsApp, widgets, notificaciones y ajustes permanecen intactos.
4. No se han sustituido los iconos actuales del usuario, cambiado preferencias ni migrado bases de datos.
5. La documentación no está conectada al flujo de compilación automática: esta rama no figura en los disparadores de GitHub Actions.

## Verificación de calidad de la documentación

Se comprobaron los dos CSV en GitHub tras su escritura: 40 + 28 filas de contenido, **68 rutas de PNG propuestas únicas**, formato ASCII minúsculas/guiones bajos y distribución P0/P1/P2 válida. Se identificaron los métodos Java reales que alojarían las imágenes en la futura fase 26. No se afirma haber probado iconos que todavía no existen.

## Siguiente decisión pendiente

**Fase 24 (NO iniciada):** producir una hoja visual con 6–8 iconos representativos (incluido **Tendencias educativas**, otro curso, una tarea, una nota, un recordatorio y un estado vacío) para tu aprobación. Solo después crear y exportar el lote 3D PNG transparente.

**Fase 25 (NO iniciada):** comprobar tamaños, calidad, transparencia, contraste, peso y legibilidad a 24–40 dp.

**Fase 26 (NO iniciada):** integrar los PNG seleccionados con mapeo por materia y fallback genérico, sin alterar datos ni acciones.

**Fase 27 (NO iniciada):** ejecutar pruebas de Android en teléfonos pequeños/tabletas, revisar capturas y, si se aprueba, compilar la versión siguiente.

**Recomendación no aplicada:** dividir la producción en prioridad P0 y ampliaciones P1/P2. Reduce el peso de la APK y permite evaluar una muestra del nuevo estilo antes de comprometer todos los recursos.
