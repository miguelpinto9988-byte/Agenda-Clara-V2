# Agenda Clara 3.10.1 — lectura histórica limitada a un solo grupo

La causa verificada fue una lectura automática de **todos los grupos autorizados** al conectar, combinada con una sincronización nativa global no solicitada.

Se distingue la autorización para mensajes nuevos de la **solicitud explícita de mensajes anteriores**. El transporte nativo y el servicio Android mantienen únicamente el identificador (JID) del grupo solicitado; las respuestas históricas de otros grupos se descartan sin guardarse o analizarse. Los grupos seleccionados conservan el funcionamiento de **mensajes nuevos**.

Las respuestas del protocolo pueden transferirse cifradas en lotes amplios; Agenda Clara no controla ese transporte, pero filtra antes del análisis y almacenamiento. El componente nativo se debe recompilar para ambas ABI, ARM64 y x86_64, por lo que GitHub Actions incorpora Go y Android NDK antes de Gradle.

Los diálogos usan animaciones de entrada de 110 ms, salida de 75 ms, menú flotante de 110 ms y revelado de pestañas de 105 ms. Se preservan las características visuales y los cuatro iconos inferiores.

## Validaciones

Prueba nativa con **dos grupos autorizados y uno solicitado**; pruebas de estructura de Java y XML; compilación Android firmada; pruebas de emulador. La lectura de mensajes reales de WhatsApp requiere validar en un teléfono con conexión autorizada. Nunca se crean tareas sin revisión.
