# Fase 22 — Catálogo de iconos de cursos

**Alcance:** 40 conceptos de asignatura propuestos, incluyendo una alternativa universal. **Son especificaciones; ningún PNG está generado.** El catálogo se entrega además como CSV para la producción futura.

Los cursos registrados admiten nombres arbitrarios. Este catálogo representa familias semánticas, no un listado obligatorio de nombres: un curso desconocido utiliza ic_subject_general.png. El nombre, las sesiones, la categoría, el color y los vínculos con tareas nunca se modificarán por elegir un dibujo.

| Clave | Materias representadas | Motivo visual | Prioridad |
|---|---|---|---|
| general | Cualquier curso sin equivalencia segura | Libro abierto con marcador violeta | P0 |
| tendencias_educativas | Tendencias educativas (E); Innovación educativa | Libro con flecha ascendente y destellos | P0 |
| pedagogia | Pedagogía; Fundamentos pedagógicos; Psicopedagogía | Libro y manzana, estilo académico | P0 |
| psicologia | Psicología; Psicología del aprendizaje | Cerebro suave y burbuja | P0 |
| investigacion | Metodología de investigación; Investigación educativa | Lupa sobre documento y gráfica | P0 |
| tecnologia_educativa | TIC educativas; Tecnología educativa | Tableta y libro con destello | P0 |
| matematicas | Matemáticas; Álgebra; Geometría | Regla, compás y símbolos geométricos sin texto | P0 |
| comunicacion | Comunicación; Lengua; Comunicación oral | Libro y burbuja de diálogo | P0 |
| ciencias | Ciencia; Ciencias naturales | Átomo colorido y hojas | P0 |
| historia | Historia; Historia universal | Rollo antiguo con reloj discreto | P0 |
| biologia | Biología; Ciencias de la vida | Microscopio con hoja | P0 |
| quimica | Química; Química general | Frascos de laboratorio con burbujas | P0 |
| fisica | Física; Mecánica | Péndulo estilizado y átomo | P0 |
| ingles | Inglés; English; Idiomas | Libro con globo terráqueo | P0 |
| programacion | Programación; Desarrollo de software | Pantalla con símbolos de código sin letras pequeñas | P0 |
| arte | Arte; Artes visuales | Paleta y pincel redondeados | P0 |
| geografia | Geografía; Cartografía | Globo terráqueo y brújula | P1 |
| economia | Economía; Microeconomía | Gráfica ascendente y monedas | P1 |
| filosofia | Filosofía; Pensamiento crítico | Busto clásico y foco | P1 |
| literatura | Literatura; Literatura universal | Libro de cubierta y pluma | P1 |
| lectura | Comprensión lectora; Taller de lectura | Libro abierto con lupa | P1 |
| escritura | Redacción; Escritura académica | Lápiz y cuaderno | P1 |
| educacion_fisica | Educación física; Actividad física | Zapatilla deportiva y cronómetro | P1 |
| didactica | Didáctica; Estrategias de enseñanza | Pizarra pequeña y puntero | P1 |
| evaluacion_educativa | Evaluación de aprendizajes; Medición educativa | Rúbrica visual y sello de aprobación | P1 |
| educacion_inclusiva | Educación inclusiva; Atención a la diversidad | Libro y círculo de personas | P1 |
| sociologia | Sociología; Sociedad y cultura | Tres siluetas conectadas | P1 |
| estadistica | Estadística; Probabilidad; Análisis de datos | Barras y gráfico de distribución | P1 |
| robotica | Robótica; Automatización | Robot académico compacto | P1 |
| diseno | Diseño; Diseño gráfico; Diseño digital | Lápiz óptico y formas cromáticas | P1 |
| administracion | Administración; Gestión empresarial | Maletín y engranaje | P1 |
| contabilidad | Contabilidad; Finanzas contables | Calculadora y hoja de balance | P1 |
| derecho | Derecho; Legislación | Balanza de justicia | P2 |
| ciencias_salud | Salud; Enfermería; Medicina básica | Estetoscopio y cruz de salud sin logo | P2 |
| marketing | Marketing; Publicidad | Megáfono y gráfico ascendente | P2 |
| musica | Música; Educación musical | Notas musicales y auriculares sin texto | P2 |
| fotografia | Fotografía; Imagen digital | Cámara compacta y destello | P2 |
| deporte | Deportes; Entrenamiento | Balón deportivo y medalla | P2 |
| emprendimiento | Emprendimiento; Innovación de negocios | Bombilla y cohete pequeño | P2 |
| ingenieria | Ingeniería; Tecnología industrial | Engranaje y casco técnico | P2 |

## Pautas de clasificación para la fase 26 (NO implementadas)

1. Priorizar icono manual asignado por el usuario.
2. Si no hay elección manual, sugerir mediante el nombre completo y palabras clave inequívocas; no aplicar similitud borrosa. La frase «TENDENCIAS EDUCATIVAS (E)» corresponde al concepto tendencias_educativas; la abreviatura «(E)» permanece en el nombre.
3. Evaluar conceptos específicos antes de genéricos: «tecnología educativa» no debe caer en tecnología general, y «ciencias de la salud» no debe caer automáticamente en ciencias naturales.
4. No asumir que «Proyecto», «Taller», «Laboratorio» o «Examen» sean materias: estos conceptos se registran como modalidades/tipos de actividad en fase 23.
5. En caso de ambigüedad o curso libre sin coincidencia, utilizar ic_subject_general.png y permitir elección posterior.

## Criterios para producir los iconos en fase 24

- P0: primero el icono genérico, Tendencias educativas y las materias representadas en uso frecuente.
- P1: ampliar cobertura de asignaturas educativas, humanidades y profesiones.
- P2: enriquecer especialidades sin ralentizar la publicación de la colección principal.
- Cada concepto tendrá un maestro 1024×1024 PNG RGBA y una exportación Android optimizada 256×256 solo cuando la fase 24 sea aprobada.
- La previsualización del sistema 3D debe aprobarse antes de generar los 39 iconos específicos de este catálogo.
