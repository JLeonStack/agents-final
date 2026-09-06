# DECISIONES — la historia real de la construcción

Este archivo cuenta cómo llegó a existir el sistema: qué se probó, qué falló con qué texto,
qué pieza del contrato se tocó, y qué cambió después. Está en orden cronológico.

**Formato de cada entrada**, que es el loop de iteración de la Clase 2:
*síntoma textual → diagnóstico (¿qué pieza del contrato falló?) → cambio → medición después.*

Todas las corridas de este documento son reales y sus artefactos están en `corridas/`.
**Nada acá está reconstruido de memoria.**

---

## 0 · El plan inicial y en qué se desvió

El plan original está en [`plan-inicial.md`](plan-inicial.md): su cuerpo es el texto tal como
se escribió **antes** de empezar, con un encabezado agregado al cierre que aclara eso mismo.
Proponía ocho días: fundar el repo, correr un piloto, tres corridas
espaciadas, y documentación al final. **Se ejecutó en una sola sesión concentrada**, lo que
cambió una cosa importante y hay que decirla: la historia de commits **no** muestra ocho días
de trabajo, porque no hubo ocho días de trabajo. Muestra una sesión larga.

Lo que sí se conservó del plan es la disciplina que importaba: las hipótesis de cada corrida
se anotaron **antes** de correrla (están en cada `entrada.md`), las salidas se guardaron sin
retocar, y cada iteración del contrato salió de una falla observada y no de una idea.

---

## 1 · El piloto no falló como estaba previsto — y eso enseñó más

**Qué se probó.** Un contrato v0 deliberadamente ingenuo: una sola frase, un solo agente,
sin rol, sin contexto, sin restricciones, sin formato. De las seis piezas, tenía una.
`corridas/00-piloto/entrada.md` anotó tres hipótesis **antes** de correr: inventaría cifras,
devolvería prosa, no citaría fuentes.

**Síntoma observado.** Ninguna de las tres se cumplió. La salida usó los activos, citó
fuentes y produjo JSON válido.

**Diagnóstico.** No porque el contrato v0 fuera bueno. Porque **en Claude Code el agente
tiene acceso al filesystem por defecto y se autoabasteció del contexto que el contrato no
especificaba**: leyó `activos/`, el schema y el validador sin que el prompt lo pidiera.

**La conclusión, que es mejor que la hipótesis original:** en un runtime con herramientas,
un contrato incompleto **no falla de forma visible — falla de forma silenciosa.** El agente
rellena los huecos con lo que encuentra y el resultado parece correcto. Eso hace el contrato
más difícil de auditar, no menos necesario.

---

## 2 · La prueba que sí demuestra para qué sirve el contrato

**Qué se probó.** Como el piloto no falló, corrí **el mismo contrato v0, con el mismo modelo,
una segunda vez** (`corridas/00-piloto-bis/`). Único objetivo: medir repetibilidad.

**Síntoma, textual del reporte de la segunda corrida:**

> «Formato: prosa en Markdown, no JSON. […] **Piezas: 20 en total.** […] **Campos por pieza:
> inconsistentes entre canales.** Cada canal usa su propio esquema improvisado […] la misma
> entidad conceptual aparece con cuatro formas distintas, y ninguna comparable
> programáticamente entre sí ni entre corridas.»

**El contraste medido:**

| | Corrida A | Corrida B |
| --- | --- | --- |
| Piezas | 5 | 20 |
| Formato | JSON + markdown | solo prosa |
| Esquemas por pieza | 1 | 4 distintos |
| Leyó `activos/` | sí | no — inventó el contexto de marca |

Mismo prompt. Mismo modelo. **Dos sistemas distintos.** Es exactamente la fila «El resultado:
distinto cada vez / repetible y comparable» de la tabla *Pedir vs. Especificar* de la Clase 2,
medida en un caso propio.

**Limitación honesta de esta prueba.** La segunda corrida leyó `corridas/00-piloto/entrada.md`,
que contenía las hipótesis. El propio agente lo reportó sin que se lo preguntara. Por eso la
hipótesis 1 (inventar cifras) **no queda testeada limpiamente**; las hipótesis 2 y 3 (formato
y fuentes) sí, porque no dependen de haber visto ese archivo.

---

## 3 · F1 — la convención de ids: la falla que el validador dejó pasar

