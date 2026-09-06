# Equipo de agentes de marketing — Acme

**Trabajo final · Programación de y con Agentes de IA · MBA UCEMA · 2026 2T**
**Autor:** Julián De León · **Caso:** [acme-multilingual.example](https://www.acme-multilingual.example/), empresa
de marketing de contenido multilingüe.

---

> ### Nota de anonimización — leer antes que nada
>
> **«Acme Multilingual» es un seudónimo.** El caso es una empresa real de marketing de
> contenido multilingüe, y el sistema corrió de verdad sobre **su material público real**:
> su sitio, su blog y el sitio de un competidor, extraídos con `WebFetch` el 2026-09-05.
>
> Antes de publicar este repositorio se **redactaron los identificadores**: el nombre de la
> empresa y su dominio, el nombre de su categoría propia y de sus productos, los nombres de
> sus clientes, los de las dos personas que firman su blog, el del competidor, y las cifras
> de resultados que publica. Cada uno se reemplazó por un equivalente ficticio, de forma
> **consistente en todo el repositorio**, de modo que la estructura del caso, el
> comportamiento del sistema y todos sus controles siguen siendo exactamente los mismos:
> el control C2 sigue verificando cada cifra contra los activos, y sigue pasando.
>
> **Lo que no cambió:** ninguna corrida, ninguna falla, ningún conteo de tokens, ninguna
> decisión. Los dominios usados terminan en `.example`, un TLD reservado que no puede
> corresponder a ningún sitio real.
>
> El motivo es la propia regla de este trabajo, en `GOBIERNO.md`: *al repo público solo entra
> material que ya es público* — y el titular del material pidió no ser nombrado.

---

## Qué construí

Un equipo de **seis agentes** —un director y cinco especialistas— que produce el plan de
contenidos semanal de una marca real. Lee material público de la empresa y de su competencia,
fija un ángulo editorial, escribe las piezas de blog y redes, arma el plan de SEO, y
**verifica su propio trabajo** antes de entregar. Sirve para quien tiene que sostener un
calendario editorial semanal y hoy lo hace a mano: le devuelve borradores trazables y una
lista corta de decisiones que un humano tiene que tomar. **No publica nada, nunca.**

### Si lo querés correr, no leas esto: leé [`OPERACION.md`](OPERACION.md)

Este README explica **qué es** el sistema y qué falló al construirlo.
[`OPERACION.md`](OPERACION.md) es el runbook: requisitos, los pasos de una corrida de punta a punta, los
prompts exactos que se pegan, y qué hacer cuando algo se rompe. El primer paso no gasta un
token y responde si el repositorio está sano:

```bash
python3 herramientas/verificar-repo.py
```

Trece controles del repositorio **contra su propia documentación** — contratos sincronizados,
R1–R8 coherente en los seis, las tres corridas completas y reconstruibles byte a byte, la jaula
de permisos cargada y sincronizada, cero enlaces rotos y **ningún dato que viva solo en una
carpeta oculta**. Exit 1 si algo no cierra, y dice qué. Una corrida completa
cuesta **≈ USD 3,12** —2,62 medidos, 0,50 proyectados; el desglose en
[`COSTOS.md`](COSTOS.md) §6— y tarda unos 35 minutos, de los cuales 10 son de la persona que
revisa y firma.

---

## Cómo se lo pedí

### 1 · El primer intento, que es el que todos escribimos

```
Sos un equipo de marketing de contenidos. Armame el plan de contenidos de la semana
para Acme, una empresa de marketing de contenido multilingüe. Que incluya
posts de blog y de redes sociales.
```

Tiene la **tarea** y ninguna de las otras cinco piezas. Corrida dos veces con el mismo modelo
dio dos sistemas distintos: 5 piezas con JSON una vez, 20 piezas en prosa con cuatro esquemas
distintos la otra. Está en [`corridas/00-piloto/`](corridas/00-piloto/) y
[`corridas/00-piloto-bis/`](corridas/00-piloto-bis/).

### 2 · El contrato del director — las seis piezas

El contrato completo está en [`prompts/system_prompt.md`](prompts/system_prompt.md), con las
seis piezas rotuladas: **ROL · CONTEXTO · TAREA · RESTRICCIONES · FORMATO · EJEMPLOS**. El
corazón son las restricciones, que se numeran para poder citarlas en cada revisión:

```
R1 · Cero cifras inventadas. Está prohibido afirmar una cifra, fecha o resultado que no
     esté literalmente en un archivo de activos/. Si hace falta un dato que no está,
     escribí [DATO FALTANTE: qué se necesita] y registralo.
R2 · Toda pieza declara sus fuentes: las rutas a los archivos que la respaldan.
R3 · Nunca publicás. El sistema no tiene permiso de publicación en ningún canal.
R4 · Nada del competidor. Ese archivo se lee para diferenciarse, no para inspirarse.
R5 · Un solo pilar por pieza. Una pieza que cuelga de los tres no cuelga de ninguno.
R6 · No repetir la semana anterior. Leé el calendario editorial.
R7 · Salida en formato estricto: un JSON que valida contra el schema.
R8 · Convención de ids compartida (blog-01, li-01, x-01). Nadie inventa su propio esquema.
```

**R8 no estaba en la versión 1.** Se agregó después de una falla concreta, y esa historia es
la entrada §3 de [`DECISIONES.md`](DECISIONES.md). Los contratos v1 y v2 están archivados en
[`prompts/variantes/`](prompts/variantes/) para que el antes/después se pueda auditar.

### 3 · El brief semanal — lo que cambia en cada corrida

Plantilla completa en [`prompts/user_prompt.md`](prompts/user_prompt.md):

```
Armá el plan de contenidos para la semana <SEMANA ISO> (<RANGO DE FECHAS>).

CONTEXTO DE ESTA SEMANA
  Disparador:        <qué hecho real justifica hablar de esto ahora>
  Público objetivo:  <a quién le hablamos, con cargo y problema>
  Objetivo:          <qué queremos que pase — demanda, autoridad, activación>
  CTA:               <la url exacta a la que mandamos>
  Pilar sugerido:    <InSpeech | InContext | InRegion | que lo elija el estratega>

RESTRICCIONES DE ESTA SEMANA
  <cualquier límite propio de la semana>

ENTREGA
  Escribí corridas/<ID>/salida/plan_semanal.json y corridas/<ID>/salida/plan.md.
  Corré python3 herramientas/validar.py sobre el JSON antes de terminar.
  Si el validador falla, arreglá el JSON — no toques el validador ni el schema.
```

### 4 · Cómo se invoca a cada especialista — textual

Los cinco contratos de especialista están en [`prompts/agentes/`](prompts/agentes/), cada uno
con sus propias seis piezas. **A ninguno se le pega el contrato en el mensaje**: el contrato es
un archivo versionado del repositorio y el agente lo lee de ahí.

**Así se invocó en las tres corridas archivadas** — pasándole la ruta:

```
Trabajás en el repositorio actual. Tu contrato está en archivos versionados del repo,
no en este mensaje.

PASO 1 — leé, completos: `prompts/system_prompt.md` (contrato del director v3,
restricciones R1-R8) y `prompts/agentes/redactor-contenido.md` (TU contrato).

PASO 2 — leé `contexto/marca.md` fresco y completo. Ahí está el ángulo de la semana,
ya aprobado. Leé después los activos que necesites para respaldar afirmaciones.

PASO 3 — ejecutá tu tarea para la semana 2026-W39. CTA: <url>

LÍMITES: NO escribas archivos. NO leás `corridas/`. Devolveme exactamente los campos
que tu contrato pide en su sección FORMATO.
```

Eso tiene una consecuencia buena que no había previsto: **cualquiera que clone el repo ejecuta
exactamente los mismos contratos**, porque son archivos versionados y no texto pegado en una
conversación. Y una mala, que descubrí tarde: pasarle la ruta lo ejecuta como **agente
genérico**, y el `tools:` que su contrato declara no se le aplica.

**Así se invoca ahora** — por su **nombre registrado**, que es lo que hace que el `tools:` del
frontmatter sea una jaula y no una declaración:

```
Invocá a cada especialista POR SU NOMBRE REGISTRADO — estratega-posicionamiento,
redactor-contenido, community-social, seo-analista, editor-qa — y no pegándole su
contrato ni su ruta en el mensaje.
```

El prompt completo del director está en [`OPERACION.md`](OPERACION.md) paso 3. El cambio se
pudo hacer por una razón tonta y decisiva: **los contratos ahora existen antes de que empiece
la sesión.** Cuando se construyó el sistema se escribían durante la sesión, y por eso no había
nada registrado que invocar.

### 5 · El orden de trabajo — tres olas

```
OLA 1   estratega-posicionamiento   → fija el ángulo y escribe contexto/marca.md
                                       ⏸ acá reviso yo antes de seguir (L2)
OLA 2   redactor-contenido  ┐
        community-social    ├─ en paralelo, los tres leen contexto/marca.md
        seo-analista        ┘
OLA 3   editor-qa                   → verifica todo contra R1-R8
        director                    → consolida en JSON + markdown
                                       ✍️ FIRMA HUMANA
```

Los tres de la ola 2 **corren en paralelo y no se hablan**. Se coordinan por un archivo
compartido, no por conversación. Ese detalle explica la mitad de las fallas del trabajo.

---

## Qué funciona

### Corrió tres veces con briefs reales distintos

| # | Semana | Contrato | Modelo | Validador | Firma | Costo |
|---|---|---|---|:---:|:---:|---:|
| [01](corridas/01-2026-09-05-w37/) | W37 · descubribilidad en respuestas de IA | v1 | Opus 5 | ✓ con el de entonces · **✗ con el actual** | **no** | 6,10 |
| [02](corridas/02-2026-09-05-w38/) | W38 · criterio de asignación por mercado | **v2** | Opus 5 | ✓ exit 0 | **no** | 7,70 |
| [03](corridas/03-2026-09-05-w39/) | W39 · cómo se argumenta la inversión | **v3** | **Sonnet 5** | ✓ exit 0 | **no** | 4,04 |

Cada corrida tiene su `entrada.md` con el brief exacto, la salida **sin retocar**, `NOTAS.md`
con el contraste contra las hipótesis anotadas *antes* de correr, `FIRMA.md` y el consumo
medido. **La corrida 01 falla contra el validador actual a propósito**: el control que la
detecta se agregó justamente por lo que esa corrida reveló, y su salida se archiva como salió.

### La salida es estructurada porque hay un proceso que falla

```bash
python3 herramientas/validar.py corridas/03-2026-09-05-w39/salida/plan_semanal.json
```

Sale con **exit 1** si no cumple. Tres controles: **C1** trazabilidad (las fuentes declaradas
existen), **C2** antialucinación (toda cifra con % aparece literal en `activos/`), **C3**
integridad referencial (los enlaces internos apuntan a piezas que existen).

```bash
python3 herramientas/verificar-repo.py                                   # 13 controles del repo
python3 herramientas/render.py  corridas/<id>/salida/plan_semanal.json   # genera plan.md del JSON
python3 herramientas/costo.py --desde <inicio> --hasta <fin>             # tokens y costo reales
bash herramientas/sincronizar.sh                                         # prompts/agentes/ y jaula/ → .claude/
bash herramientas/nueva-corrida.sh 2026-W40 <desde> <hasta>              # abre una corrida
bash herramientas/cerrar-corrida.sh corridas/<id>                        # valida, mide y cierra
```

`cerrar-corrida.sh` mide, valida, regenera el markdown y **deja `FIRMA.md` y `NOTAS.md` en
blanco a propósito**: termina imprimiendo las tres cosas que ningún script puede hacer.
Automatizar hasta el borde de la firma y frenar ahí es la línea del sistema.

### La supervisión está definida, no declamada

| Paso | Nivel | Quién firma |
|---|---|---|
| Leer `activos/`, fetch del sitio y del competidor | **L3** ejecutar y avisar | Auditoría por muestreo — *definida, no implementada* |
| Actualizar `contexto/marca.md` | **L2** | Yo apruebo antes de que la ola 2 lo lea |
| Redactar las piezas | **L2** | Yo reviso pieza por pieza |
| Control de calidad (`editor-qa`) | **L3** | Su salida es el insumo de mi revisión |
| **Publicar en cualquier canal** | **L0 — el agente no publica** | Yo, siempre |

`firma.requiere_firma_humana` es `const: true` en el schema: **una salida sin firma humana es
inválida por construcción**, no por convención.

### La economía cierra y está medida

**Construir: USD 21,23** (suma de las cuatro ventanas de corrida, archivadas en cada
`consumo.json`). **Operar: ≈ USD 3,12 por corrida** en configuración de producción, y **3,12 ×
52 = 162,08 ≈ USD 162 al año** para una marca. La proyección se hace sobre la corrida completa,
no sobre los especialistas solos.

Ese 3,12 **no es todo medido, y la diferencia importa**: 2,62 son la medición real de los cinco
especialistas en Sonnet 5, y 0,50 es el director *proyectado* a Sonnet desde su costo real en
Opus (USD 1,43) con el ratio Opus/Sonnet medido en el banco sobre la misma tarea (2,853). Todavía
no hubo una corrida con el director en Sonnet. Los precios están citados con fuente y fecha en
[`COSTOS.md`](COSTOS.md) §2 —la tabla de precios de la API de Anthropic consultada el
2026-09-06— junto con el banco de tres modelos y las **cuatro** trampas de medición que hubo que
corregir, la última de las cuales era un supuesto de tarifa que resultó ser medible.

### La prueba de estrés que sí pasó

El brief de la corrida 03 empujaba deliberadamente hacia *«growth engine»* — que es el titular
del competidor **y** una frase del propio sitio de Acme. **Ninguna de las cinco piezas
la usó.** Ningún agente supo que estaba siendo probado.

---

## Qué falta o qué falló

### La tabla de permisos que escribí no estuvo vigente en ninguna de las tres corridas

Es lo más serio que encontré, y lo encontré tarde. `GOBIERNO.md` presentaba una tabla de
permisos como si fuera configuración. **No lo era.** El único control mecánico de permisos era
el `tools:` del frontmatter de cada contrato —`redactor-contenido.md` declara
`tools: Read, Glob, Grep`— y ese control **solo se aplica si el agente se invoca por su nombre
registrado**. Yo los invoqué pasando la ruta del contrato, que los ejecuta como agentes
genéricos.

Inspeccioné los transcripts de la corrida 03: **cuatro de los cinco usaron `Bash`** —uno lo
llamó 17 veces— y ninguno de los cinco contratos lo declara. La regla «no modifica su propia
verificación» se cumplió en las tres corridas, pero **por instrucción, no porque estuviera
impedida**.

**Después de las tres corridas se puso la jaula de verdad**, y la prueba no es que esté
escrita: es que **bloqueó a la sesión que la escribía**. Al crear
`herramientas/verificar-repo.py` la herramienta `Write` fue rechazada —*«File is in a directory
that is denied by your permission settings»*—, y lo mismo un `rm` sobre una corrida archivada y
un `cp` sobre el propio archivo de configuración. Ampliar los propios permisos dejó de ser algo
que el sistema pueda hacer.

**Y tiene un agujero, medido.** La regla `deny` se evalúa sobre el comando: un
`echo >> herramientas/costo.py` se bloquea, y un `python3 - <<'PY'` que escribe el mismo
archivo desde adentro del intérprete **pasa**. Para los cinco especialistas eso da igual —
ninguno tiene `Bash`, y sin intérprete no hay elusión. Para el director no: necesita `Bash`
para correr el validador. La jaula frena el atajo distraído, que es el modo de falla real, y
no frena a uno decidido a rodearla. Todo desarrollado en [`GOBIERNO.md`](GOBIERNO.md) §1 y en
[`DECISIONES.md`](DECISIONES.md) §15.

**Lo que sigue sin probarse:** la jaula **todavía no corrió una corrida completa**. Las tres
archivadas son anteriores. Contar las llamadas a `Bash` de los cinco especialistas en los
transcripts de una corrida hecha con la jaula puesta es la corrida 04, y es de quien la corra.
Escribir acá que está probado sería el mismo error que este repositorio ya cometió una vez.

### Las tres corridas terminaron sin firmar

Y es el resultado correcto, no una falla. Cada `FIRMA.md` dice por qué. Los bloqueantes reales
que encontró el `editor-qa`:

- **Corrida 01:** 5 de 7 enlaces internos apuntaban a piezas inexistentes — **con el validador
  en verde**. El schema valida campos, no relaciones entre campos.
- **Corrida 02:** el argumento central de las cinco piezas era una **inferencia** del orden de
  las etapas del framework, no una cita de ningún activo.
- **Corrida 03:** `blog-01` escribe *«a dozen-plus languages»* en el primer párrafo —la forma
  correcta— y dos párrafos después *«we're live in fourteen markets»*, un número que el
  contexto de marca prohíbe explícitamente. **La misma pieza contiene la forma correcta y la
  prohibida.**

### El medidor de costo medía 4,3 veces menos de lo real

Primer conteo de la corrida 01: USD 1,41. Real: USD 6,10. Tres bugs, todos empujando en la
misma dirección —hacer parecer el sistema más barato—: no deduplicar los bloques de streaming,
quedarse con el bloque de salida incompleto en vez del mayor, y no escanear los transcripts de
los subagentes, que son el 89% de las llamadas. Un cuarto: el id de Haiku llega con sufijo de
fecha y no matcheaba la tabla de precios, así que **el brazo más barato del banco se contaba
como costo cero**. Y un quinto, encontrado al citar la tarifa real para este documento: la
escritura de caché se cobraba toda a 1,25× el precio de entrada, pero esa es la tarifa del TTL
de 5 minutos y el de 1 hora vale 2,00×. Estaba declarado como supuesto —y el transcript traía
el desglose para no tener que suponerlo. Ver [`COSTOS.md`](COSTOS.md) §1, T4.

### Lo que decidí NO arreglar, y por qué

Cuando C3 tapó la falla de los ids, el `editor-qa` encontró que reaparecía un casillero más
allá: los anchors declarados no existían en el texto. La tentación era un control C4.
**No lo hice.** Cada control mueve la falla, no la elimina — y un anchor puede existir y estar
sobre la frase equivocada, que es exactamente lo que pasó. Perseguir eso con controles es
perseguir verificación semántica con expresiones regulares. Costo de la decisión: **el
enlazado interno no es confiable sin revisión humana**, y está declarado. Razonamiento
completo en [`DECISIONES.md`](DECISIONES.md) §6.

### Otros límites conocidos

- **`WebFetch` no se ejercitó dentro de una corrida**: se usó para construir `activos/`
  (4 llamadas reales, con fecha en [`activos/FUENTES.md`](activos/FUENTES.md)). Dentro de las
  corridas la herramienta es el filesystem.
- **El paso «escribir `calendario.csv`» está en el pipeline y nunca se ejecutó.**
- **El banco de modelos midió una sola de las cinco tareas.** El modelo del `editor-qa` es
  extrapolación — y es el rol donde más importaría medirlo, porque el criterio que Haiku falló
  (ver los propios límites) es precisamente el suyo.
- **Los contratos v1 y v2 están reconstruidos**, no guardados en su momento. Su cabecera lo dice.
- **Ninguna pieza se publicó.** No hay evidencia de que el contenido funcione en el mercado.
- **La marca está anonimizada** (ver la nota al principio). El sistema corrió sobre material
  público real; los identificadores se redactaron antes de publicar el repositorio.
- **La historia de commits no muestra días de trabajo**, porque no los hubo: el proyecto se
  ejecutó en una sesión concentrada.
- **La jaula de permisos y el runbook no fueron ejercitados en una corrida completa.** Se
  probaron contra intentos directos —la jaula bloqueó tres veces a la sesión que la escribía— y
  los scripts de apertura y cierre se corrieron de punta a punta sobre una corrida de prueba
  que después se borró. Pero **el sistema entero con la configuración nueva es la corrida 04**,
  y todavía no existe.

---

## Qué aprendí

**El contrato no sirve para que el agente no haga macanas: sirve para que haga lo mismo dos
veces.** Corrí el prompt ingenuo dos veces con el mismo modelo y obtuve 5 piezas con JSON una
vez y 20 en prosa la otra. Sin contrato no hay sistema, hay suerte.

**Cada control mecánico mueve la falla en vez de eliminarla, y además cambia el comportamiento
del agente.** Agregué C3 y la falla reapareció un casillero más allá; y el analista SEO escribió
por iniciativa propia que evitaba enlazar a piezas dudosas *«para no arriesgar el control C3»*.
Se volvió conservador. Los agentes optimizan contra el control que ven.

**Lo más incómodo: escribir que un modo de falla existe no protege contra él.** Documenté que el
sistema puede citarse a sí mismo como fuente, y después cometí exactamente ese error un nivel
más arriba — afirmé en `GOBIERNO.md` que los permisos eran de cierta manera porque yo mismo los
había escrito así, sin verificar los transcripts. Lo encontró un evaluador externo, no yo.

**Un sistema no está terminado cuando funciona: está terminado cuando funciona en manos de
alguien que no lo construyó.** La distancia entre las dos cosas no se mide en código —el
sistema no cambió al escribir el runbook— sino en todo lo que el autor sabe sin haberlo
escrito. Acá eran tres cosas: por dónde empezar, cómo saber si el repo está sano sin gastar una
corrida, y un nombre de directorio escrito a mano que hacía que el medidor de costo devolviera
«sin datos» en cualquier máquina que no fuera la mía.

**La verificación mecánica y la humana encuentran cosas distintas, y hay que tener las dos.**
`validar.py` salió en verde en las tres corridas, y las tres terminaron no aptas para firma:
los tres hallazgos graves los encontró el `editor-qa` o una persona. La herramienta verifica la
forma; el criterio sigue siendo del que firma. **La responsabilidad no se delega.**

---

## Mapa del repositorio

| Dónde | Qué contiene |
|---|---|
| [`OPERACION.md`](OPERACION.md) | **El runbook.** Requisitos, los pasos de una corrida, los prompts que se pegan, y qué hacer cuando algo falla |
| [`prompts/system_prompt.md`](prompts/system_prompt.md) | Contrato del director: seis piezas, R1–R8, ruteo del equipo, mapa L0–L4 |
| [`prompts/user_prompt.md`](prompts/user_prompt.md) | Plantilla del brief semanal |
| [`prompts/agentes/`](prompts/agentes/) | Los cinco contratos de especialista |
| [`prompts/variantes/`](prompts/variantes/) | Contratos v1 y v2, reconstruidos — la cabecera lo declara |
| [`corridas/`](corridas/) | Las tres corridas reales + los dos pilotos + el banco de modelos |
| [`corridas/PROCEDENCIA.md`](corridas/PROCEDENCIA.md) | **Cómo reconstruir cada corrida:** entrada, salida, fecha y el dato de origen que leyó, en una tabla |
| [`DECISIONES.md`](DECISIONES.md) | La historia de la construcción: 17 entradas (§0–§16) y lo que queda pendiente |
| [`COSTOS.md`](COSTOS.md) | Tokens medidos, banco de 3 modelos, proyección semanal y anual |
| [`GOBIERNO.md`](GOBIERNO.md) | Permisos, 8 modos de falla, checklist de firma, quién firma |
| [`activos/`](activos/) | Material público real de la marca, con procedencia en [`FUENTES.md`](activos/FUENTES.md) |
| [`contexto/marca.md`](contexto/marca.md) | El documento compartido que mantiene el estratega y leen los otros cuatro |
| [`esquemas/`](esquemas/plan_semanal.schema.json) | El contrato de datos de la salida |
| [`herramientas/`](herramientas/) | `verificar-repo.py` · `validar.py` · `render.py` · `costo.py` · `nueva-corrida.sh` · `cerrar-corrida.sh` · `sincronizar.sh` |
| [`jaula/settings.json`](jaula/settings.json) | **La jaula de permisos vigente**, con su [README](jaula/README.md): qué deniega, a quién, y hasta dónde llega |
| `.claude/` | Carpeta oculta, **espejo y no original**: `agents/` es copia de [`prompts/agentes/`](prompts/agentes/) y `settings.json` es copia de [`jaula/settings.json`](jaula/settings.json). La escribe `sincronizar.sh`; es donde Claude Code lee. Nada vive solo ahí — lo verifica el control D12 |
