# Agenda Clara 3.15.7 — Aprendizaje de variantes nuevas del OCR

## Objetivo

La versión 3.15.6 recordaba decisiones exactas entre dos nombres presentes en
una fotografía. Ahora, aunque aparezca **un solo nombre** nuevo, el lector puede
sugerir un nombre canónico aprendido anteriormente.

Ejemplo: previamente se confirmó «Tendencias» y «Tendencias educativas»
como «Tendencias educativas». En otra fotografía aparece únicamente
«Tendencas educativas». Se propone «Tendencias educativas» con la evidencia
de la corrección anterior; la persona debe pulsar **Sí · utilizar nombre**
para modificar las sesiones de esa nueva fotografía.

## Flujo

1. OCR local y limpieza conservadora de nombres duplicados (fases anteriores).
2. La pantalla de revisión lee una única vez las reglas privadas del dispositivo.
3. `ScheduleAdaptiveVariants.suggest` examina únicamente reglas **positivas**
   confirmadas, incluyendo el nombre corto, la variante larga y el canónico.
4. Si hay una coincidencia normalizada exacta o una **variación ortográfica
   pequeña de dos o más palabras**, propone un único destino. Un nombre corto
   de una sola palabra solo sirve si corresponde exactamente a una variante
   previamente confirmada.
5. Bloquea las sugerencias de grupos explícitos distintos, niveles I/II
   diferentes, parejas rechazadas y destinos canónicos en conflicto.
6. Muestra la evidencia: nombre leído, nombre propuesto y variante anterior.
   No renombra ni marca una clase desmarcada automáticamente.
7. **Aceptar:** corrige solo las sesiones con el mismo nombre OCR observado,
   conservando día, hora, aula y selección. **Rechazar:** conserva el nombre,
   oculta la propuesta durante esa importación y memoriza el rechazo únicamente
   si el horario se guarda después.
8. Tras guardar efectivamente el horario, la memoria existente registra la
   decisión aceptada o rechazada. Si se cancela la importación, no se aprende.

## Casos que deben pasar

- `Tendencas educativas` ⇒ propone `Tendencias educativas` tras haber
  confirmado el nombre original.
- `Tendencias tecnológicas` ⇒ **no** debe confundirse con
  `Tendencias educativas`.
- `Tutoría educativa` / `Investigación educativa` ⇒ nunca se igualan
  por compartir «educativa».
- `Historia I` / `Historia II` y `grupo 2` / `grupo 3` ⇒ sin
  normalización silenciosa.
- Una propuesta expresamente rechazada no vuelve a ofrecerse a partir de la
  misma pareja.
- Dos destinos canónicos igualmente respaldados ⇒ no se recomienda ninguno.

## Privacidad y límites

La mejora es **local y sin internet**; reutiliza la memoria `SharedPreferences`
existente de hasta 80 parejas confirmadas. No guarda fotografías ni sus
textos completos. No crea un modelo de visión artificial general, no aprende
de correcciones que no se hayan confirmado y no modifica horarios antiguos
al actualizar la APK.

La puntuación de similitud es una heurística léxica, **no una probabilidad
calibrada**. La prueba JVM `Phase88VariantTests.java` y la migración
`qa_variant_patch.py` deben pasar junto con la compilación y Android 15.
La precisión y la comodidad de la interfaz con fotografías reales deben
comprobarse aparte.