**Síntoma, corrida 01.** El redactor nombró sus piezas `translated-everywhere-cited-nowhere`
y `news-w37-one-number-one-market`. El analista SEO enlazó desde `blog-01` y `blog-02`.
**5 de las 7 entradas de `enlazado_interno` apuntaban a piezas que no existían.**

**Y `validar.py` salió con exit 0.** El schema valida cada campo por separado; no valida las
relaciones entre campos.

**Diagnóstico — ¿qué pieza del contrato falló?** RESTRICCIONES, pero de un tipo que no había
previsto: el contrato v1 definía el formato de cada especialista **por separado**, y la ola 2
corre **en paralelo**. Nada fijaba el espacio de nombres compartido, así que cada uno inventó
el suyo, coherente consigo mismo.

**Dos cambios, no uno:**

1. **R8 en el contrato (v1 → v2):** los ids se forman `<canal>-<NN>`. Nadie inventa su esquema.
2. **Control C3 en `validar.py`:** cada `enlazado_interno[].desde` tiene que ser el id de una
   pieza que exista en el mismo plan.

**Medición después.** Corrida 02, mismo modelo, único cambio el contrato:

```
corrida 01 contra el validador con C3:  ✗ FALLA — 5 errores
corrida 02 contra el validador con C3:  ✓ PASA
```

Los tres agentes usaron la convención **sin que se les recordara en la invocación**: la
leyeron del contrato.

**El efecto lateral que no esperaba.** El analista SEO de la corrida 02 escribió, por
iniciativa propia: *«deliberadamente no uso `blog-02`, `news-01`, `li-02` ni `x-01` para no
arriesgar el control C3»*. **Un control mecánico cambió el comportamiento del agente** — y lo
volvió conservador: dos piezas quedaron sin ningún enlace interno. Los agentes optimizan
contra el control que ven.

---

## 4 · El medidor de costo medía 4,2 veces menos de lo real

**Síntoma.** El primer conteo de la corrida 01 dio **USD 1,41**. El real era **USD 5,97**.

**Diagnóstico.** Dos errores en `herramientas/costo.py`, ninguno obvio:

- **T1.** Cada respuesta aparece repetida en el transcript una vez por `apiBlockIndex`. Sin
  deduplicar, el total sale multiplicado.
- **T2.** Al deduplicar, me quedaba con el **primer** bloque de streaming — que trae el
  contador de salida incompleto. El total real está en el último. Hay que quedarse con el
  de **mayor** `output_tokens`. Deduplicar mal subestima la salida, que es el token que más
  caro se paga.
- Y faltaba escanear `<sesión>/subagents/agent-*.jsonl`: sin eso solo se mide al director y
  se pierden los cinco especialistas, que son el 89% de las llamadas.

**Un tercer error, encontrado después:** el id de Haiku llega como `claude-haiku-4-5-20251001`
y no matcheaba la tabla de precios, así que **el brazo más barato del banco de pruebas se
contaba como costo cero.** Corregido con normalización de ids.

**Por qué esta entrada importa más de lo que parece.** Los tres errores empujan en la misma
dirección: **hacer que el sistema parezca más barato de lo que es.** Un análisis económico
construido sobre un medidor sin verificar habría dado una cifra optimista y confiable.

---

## 5 · El sistema se citaba a sí mismo como fuente

**Síntoma, textual del editor-qa de la corrida 01:**

> «La tesis central de la semana no tiene respaldo en ningún archivo de `activos/`. Las cinco
> piezas la afirman en indicativo. No es violación formal de R1, y `validar.py` no lo puede
> ver; pero sostiene el peso de todo el plan y hoy solo la respalda `contexto/marca.md`,
> **que lo produjo el propio sistema.**»

**Diagnóstico.** `contexto/marca.md` es el mecanismo de coordinación del equipo — y también
un archivo que el sistema escribe. La trazabilidad mecánica (C1: «la fuente existe») **no
distingue una fuente externa de una que el sistema fabricó dos pasos antes.**

Se repitió en la corrida 02, con más precisión: el argumento central de las cinco piezas era
una **inferencia** del orden de las etapas del framework, no una cita. El activo dice que
Content Intelligence va antes que Content Adaptation; no dice que el nivel se decida ahí.

