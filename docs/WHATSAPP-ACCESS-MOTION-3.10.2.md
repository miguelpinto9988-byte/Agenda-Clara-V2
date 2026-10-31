# Agenda Clara 3.10.2 — Corrección de permisos e interfaz
La autorización se basa en el grupo que el usuario seleccionó expresamente, no en un indicador de pertenencia que puede quedar desactualizado. El componente nativo de WhatsApp sigue limitado al grupo autorizado y solicitado; los demás grupos no se revisan por esta solicitud.

Se impide que una segunda petición cambie de grupo mientras hay una descarga en curso y se amplía el periodo de espera de 45 a 240 segundos. Se comunica cuándo el historial ya estaba procesado y se informa cuando falta el mensaje de referencia para pedir mensajes anteriores.

Las animaciones pasan a una entrada de 200 ms y salida de 160 ms, con pestañas y menú + de 190 ms e interpolación de desaceleración. Se evita una petición de layout redundante.

Los scripts previos se conservan porque son parte del proceso reproducible; no se modifican los iconos de navegación ni los datos existentes.

Esta versión requiere pruebas en teléfono para confirmar el comportamiento específico de la conexión WhatsApp y el rendimiento de su hardware.