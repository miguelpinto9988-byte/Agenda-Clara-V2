# Agenda Clara 3.15.9: «Mi horario» según Canva corregido

**Referencia aprobada y editada por el usuario:** Canva `DAHaMNOks0I`,
https://www.canva.com/d/96xjY-_dXFxRPDw (lienzo 1920×960, revisión 4).

## Correcciones preservadas

- Se reutiliza el PNG del lago y las montañas, sin SVG.
- Encabezado con panel blanco, icono de calendario, título PNG y birrete por delante de todo.
- Flechas grandes alrededor del selector de día; este navega por días reales, de modo independiente por instancia.
- Dos tarjetas con iconos originales PNG y texto dinámico, no nombres fijos.
- **Se elimina el botón inferior** (tal como el usuario lo dejó en Canva).
- Estados de clase (completada/pendiente) basados en la fecha y hora local, no en datos ficticios.
- En widgets bajos se muestra una tarjeta para evitar cortes; al ampliar se muestran dos.
- No se cambia ninguna clase ni archivo del widget `Mi día académico`, tareas o fotografía.

Los 16 PNG están comprimidos dentro de `assets.zip`, almacenado de forma permanente
en el repositorio; el instalador los descomprime a `res/drawable-nodpi`.
Android muestra fondos escalados y textos dinámicos, con ajustes responsive respecto de
la composición de escritorio de Canva.

## Instalación y pruebas

Partir del artefacto de fuentes verificado de Agenda Clara 3.15.8.

```sh
python3 updates/phase90/apply_canva_week_3159.py
python3 updates/phase90/qa_canva_week_widget.py
cd AgendaClara
./gradlew :app:assembleDebug
```

La compilación automática se realiza por GitHub Actions en la rama de integración.
No incluye modificaciones al documento original de Canva.