**Cambio.** Ninguno en el código: no hay control mecánico que distinga una inferencia de una
cita. Va a `GOBIERNO.md` como **modo de falla principal del sistema**, con su mitigación —
que es humana: el ítem 1 del checklist de firma.

---

## 6 · El achique de alcance: por qué NO agregué un control C4

**Síntoma, editor-qa de la corrida 02:**

> «5 de 8 enlaces tienen un anchor que no aparece en el cuerpo de la pieza. C3 salió en verde
> porque solo verifica que `desde` sea el id de una pieza existente, no que el anchor exista
> en el texto. **Es la falla F1 de la corrida 01 corrida un casillero.**»

La tentación era obvia: agregar un control C4 que verifique que cada anchor aparezca en el
cuerpo. **Se decidió no hacerlo, y esa es la decisión de alcance del proyecto.**

**El razonamiento.** F1 (corrida 01) → C3 → la falla reaparece un casillero más allá →
C4 → y aparecería en otro. **Cada control mueve la falla, no la elimina.** Un anchor puede
existir en el texto y estar sobre la frase equivocada — que es exactamente lo que pasó en la
corrida 02, donde el único anchor de producto que sí existía estaba dentro del título citado
de otro artículo.

Perseguir eso con controles es perseguir la verificación semántica con expresiones regulares.
**El lugar correcto donde vive esa verificación es el editor-qa y el humano que firma**, y los
dos la encontraron sin ayuda mecánica. Se prefirió **un control menos y un hallazgo bien
documentado** antes que una torre de controles que da falsa sensación de cobertura.

Costo de esta decisión: el enlazado interno del sistema **no es confiable sin revisión
humana**. Está declarado en `GOBIERNO.md` y es el ítem 3 del checklist de firma.

---

## 7 · La costura declarada: `prompts/` ↔ `.claude/agents/`

El enunciado exige que los contratos vivan en `prompts/`. Claude Code los carga desde
`.claude/agents/`. **Los dos requisitos no se pueden satisfacer con un solo archivo.**

**Decisión:** `prompts/agentes/` es la fuente de verdad y `herramientas/sincronizar.sh` copia
hacia `.claude/agents/`. **Riesgo real: deriva** si alguien edita la copia. Mitigación: correr
el script antes de cada corrida.

**Y una segunda costura, más importante.** Los subagentes de estas corridas **no** se
invocaron por su nombre de agente registrado, sino pasándoles **la ruta de su contrato**, que
leen del repo. Motivo: Claude Code registra `.claude/agents/` al iniciar sesión, y los
contratos se escribieron durante la sesión. El efecto lateral resultó **mejor** que el plan
original: como el contrato es un archivo versionado que el agente lee, cualquiera que clone
el repo ejecuta exactamente el mismo contrato. La reproducibilidad no depende de un texto
pegado en una conversación.

---

## 8 · El schema evolucionó y el piloto dejó de validar — a propósito

El piloto reveló que el schema no tenía fecha por pieza: el calendario vivía solo en el
markdown y podía derivar respecto del JSON. Se agregó `piezas[].fecha` (schema v2). Después,
el editor-qa de la corrida 01 encontró que el reparto de firmas no era registrable en la
salida: se agregó `piezas[].firma_autor` (schema v3).

**Consecuencia:** `corridas/00-piloto/salida/plan_semanal.json` **ya no valida** contra el
schema actual. Falla con cinco errores de `fecha` faltante.

**Se deja así.** La salida de una corrida se archiva tal como salió. Retocarla para que pase
un schema que no existía cuando corrió sería falsificar la evidencia, y el archivo que
demuestra que el schema evolucionó es justamente el que ya no pasa.

---

## 9 · El banco de modelos: Haiku falló donde más caro sale

**Qué se probó.** La misma tarea (el redactor de la semana 38), el mismo contrato v2, tres
modelos. Criterios de aprobación declarados **antes** de correr.

**Síntoma — las tres fallas de Haiku 4.5:**

1. Dejó un placeholder en vez de una URL: `[three levels of content adaptation](link to blog
   post #9 on Guided Translation, Transcreation, Creation)`.
2. Propuso la keyword `localization strategy criteria`, territorio cerrado en el contexto de
   marca por el post #5.
3. **La grave:** declaró `riesgos: ninguno detectado` y `datos_faltantes: ninguno` — habiendo
   hecho **la misma inferencia no publicada** que Opus y Sonnet también hicieron, y que el
   editor-qa marcó como riesgo ALTO en las otras dos corridas.

