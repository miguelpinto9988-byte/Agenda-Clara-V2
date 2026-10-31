# Agenda Clara 3.9.5 — prototipo avanzado de comprensión de WhatsApp

## Alcance real

Motor local, determinista, de **propuestas para revisión**, no un modelo neuronal ni acceso irrestricto a WhatsApp.
Respeta la selección/autorización de chats existente y no transmite textos a servidores.

1. Separa hasta 40 instrucciones independientes de un mensaje con viñetas, punto y coma, oraciones y conectores como «y», «además» y «luego», cuando después aparece una acción independiente.
2. Mantiene las instrucciones compuestas («leer y resumir el capítulo») sin descomponerlas artificialmente.
3. Agrupa anuncios equivalentes del mismo autor y contexto durante hasta 48 horas si existen pruebas textuales del mismo asunto. Mantiene distintos los trabajos de asignaturas diferentes y evita inferir equivalencia por solo la palabra «informe».
4. Si dos fechas discrepan sin corrección expresa, **no fusiona** propuestas: las marca ambiguas para revisión.
5. Las correcciones con tema explícito pueden actualizar la **propuesta**, siempre señalando que la nueva fecha requiere confirmación. Las respuestas citadas siguen beneficiándose de la lógica anterior.
6. Conserva el flujo de aprobación del usuario previo a guardar. Ningún mensaje dispara directamente la creación de una tarea.

## Seguridad y limitaciones

- No interpreta ironías, referencias sin contexto ni todas las variantes de español; especialmente las referencias vagas «eso» sin un mensaje citado permanecen inciertas.
- No fusiona mensajes de distintos autores por simples coincidencias: reduce falsos positivos, aunque algunas repeticiones seguirán apareciendo.
- La deduplicación se limita a un contexto de 48 horas. Las recurrencias se deben confirmar por separado.
- La comparación es textual/semántica limitada y local; **no equivale a comprensión humana ni inteligencia de lenguaje de propósito general**.
- No modifica la base de datos, credenciales, permisos, historial guardado, notas adhesivas ni los cuatro iconos de navegación.

## Pruebas

`javac` y `java` ejecutan el corpus de 17 comprobaciones sintéticas más las 76 pruebas de conversación preexistentes. El CI recompila la APK y prueba la navegación en emulador. No se añaden conversaciones reales al repositorio.

Para futuras iteraciones se recomienda corpus anónimo etiquetado por intención, múltiples formas lingüísticas, métricas precisión/recobrado y confirmación de falsos positivos antes de automatizar nuevos tipos de relación.
