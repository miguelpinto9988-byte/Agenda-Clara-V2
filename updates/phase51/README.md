# Fase 4 — Inicio «Mi día» (integración pendiente)

Base verificada: Agenda Clara 3.11.3. El objetivo es reemplazar únicamente la presentación de la pestaña Agenda, preservando el almacenamiento, las acciones, los widgets, la voz, WhatsApp, el calendario y la firma.

## Recursos aprobados
- 30 imágenes `bg_mi_dia_01.png` a `bg_mi_dia_30.png`, en `app/src/main/res/drawable-nodpi/`, 1920×864; usar `CENTER_CROP` y no deformar.
- 50 frases originales en `app/src/main/res/values/mi_dia_frases.xml`.
- `MiDiaDailyRotation.java` y `MiDiaHeaderView.java`, paquete `pe.agendaclara.app`.
- Artefacto local preparado: `AgendaClara_Fase4_Integracion_Recursos.zip` (no se almacena todavía en GitHub).

## Condiciones de aceptación
1. Integrar los archivos en la reconstrucción del proyecto *después* de `updates/phase50/apply_widgets_3_11_3.py`.
2. Sustituir el contenido visual de Agenda por Inicio/Mi día y preservar las acciones actuales.
3. Mostrar cuatro indicadores basados en registros reales; no inventar estadísticas.
4. Cambiar paisaje y frase por fecha local sin conexión.
5. Compilar APK y ejecutar las pruebas de regresión y emulador antes de declarar la fase completada.

**Estado:** documento de control, no implementación. No habilitar scripts nuevos en el workflow hasta que todos los recursos estén presentes y se valide el proyecto reconstruido. No crear backups por instrucción del propietario.