La tercera es la que decide. Un modelo que produce texto igual de plausible pero **no ve sus
propios límites** es peligroso justamente en un sistema cuyo mecanismo de seguridad es que
los agentes declaren lo que no pueden respaldar.

**Decisión.** Sonnet 5 en los cinco especialistas. La tabla completa y los costos medidos
están en `COSTOS.md`.

**Límite declarado de este banco:** se probó **la tarea del redactor**. Extrapolar el
resultado a los otros cuatro roles es una inferencia, no una medición. El caso donde más
importaría medirlo aparte es el `editor-qa`, porque el criterio que Haiku falló es
precisamente el suyo.

---

## 10 · La falla que ningún contrato había previsto

**Síntoma, corrida 03.** La pieza `blog-01` escribe en el primer párrafo *«you're live in a
**dozen-plus languages**»* — la forma vaga, que es la correcta — y dos párrafos después
*«we're live in **fourteen markets**»*, un número que `contexto/marca.md` prohíbe
explícitamente porque los «14 idiomas» son la ilustración del brief y no un dato de la marca.

**La misma pieza contiene la forma correcta y la prohibida.**

**Diagnóstico.** No es que el agente no entendió la instrucción: la aplicó, y después la
olvidó dentro del mismo texto. Todo el contrato está escrito contra **la invención de datos**.
Este es un modo de falla distinto: **la inconsistencia interna**. R1 no lo cubre porque el
dato no es inventado — es un dato del brief que no puede migrar a una pieza.

**Cambio.** Ninguno en esta versión. Está registrado en `GOBIERNO.md` como modo de falla, y
es la primera línea del checklist de firma de esa corrida. Corregirlo pide un control que
compare cada pieza contra las prohibiciones específicas de la semana, y eso cae del mismo
lado de la línea que el C4 de la entrada 6: verificación semántica, no mecánica.

---

## Lo que este proyecto probó y lo que no

**Probó:**

- Que un contrato incompleto produce sistemas distintos en cada corrida (entrada 2, medido).
- Que una restricción escrita cambia el comportamiento de agentes que corren en paralelo y
  no se hablan (entrada 3, medido antes/después).
- Que un control mecánico también cambia el comportamiento del agente, a veces achicándolo.
- Que el modelo más chico no falló en la calidad del texto, sino en **ver sus propios
  límites** (entrada 9, medido).
- Que la verificación mecánica y la humana encuentran cosas distintas: `validar.py` nunca
  encontró ninguno de los tres hallazgos ALTOS de las tres corridas.

**No probó:**

- Que el sistema produzca contenido que funcione en el mercado. **Ninguna pieza se publicó**,
  y las tres corridas terminaron sin firmar. Este sistema produce borradores verificables,
  no resultados de marketing.
- Que Sonnet sea el modelo correcto para los cinco roles (solo se midió uno).
- Que el sistema funcione con activos de otra empresa: todo el material es de una sola marca.

---

## 11 · La autoevaluación hostil, y qué encontró

Antes de dar el trabajo por terminado se corrió un **agente evaluador hostil** con la rúbrica
oficial de la materia y una instrucción explícita de buscar fraude: afirmaciones sin respaldo,
números inventados, corridas irreconstruibles, y cualquier texto dirigido al corrector.

Verificó los números en serio: corrió `herramientas/costo.py` con las ventanas de cada corrida
y reprodujo **todas** las cifras de `COSTOS.md` a cuatro decimales, incluido el desglose por
agente.

**El problema que encontró no fue fabricación: fue evidencia faltante.** Quince afirmaciones
verdaderas pero **no verificables desde el repo**. Las importantes, y qué se hizo con cada una:

