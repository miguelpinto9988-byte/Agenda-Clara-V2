# Paneles: iconos Exámenes, Horarios, Cursos y Mi día

Estado: integración de rutas y etiquetas iniciada en esta rama. La compilación de Android utiliza la biblioteca existente hasta que se suban los cuatro PNG nuevos; no afirmar que contiene las ilustraciones finales antes de sustituirlos.

## Archivos esperados
Los archivos deben almacenarse en el proyecto Android después de reconstruir las fuentes, en `AgendaClara/app/src/main/res/drawable-nodpi/`, con estos nombres exactos:

| Panel | Archivo | Motivo visual |
| --- | --- | --- |
| Exámenes | `ic_adapt_ui_exam_review.png` | Lista de examen y birrete morado |
| Horarios | `ic_adapt_ui_class_schedule.png` | Calendario morado con reloj cian |
| Cursos | `ic_adapt_ui_course_add.png` | Libros con birrete |
| Mi día | `ic_adapt_ui_my_guide.png` | Lista diaria y calendario |

Los archivos generados por el usuario se encuentran en el paquete `Agenda-Clara-4-Iconos-Paneles-PNG.zip` entregado en la conversación. El repositorio aún no incluye sus bytes. Las imágenes no deben sustituirse por la lámina de 20 iconos con fondo degradado.

## Criterios de aceptación
1. PNG con canal alfa y transparencia comprobada, sin halo/fondo continuo.
2. La ruta del recurso y el identificador deben coincidir.
3. Verificar su proporción, legibilidad a 24–48 dp y contraste en temas claro/oscuro.
4. Sustituir los cuatro `ic_adapt_*.png` **después** de `updates/phase53/build_500.py --mode mobile`, porque ese generador sobrescribe los recursos.
5. Repetir las pruebas `updates/phase53/test_500.py` y compilar la APK. No alterar datos de usuario ni la rama principal.
6. Validar visualmente en el emulador las cuatro secciones.

## Mapeo de la interfaz
`updates/phase53/integrate_ui_icons.py` resuelve títulos y acciones de Exámenes, Horarios, Cursos y Mi día. Es un cambio de enrutamiento, no una afirmación de que los PNG nuevos ya están empaquetados.
