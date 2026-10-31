# Agenda Clara 3.9.3 · Notas adhesivas refinadas

**Diseño:** nuevos PNGs de papel para las seis variantes de color existentes (amarillo, rosa, azul, verde, morado, durazno), con chincheta roja esmaltada y brillo, punta metálica, sombra suave, textura sutil y esquina doblada. Los fondos se generan con Python estándar para facilitar su reconstrucción y no introducir dependencias.

**Contenido editable:** el título, cuerpo y fecha son TextViews; el PNG no contiene texto. El mismo fondo se ve en agenda, calendario, vista previa del editor y widget de notas (este último en miniatura).

**Fecha:** se elimina el glifo Unicode de cuadrícula y se reutiliza el PNG nativo ic_ref_date.png, al lado del texto con separación adecuada (8 dp). Se mantiene tipografía en negrita y el día elegido, sin hora límite ni estado de completado.

**Sin cambios:** los cuatro iconos inferiores, las alarmas de tareas, el calendario bonito, el botón «+», la base de datos de notas, sus categorías y sus colores.

**Pruebas:** tests estáticos/PNG, validación XML, compilación y emulador de pantalla. Para evaluar el aspecto en tamaños distintos de widget es recomendable una prueba manual adicional en un launcher físico.