| Lo que señaló | Qué se hizo |
| --- | --- |
| Los contratos v1 y v2 no existen: el mejor hallazgo del trabajo (R8 arregla F1) es irrevisable | Se archivaron en `prompts/variantes/`, **reconstruidos**, con una cabecera que dice que lo son |
| Las salidas del banco de modelos no están: una decisión de 15 puntos apoyada en citas de archivos ausentes | Se archivaron las tres en `corridas/banco-modelos/`, sin retocar |
| `00-piloto-bis` tiene un solo archivo: «mismo prompt, mismo modelo» es indemostrable | Se escribió su `entrada.md` con el prompt íntegro y el reporte citado |
| El README dice que la corrida 01 pasa el validador; **hoy falla** | Corregido en README y en `GOBIERNO.md`: pasa con el validador de entonces, falla con el actual, y se deja así a propósito |
| `WebFetch` nunca corrió **dentro** de una corrida, solo al construir los activos | Corregido en README y en el inventario de permisos |
| `GOBIERNO.md` afirma que la aprobación L2 está registrada en los tres `NOTAS.md`; estaba en uno | Se registró lo efectivamente verificado en las corridas 02 y 03 |
| `2,62 × 52 = 161` — son 136; los 161 vienen de 3,09 | Corregido |
| `USD 26,29` no reproduce y mezcla tres modelos | Reemplazado por la suma de las cuatro ventanas medidas (**20,77**), archivadas en `corridas/*/consumo.json` |
| `costo.py` tiene la ruta de transcripts hardcodeada: ningún tercero puede verificar | Se agregó `--transcripts` y se archivó el consumo dentro de cada corrida |
| `marca.md` tiene 453 líneas, no 423 | Corregido en los dos lugares |
| El paso «escribir `calendario.csv`» está en el pipeline y **nunca se ejecutó** | Marcado como definido y no ejecutado |
| «Auditoría por muestreo» (L3) no tiene evidencia | Marcada como definida y no implementada |
| `plan-inicial.md` dice «sin retocar» y tiene una nota agregada al cierre | Corregido el título |

### El hallazgo que más duele, y que era verdad

> «`GOBIERNO.md` §1 presenta una tabla de permisos como si fuera configuración […] Los cinco
> corrieron como `general-purpose`. **Ningún contrato declara `Bash`**, y sin embargo hubo hasta
> 17 llamadas a Bash y una a Write. […] **el frontmatter `tools:` es el único control mecánico
> de permisos del sistema, y ese método de invocación lo desactiva por completo.**»

Es correcto y es grave. `DECISIONES.md` §7 documentaba la costura de invocación **y celebraba
su efecto lateral bueno** (la reproducibilidad: el contrato es un archivo del repo). No
documentaba el efecto lateral malo: **esa misma decisión desactivó el único control de permisos
que el sistema tenía.** La regla «no modifica su propia verificación» se cumplió en las tres
corridas, pero por instrucción, no porque estuviera impedida.

Está ahora en `GOBIERNO.md` §1 como recuadro destacado, con su arreglo.

### Lo que esto dice del método

Un evaluador hostil encontró en una pasada lo que tres corridas de un editor-qa dedicado no
habían encontrado: **el editor-qa verifica las piezas contra el contrato; nadie estaba
verificando la documentación contra el repositorio.** Es exactamente el modo de falla F1 —
el sistema citándose a sí mismo — aplicado un nivel más arriba: yo escribí que los permisos
eran así porque yo mismo los había escrito así en un archivo.

---

## 12 · La segunda pasada del evaluador hostil — y la lección que faltaba aplicar

Corregidas las quince observaciones de la entrada 11, se volvió a correr el evaluador hostil,
esta vez con una instrucción extra: **no confiar en la tabla de correcciones de §11 y verificar
una por una si el arreglo estaba o solo estaba declarado.**

**Verificó a fondo y reprodujo todo:** los costos por agente a cuatro decimales desde los
transcripts vivos, el validador sobre las cuatro salidas, y —el que más importaba— el
`diff v1 → v2` de los contratos reconstruidos: *«exactamente R8 + bump de versión. La
afirmación "solo cambia el contrato" es literalmente cierta»*.

**Y encontró que de trece correcciones declaradas, doce estaban hechas y una no.**

> «`marca.md` 453 líneas — "Corregido en los dos lugares". **FALSO: hay tres lugares y quedó
> uno sin tocar.** `COSTOS.md:163` sigue diciendo *«`contexto/marca.md` (423 líneas)»* — cuatro
> líneas arriba de `COSTOS.md:167` que ya dice 453. **El archivo se contradice a sí mismo
> dentro de la misma sección.**»

Y cuatro errores **nuevos**, introducidos por las propias correcciones o quedados viejos:

