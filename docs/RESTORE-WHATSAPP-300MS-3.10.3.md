# Agenda Clara 3.10.3 — Restauración de la recopilación de WhatsApp
Esta rama parte directamente de **Agenda Clara 3.9.9**, no de las correcciones 3.10.0–3.10.2 que produjeron regresiones.

Se recuperan sin cambios el servicio Java y el motor Go del sistema anterior. Se mantienen dos etapas: **sincronización general** del historial accesible de los grupos autorizados y **revisión específica** de un grupo mediante los controles correspondientes.

La sincronización general puede abarcar varios grupos autorizados al reconectarse: así funcionaba el sistema restaurado. Los mensajes de grupos no autorizados no deben analizarse. WhatsApp puede limitar el historial accesible al vincular un dispositivo.

Única modificación funcional respecto a 3.9.9: **animaciones de 300 ms** en apertura/cierre de diálogos, aparición del menú + y transiciones de pestañas, con desaceleración suave. No se ralentiza el feedback táctil del botón +.

Se conserva el diseño aprobado, notas, iconos PNG, navegación y datos guardados. Android versionCode **44** permite instalarla sobre 3.10.2 sin desinstalar la aplicación.

La prueba local validó el script y las comprobaciones del historial original. CI debe reconstruir la APK a partir de las migraciones hasta phase39, después aplicar exclusivamente la restauración de animaciones. Las pruebas con conversaciones reales requieren una vinculación de WhatsApp en el dispositivo del usuario.
