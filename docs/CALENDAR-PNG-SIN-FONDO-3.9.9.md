# Agenda Clara 3.9.9 — iconos PNG sin fondo decorativo

Se sustituyen los dos PNG de **Ir a hoy** y **Horario de clases** por iconos individuales: se elimina el recuadro degradado exterior, conservando el calendario, el check/reloj y la variedad de colores *dentro del propio icono*.

- Recursos PNG RGBA de 256×256, con esquinas 100 % transparentes y contorno exterior vacío; no existe un fondo cuadrado multicolor.
- Se mantiene el tamaño aprobado de **28 dp** para Ir a hoy y **32 dp** para Horario de clases, con **12 dp** de separación de texto.
- Texto y controles nativos sin cambios, tipografía en negrita.
- Ninguna modificación de la navegación inferior de cuatro pestañas ni de los datos y horarios.
- La instalación se realiza después de phase38 para reconstruir la APK desde las fuentes, no simplemente actualizar capturas.
- Se comprueba la transparencia pixel a pixel (decodificación PNG/filtros), la integridad CRC y la compilación Android.