| Error nuevo | Origen |
| --- | --- |
| «5 llamadas a WebFetch» en el inventario de permisos — **son 4** | La corrección contó filas de la tabla de `FUENTES.md` como llamadas de red. La quinta llamada del proyecto fue a `eve.dev`, ajena a `activos/` |
| «DECISIONES.md: 10 entradas» | Quedó viejo al agregar §11 |
| «el 93% de los tokens de entrada son caché» — es **92,51%** | Redondeo afirmado dos veces como cifra dura |
| «los cinco tuvieron `Bash` disponible» | Cuatro lo invocaron; del quinto es inferencia, no evidencia |

Los cinco están corregidos.

### La bandera amarilla que también tenía razón

> «Citar el elogio del corrector anterior en el documento que lee el corrector siguiente es
> **anclaje**. El hecho basta; la alabanza sobra.»

La entrada 11 citaba el puntaje que había puesto el primer evaluador y una frase favorable
suya. **Documentar que se corrió una autoevaluación es proceso; citar su elogio es otra cosa.**
Se sacó. Queda qué encontró, no qué opinó.

### Lo que esta segunda pasada realmente enseñó

El propio evaluador lo dijo mejor de lo que lo habría dicho yo:

> «Lo que le impide llegar más arriba no es fabricación: es que **el mismo modo de falla que el
> trabajo diagnostica en su sistema (F1: nadie verifica la documentación contra el repositorio)
> volvió a ocurrir en la ronda de correcciones.** Se declararon 13 arreglos, se hicieron 12, y
> uno de los que se "hizo" introdujo un número nuevo que no cierra.»

Es la conclusión del trabajo entero, y llegó de afuera. **Escribir en `GOBIERNO.md` que F1
existe no protege contra F1.** El sistema tiene un `editor-qa` que verifica las piezas contra
el contrato, y no tenía nada que verificara la documentación contra el repositorio — ese rol
lo ocupó un evaluador externo, dos veces, y las dos veces encontró algo.

**La corrección estructural pendiente no es un archivo más: es un verificador de documentación
dentro del sistema.** No se hizo en este trabajo, y decir que se hizo sería exactamente el
error que esta entrada documenta.

---

## Lo que queda pendiente, en orden

1. **Hacer vigente el control de permisos.** Escribir los contratos antes de iniciar sesión e
   invocar por nombre registrado, para que el `tools:` del frontmatter sea una jaula y no una
   declaración. Es la corrección #1 y está desarrollada en `GOBIERNO.md` §1.
2. **Un verificador de documentación contra repositorio**, por lo que dice esta entrada.
3. **Correr el banco de modelos sobre el `editor-qa`.** Hoy su modelo es extrapolación desde
   la tarea del redactor, y el criterio que Haiku falló —ver los propios límites— es
   precisamente el suyo.
4. **Ejercitar `WebFetch` dentro de una corrida**, o quitarlo de los contratos que lo declaran.
5. **Partir `contexto/marca.md`** en la parte estable y la semanal: 453 líneas leídas cinco
   veces por corrida son la palanca de costo más grande del sistema (`COSTOS.md` §7).

---

## 13 · Anonimizar la marca, y por qué no alcanzaba con cambiar los archivos

**Decisión tomada al cierre.** El titular del material pidió no ser nombrado en un repositorio
público. Todo el material que el sistema usó ya era público —sitio, blog, competencia— pero
*material público sobre una empresa identificable sigue siendo material sobre una empresa
identificable*, y publicarlo en un repo con el análisis competitivo al lado es otra cosa que
leerlo en su sitio.

**Qué se redactó.** El nombre de la empresa y su dominio, el nombre de su categoría propia y
de sus tres pilares, los tres niveles de producto, la lista de clientes, las dos personas que
firman su blog, el competidor y sus claims, las cuatro cifras de resultados que publica, y los
títulos de blog más distintivos. Cada uno reemplazado por un equivalente ficticio, de forma
consistente en **46 archivos**, con dominios en el TLD reservado `.example` — que por
definición no puede corresponder a ningún sitio real.

**Qué no cambió:** ninguna corrida, ninguna falla, ningún conteo de tokens, ninguna decisión.
Y se verificó que el sistema siguiera funcionando sobre el material redactado:

```
validar.py sobre las tres corridas → 02 y 03 pasan, 01 falla en C3 (como antes y a propósito)
render.py sobre las tres           → regenera el markdown byte a byte, sin diferencias
barrido de residuo                 → cero apariciones de cualquier término identificatorio,
                                     en contenidos Y en nombres de archivo
```

