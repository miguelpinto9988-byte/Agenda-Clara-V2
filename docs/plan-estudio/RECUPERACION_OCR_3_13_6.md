# Agenda Clara 3.13.6 — Recuperación de corroboración de cursos OCR

## Defecto observado

El usuario informó que algunas fotos con materias repetidas, con una sola palabra o con distintos cursos que comparten el comienzo dejaban de mostrar las ventanas de corroboración.

Se compararon las fuentes verificadas 3.13.2 y 3.13.5. El motor OCR ya contenía en ambas una restricción que descartaba nombres genéricos como Historia, Educación o Investigación y fragmentos breves al comparar cursos. Además, descartaba algunos duplicados antes del diálogo de revisión. Por tanto, no hay evidencia para atribuir esas reglas exclusivamente a la modificación reciente del nombre de horario, aunque su efecto sí se aprecia en el flujo actual.

## Corrección aplicada

1. Reconocer **nombre truncado** (ej. Tendencias / Tendencias educativas) y **palabra inicial compartida** (Investigación / Investigación educativa o Investigación social).
2. No convertir una coincidencia inicial en unión automática: la pantalla explica que pueden ser cursos diferentes y muestra las dos asignaturas, con día y horario.
3. Al pulsar **«No, separados»**, seguir examinando otras coincidencias posibles del mismo fragmento; no excluir automáticamente el curso de todas las comparaciones.
4. Conservar las materias diferentes por nivel o grupo (Historia I != Historia II), y los horarios/días de las sesiones incluso al confirmar un nombre común.
5. No eliminar candidatos duplicados antes de la ventana de corroboración; retirar únicamente sesiones exactamente idénticas después de revisar.
6. Cuando una cuadrícula o una lectura OCR detecta repetición en el mismo bloque, incluir una advertencia específica y solicitar **corroboración de anomalías de la imagen** antes de solicitar el nombre del horario.
7. Hacer desplazable la ventana **«¿Son el mismo curso?»** para que se vean completos ambos nombres, los horarios y los botones de decisión.
8. Respetar el flujo **foto → corroborar cursos → revisar anomalías → confirmar nombre/categoría → guardar**. No se modifica la base de datos anterior ni se fusionan registros sin autorización.

## Regresiones realizadas

- Pruebas JVM de nombres parciales, primera palabra compartida, curso breve TIC, nombres iguales, materias numeradas, grupos distintos, dos candidatos que comienzan igual, negativa y revisión de la siguiente alternativa.
- Pruebas JVM geométricas con un horario sintético y un bloque OCR repetido.
- Preflight estático sobre fuentes verificadas 3.13.5, con comprobación del orden de diálogos y de que no se restauró el antiguo diálogo de nombre antes de la imagen.
- El resultado final de Android, la firma y la prueba de apertura corresponden a GitHub Actions; una prueba en emulador es insuficiente para confirmar la lectura OCR de todas las fotografías reales.

## Alcance y límites

La app sigue procesando el OCR localmente con ML Kit; sin la fotografía específica que presenta las anomalías no es posible garantizar su interpretación o el reconocimiento correcto de todas sus palabras. Las alertas para bloques que el OCR no entiende requieren que el usuario revise o corrija manualmente las materias; no se inventan nombres ni horas.

Rama: `fix/ocr-cursos-ambiguos-3-13-6-20261105`.


## Resultado técnico verificado

- QA de fuente y JVM, incluida detección de una palabra parcial, cursos con primera palabra compartida y bloques duplicados: **correcto**. Ejecución: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41961636784.
- Compilación de la APK `3.13.6` (`versionCode 62`), firma y paquete: **correcto**. APK de la ejecución: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41961746709/artifacts/13385826822.
- En la ejecución de compilación, la prueba de interfaz pasó, pero el trabajo completo quedó marcado en rojo porque buscaba cualquier línea `AndroidRuntime`, incluso registros normales de `uiautomator`. No se identificó una excepción fatal de Agenda Clara.
- Se corrigió la interpretación de esa prueba ejecutándola por separado, sin recompilar la APK: navegación real en Android 15 AOSP **exitosa**. Ejecución: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41962318724, capturas: https://github.com/miguelpinto9988-byte/Agenda-Clara-V2/actions/runs/41962318724/artifacts/13386041656.
- La lectura de una **fotografía real del usuario** y su diálogo de comprobación aún requieren un ejemplo específico; estos resultados validan reglas de matching, datos geométricos sintéticos y navegación en Android, no todas las fotografías posibles.