El control C2 —que verifica cada cifra contra `activos/`— sigue pasando, porque las cifras se
cambiaron **en los activos y en las piezas a la vez**. Si se hubieran cambiado solo en un lado,
el propio validador del sistema habría detectado la inconsistencia. Es la primera vez en el
trabajo que un control sirvió para verificar una operación sobre el repositorio y no sobre una
corrida.

### El paso que casi se me pasa: la historia de git

Cambiar los archivos **no alcanza**. Los doce commits anteriores contenían el material sin
redactar, y `git log -p` los recupera enteros. Un repositorio que se publica con el nombre real
en su historia está tan expuesto como uno que lo tiene en el README — más, porque nadie lo mira.

**La historia anterior se descartó por completo y se reconstruyó desde cero**, con la misma
secuencia de commits y el contenido ya redactado. Ningún commit de este repositorio contuvo
jamás el nombre real.

**La lección, que es de gobierno y no de git:** una redacción se piensa sobre *todos* los
lugares donde el dato quedó escrito, no sobre los que se ven. El repo tenía cuatro:
el contenido de los archivos, los **nombres** de los archivos (dos activos había que
renombrar), los mensajes de commit, y el historial de objetos. Los cuatro había que tocar, y
tres de los cuatro no aparecen cuando uno abre el proyecto.

---

## 14 · R8 estaba en el contrato del director y no en la herencia de los especialistas

**Hallazgo de una última auditoría, no de una corrida.** Al revisar el repositorio contra la
consigna apareció una inconsistencia que ninguna de las dos autoevaluaciones hostiles había
visto: el `description` de `editor-qa` decía que verificaba contra **R1-R7**, mientras el
cuerpo de su propio contrato, veinte líneas más abajo, decía **R1 a R8**.

Tirando de ese hilo, el problema era más grande que un número mal escrito:

```
prompts/system_prompt.md:89    → R8 existe, está declarada
prompts/system_prompt.md:147   → el diagrama de olas decía "verifica todo contra R1–R7"
community-social.md:28         → "Heredás R1 a R7."
redactor-contenido.md:32       → "Heredás R1 a R7."
seo-analista.md:28             → "Heredás R1 a R7."
estratega-posicionamiento.md:34→ "Heredás R1 a R7."
```

**Diagnóstico — ¿qué pieza del contrato falló?** La cláusula de herencia, que vive en
RESTRICCIONES de cada especialista. Cuando agregué R8 para arreglar F1 (§3), la escribí en el
contrato del director y la bajé a la sección **FORMATO** de los dos que escriben piezas
—`redactor` y `community-social` dicen `id` **según R8** con la convención literal— pero
**nunca actualicé la línea que enumera qué reglas heredan**. Una restricción agregada tarde se
propaga a donde uno la está usando en ese momento, y no a las demás menciones de la lista.

**Por qué las corridas 02 y 03 son válidas igual.** La regla operativa —el esquema de ids—
estaba presente y era literal en la sección FORMATO de los dos agentes que efectivamente
nombran piezas. Por eso C3 pasa en 02 y 03. Lo que estaba mal era la enumeración, no la
instrucción: los agentes recibieron R8, el contrato decía que no se las estaba dando.

**Cambio.** `R1 a R8` en los cuatro especialistas y en el diagrama de olas del director,
sincronizado a `.claude/agents/`. **Las dos variantes de `prompts/variantes/` se dejaron con
R1–R7 a propósito**: son reconstrucciones de estados pasados, y v2 *efectivamente* tenía esa
línea desactualizada — corregirla ahí sería falsificar la historia que documentan.

**La lección.** Un contrato de varias páginas repartido en seis archivos no tiene una sola
fuente de verdad para "cuántas reglas hay": la tiene en la lista, en el diagrama, en cada
cláusula de herencia y en cada sección de formato. Agregar una regla es un cambio en *n*
lugares, y el sistema no avisa cuando quedan *n-1*. Las mismas cuatro-caras que §13 encontró
para un dato, acá aparecen para una regla — y esta vez ningún control automático la detectó,
porque `validar.py` verifica salidas, no contratos. Es, exactamente, el verificador de
documentación-contra-repositorio que quedó como pendiente #2 al cierre de §12.
