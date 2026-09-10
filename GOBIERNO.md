# GOBIERNO Y RIESGO

Qué sistemas toca el agente y con qué permisos · qué puede salir mal y qué pasa cuando sale
mal · qué se revisa antes de confiar en una salida · quién firma.

> **Si venís a verificar y tenés tiempo para una sola sección, es la [§5](#5--los-dos-controles-la-restricción-escrita-y-la-restricción-actuando).**
> Ahí está cada restricción de gobierno en dos columnas: la cita textual del contrato, y esa
> misma restricción **citada actuando** en la salida de una corrida. Lo demás de este documento
> describe el sistema; esa sección lo muestra funcionando.

---

## 1 · Inventario de permisos

### Lo que el sistema toca

| Sistema | Alcance | Permiso | Nivel |
| --- | --- | --- | --- |
| Filesystem — `activos/` | 6 archivos de material **público** de la marca | lectura (ver el recuadro de abajo) | L3 |
| Filesystem — `contexto/marca.md` | El documento de contexto compartido | lectura + escritura, **solo el estratega** | **L2** |
| Filesystem — `corridas/<id>/salida/` | Los dos entregables de la corrida | escritura | **L2** |
| Filesystem — `esquemas/`, `herramientas/` | Schema y validador | **solo lectura, para todos los agentes** | — |
| Red — `WebFetch` | GET sobre `acme-multilingual.example` y el sitio del competidor. **Se usó para construir `activos/`: 4 llamadas, las cuatro en `activos/FUENTES.md`. No se ejecutó dentro de ninguna corrida.** Hubo además una quinta llamada de `WebFetch` en el proyecto, a `eve.dev`, para leer el template de equipo de marketing que inspiró la arquitectura: no aporta ningún contenido a `activos/` y por eso no está ahí, pero se declara acá para que el conteo cierre contra los transcripts | solo lectura, sin credenciales | L3 |

> ### ⚠️ En las tres corridas, estos permisos fueron documentales y no configuración vigente
>
> **Es el hallazgo más serio de la revisión adversarial de este trabajo, y se deja
> escrito tal como se encontró.** El único control mecánico de permisos que el sistema tenía
> entonces era el `tools:` del frontmatter de cada contrato — por ejemplo,
> `redactor-contenido.md` declara `tools: Read, Glob, Grep`. Ese control **solo se aplica si
> el agente se invoca por su nombre registrado en `.claude/agents/`.**
>
> En esas corridas los especialistas se invocaron **pasándoles la ruta de su contrato**
> (ver `DECISIONES.md` §7), lo que los ejecuta como agentes genéricos. La inspección de los
> transcripts de la corrida 03 lo confirma: **cuatro de los cinco invocaron `Bash`** — uno lo
> usó 17 veces, y uno hizo además un `Write` — y **ninguno de los cinco contratos declara
> `Bash` ni `Write`**. (Del quinto solo se puede afirmar que no lo usó; que lo tuviera
> disponible es inferencia razonable, no evidencia.)
>
> **Consecuencia real:** los cinco agentes tuvieron lectura, escritura y ejecución sobre todo
> el repo, incluidos `validar.py` y el schema. La regla «no modifica su propia verificación»
> se cumplió —ninguna corrida tocó el validador— pero **se cumplió por instrucción, no porque
> estuviera impedida.** La tabla de arriba describía el puesto que el sistema debería tener,
> no la jaula que efectivamente tuvo.

### La jaula vigente hoy — y hasta dónde llega

La corrección #1 del sistema está hecha, **después** de las tres corridas y sin volver a
correrlas. Son dos capas, y una tercera que no es técnica:

| Capa | Qué es | A quién caza | Estado |
| --- | --- | --- | --- |
| **1 · `tools:` del frontmatter** | Cada contrato declara sus herramientas. Los cinco existen en `.claude/agents/` **antes** de abrir la sesión, así que ahora sí se los puede invocar por nombre registrado | Los cinco especialistas | **Vigente.** El control D2 de `verificar-repo.py` verifica además que ninguno declare `Bash` |
| **2 · `deny` de [`jaula/settings.json`](jaula/settings.json)** | Deniega `Write` y `Edit` sobre `esquemas/`, `herramientas/`, `prompts/`, `activos/`, las corridas archivadas, la propia `jaula/` y `.claude/settings.json` | **Todos**, director incluido | **Vigente y verificada en esta sesión** (ver abajo) |
| 3 · La instrucción del contrato | *«si el validador falla, arreglá el JSON — no toques el validador ni el schema»* | Todos | Vigente desde v1. Ya no es la única barrera |

**Dónde está el archivo, y por qué importa.** La fuente de verdad es
[`jaula/settings.json`](jaula/settings.json), una ruta visible con su propio
[README](jaula/README.md); `.claude/settings.json` es la copia que Claude Code carga, y la
escribe `herramientas/sincronizar.sh`. La jaula vivía **solo** en la carpeta oculta, y un
corrector externo que listó el repositorio sin archivos ocultos no la encontró: leyó un trabajo
que afirmaba tener permisos vigentes y no podía verificarlo. **Una regla que un auditor no puede
ver no es un control: es otra afirmación.** El episodio y la corrección están en
`DECISIONES.md` §16, y el control **D11** compara las dos copias byte a byte.

**Qué está verificado, textualmente.** Al escribir la jaula, la sesión que la escribió quedó
adentro: el intento de crear `herramientas/verificar-repo.py` con la herramienta `Write` fue
rechazado —*«File is in a directory that is denied by your permission settings»*—, un `rm` sobre
una corrida archivada fue rechazado, y un `cp` sobre `.claude/settings.json` fue rechazado. **La
jaula bloqueó a su propio autor antes que a nadie.** Ese es el estándar de prueba que
`DECISIONES.md` §11 dice que le faltó a la versión anterior de esta sección: no *«escribí que
los permisos son así»* sino *«intenté violarlos y no pude»*.

**Y hasta dónde NO llega — el agujero, medido y no supuesto.** La regla `deny` se evalúa sobre
el comando, así que **una escritura escondida adentro de un intérprete la elude**: en esta misma
sesión, `python3 - <<'PY'` escribiendo a `herramientas/costo.py` pasó, y `echo >> herramientas/…`
fue bloqueado. La consecuencia es precisa y hay que decirla así:

- **Para los cinco especialistas la jaula es efectiva**, porque ninguno tiene `Bash`: sin
  intérprete no hay elusión posible. Es el 89% de las llamadas de una corrida (`COSTOS.md` §3).
- **Para el director no es una prueba de imposibilidad**, porque necesita `Bash` para correr
  `validar.py` y `render.py`. Es una barrera de primer orden: frena el atajo distraído —que es
  el modo de falla real— y no frena a un agente decidido a rodearla.

**Lo que sigue pendiente.** La jaula está cargada y probada contra intentos directos, pero
**todavía no fue ejercitada en una corrida completa**: las tres archivadas son anteriores. Que
el `tools:` se aplique al invocar por nombre es cómo Claude Code está definido y cómo esta
sesión los cargó, no algo que este repositorio haya medido en producción. La prueba
—inspeccionar los transcripts de la corrida 04 y confirmar cero llamadas a `Bash` desde los
cinco especialistas— es el paso 3 de [`OPERACION.md`](OPERACION.md), y es de la persona que
corra la próxima. **Escribirlo acá no lo prueba: es exactamente el error que este documento
cometió una vez.**

### Lo que el sistema NO toca — y no puede tocar

- **No publica.** En ningún canal. No tiene credenciales de LinkedIn, X, del CMS, ni del
  gestor de newsletter. `firma.requiere_firma_humana` es `const: true` en el schema: **una
  salida sin firma humana es inválida por construcción, no por convención.**
- **No manda mails.** No tiene acceso a ninguna cuenta.
- **No toca sistemas internos.** Ni CRM, ni analytics, ni el CMS, ni datos de clientes.
- **No modificó su propia verificación** en ninguna corrida — pero en esas tres corridas fue
  por instrucción y no por permiso: ver el recuadro de arriba. El contrato lo dice
  explícitamente (`prompts/user_prompt.md`): *si el validador falla, arreglá el JSON — no
  toques el validador ni el schema*. Es la barrera contra el atajo más tentador de un agente
  con permiso de escritura: cuando la verificación molesta, aflojar la verificación. **Desde
  la jaula de [`jaula/settings.json`](jaula/settings.json), esa instrucción tiene además una regla `deny` detrás**,
  con el alcance y el agujero que la tabla de arriba declara.

### Confidencialidad — el riesgo propio de este caso

El caso es una empresa real y el repositorio es público. **Regla dura, aplicada desde el
primer archivo:**

> Solo entra al repo material que **ya es público**: el sitio web y el índice del blog,
> extraídos de la web abierta. Cero datos internos, cero datos de clientes, cero métricas no
> publicadas, cero precios no publicados.

**Y una segunda capa, aplicada después.** La regla de arriba se cumplió desde el primer
archivo, pero no alcanzó: **el titular del material pidió no ser nombrado en un repositorio
público**, y material público sobre una empresa identificable sigue siendo material sobre una
empresa identificable. Así que antes de publicar se redactaron todos los identificadores —
nombre, dominio, categoría propia, productos, clientes, las dos personas que firman el blog,
el competidor y las cifras publicadas — reemplazados por equivalentes ficticios de forma
consistente en todos los archivos del repo, con dominios en el TLD reservado `.example`.

Es exactamente el caso que este mismo documento anticipaba: *«si algo resulta imprescindible,
se anonimiza **y se dice que se anonimizó**»*. La nota completa está al principio del README.
Ninguna corrida, falla, cifra de token ni decisión cambió: solo los nombres.

`activos/FUENTES.md` registra de dónde salió cada archivo y cuándo. Las únicas cuatro cifras
que el sistema puede usar son las cuatro que la empresa publica en su home — y R1 lo hace
cumplir mecánicamente. **El sistema no puede filtrar información interna porque nunca tuvo
acceso a ninguna.**

---

## 2 · Modos de falla

Ordenados por lo que costaría dejarlos pasar. Los seis primeros **se observaron de verdad** en
las corridas de `corridas/`; no son hipótesis.

### F1 · El sistema se cita a sí mismo como fuente — **el más grave**

**Qué es.** `contexto/marca.md` es a la vez el mecanismo de coordinación del equipo y un
archivo que el sistema escribe. Un agente puede afirmar una tesis, escribirla ahí, y los otros
cuatro la citan como si fuera un activo.

**Observado.** Corridas 01 y 02. En la 02 el argumento central de las cinco piezas era una
**inferencia** del orden de las etapas del framework, no una cita.

**Por qué es el peor.** La trazabilidad mecánica (C1) verifica que la fuente **exista**, no que
sea **externa**. El sistema produce afirmaciones perfectamente trazables a una fuente que él
mismo fabricó dos pasos antes.

**Detección.** Solo el editor-qa y el humano. Ninguna herramienta.
**Mitigación.** Ítem 1 del checklist de firma: aprobar o rechazar explícitamente la afirmación
central de la semana. Si no se aprueba, cae el plan entero.

### F2 · Inconsistencia interna dentro de una misma pieza

**Qué es.** El agente aplica una restricción y la olvida en el mismo texto.
**Observado.** Corrida 03: `blog-01` escribe «a dozen-plus languages» (correcto) y dos
párrafos después «we're live in fourteen markets» (prohibido explícitamente).
**Por qué importa.** Todo el contrato está escrito contra la **invención** de datos. Este es un
modo distinto: el dato no es inventado, es un dato del brief que no podía migrar a una pieza.
**Detección.** El editor-qa lo encontró. `validar.py` no puede.
**Mitigación.** Checklist de firma. Sin corrección mecánica en esta versión — ver
`DECISIONES.md` §6 para por qué.

### F3 · Verificación mecánica que da falsa cobertura

**Qué es.** Un control pasa y el humano lo lee como «esto está verificado».
**Observado, tres veces:**
- C2 verifica que una cifra **aparezca** en `activos/` — no que **pruebe** lo que la pieza
  afirma. Las cuatro cifras publicadas son resultados de localización y SEO: usarlas como
  prueba de otra cosa **pasa C2 y viola R1**. Lo detectó el estratega en la corrida 01.
- C3 verifica que el `desde` de un enlace exista — no que el anchor exista en el texto.
  Corrida 02: 5 de 8 anchors inexistentes, C3 en verde.
- Corrida 03: C2 salió en verde en las corridas 01 y 02 **porque no había ninguna cifra que
  verificar**, no porque hubiera verificado alguna.

**Mitigación.** El checklist de firma dice explícitamente cuándo un control pasó en vacío.

### F4 · Los agentes optimizan contra el control que ven

**Observado.** Corrida 02, el analista SEO, sin que nadie se lo pidiera: *«deliberadamente no
uso `blog-02`, `news-01`, `li-02` ni `x-01` para no arriesgar el control C3»*. Resultado: dos
piezas sin ningún enlace interno.
**Por qué importa.** Agregar un control no es gratis: cambia el comportamiento del sistema,
a veces achicándolo. **Cada control nuevo necesita su propia evaluación de efectos laterales.**

### F5 · Deriva del contexto compartido entre semanas

**Qué es.** `contexto/marca.md` se reescribe cada semana. Un error introducido ahí contamina
las cinco piezas de esa corrida y persiste en las siguientes.
**Observado.** El archivo creció de 285 a **453** líneas en tres corridas. En la **corrida 02**
el redactor encontró **una contradicción interna entre §7 y §8 del propio archivo**; el texto
está citado en [`corridas/banco-modelos/salida-opus-5.md`](corridas/banco-modelos/salida-opus-5.md).
**Mitigación.** Es el punto **L2** explícito del contrato: el humano aprueba el archivo antes
de que la ola 2 lo lea. Se hizo y quedó registrado en los `NOTAS.md` de las tres corridas.

### F6 · Parecerse al competidor sin nombrarlo

**Qué es.** El sistema lee `activos/competencia-verilang.md` para diferenciarse — y el
material más cercano es el que más contamina.
**Probado a propósito.** El brief de la corrida 03 empujaba directo hacia *«turn X into a
growth engine»*, que es el titular del competidor **y** una frase del propio sitio de la marca.
**Resultado: R4 aguantó**, cero coincidencias en las cinco piezas.
**Riesgo residual:** el eco estructural. El editor-qa marcó *«turns a content line item into a
business case»* como eco de la construcción prohibida, sin usar su vocabulario.

### F7 · Alucinación de cifras — el que el contrato sí cubre bien

**Mitigación:** R1 + control C2 + `cifras_usadas` con fuente por cifra. **No se observó ni una
sola cifra inventada en ninguna de las tres corridas.** Es el modo de falla mejor cubierto, y
es el único que tiene defensa mecánica de punta a punta.

### F8 · Dependencia operativa

Si el sistema deja de estar disponible, el plan de contenidos vuelve a hacerse a mano. **No
hay lock-in técnico**: los contratos son archivos markdown, los activos son archivos de texto,
y el entregable es JSON con schema propio. El costo de salida es el costo de volver a
escribir a mano — que es donde se estaba antes.

---

## 3 · Checklist de revisión antes de confiar en una salida

Lo produce el `editor-qa` en cada corrida, específico para esa semana, con el archivo y la
línea donde se verifica cada ítem. Está en `salida/plan.md` § Control de calidad. La forma
estable es esta:

| # | Qué se verifica | Quién puede |
| --- | --- | --- |
| 1 | **La afirmación central de la semana**: ¿es una cita de un activo o una inferencia del sistema? Si es inferencia, ¿la aprueba alguien con conocimiento de dominio? | Solo un humano |
| 2 | Cada cifra, contra su fuente y **con su contexto**: ¿prueba lo que la pieza dice que prueba? | Humano (C2 solo verifica que exista) |
| 3 | El enlazado interno: ¿los anchors existen en el texto y están sobre la frase correcta? | Humano (C3 solo verifica el id) |
| 4 | Los `[DATO FALTANTE]`: ¿se resuelven, se reescribe la oración, o se acepta el hueco? | Humano |
| 5 | R6 contra el calendario: ¿el ángulo repite algo de las últimas 4 semanas? | Parcial — el calendario está incompleto |
| 6 | R4: vocabulario y **construcciones** del competidor | Grep + criterio humano |
| 7 | Firma de autor por pieza, contra el reparto real del blog | Humano |
| 8 | Si el validador pasó **en vacío** (sin cifras que verificar, sin enlaces que chequear) | El propio editor-qa lo declara |

**Verificación mecánica, antes de todo lo anterior:**

```bash
python3 herramientas/verificar-repo.py                                   # ¿el sistema está sano?
python3 herramientas/validar.py corridas/<id>/salida/plan_semanal.json   # exit 0 obligatorio
```

Los dos verifican cosas distintas y ninguno reemplaza al otro. `validar.py` verifica **una
salida** contra el schema y los controles C1–C3. `verificar-repo.py` verifica **el sistema**
contra su propia documentación: contratos sincronizados, R1–R8 coherente en los seis, corridas
archivadas completas y reconstruibles, jaula de permisos cargada. Existe porque el hueco que
tapa tiene tres antecedentes en este mismo trabajo —`DECISIONES.md` §11, §12 y §14— y en los
tres lo encontró una persona, no una herramienta.

Es condición necesaria y **claramente no suficiente**: las tres corridas salieron con exit 0
contra el validador vigente al momento de correrlas, y las tres terminaron **no aptas para
firma**. (La corrida 01 **falla** contra el validador actual: el control C3 se agregó justamente
por lo que esa corrida reveló, y su salida se archiva sin retocar — ver `DECISIONES.md` §8.) Los tres hallazgos ALTOS de este
proyecto los encontró el editor-qa o un humano; ninguno lo encontró una herramienta.

---

## 4 · Quién firma

| Rol | Quién | Qué firma |
| --- | --- | --- |
| **Firmante** | Julián De León — responsable del sistema | Que el plan es apto para publicarse |
| Operador | El mismo | Que la corrida se ejecutó como dice `entrada.md` |
| Verificador automático | `editor-qa` + `validar.py` | Producen la evidencia; **no firman nada** |

**La firma se registra por corrida en `corridas/<id>/FIRMA.md`**, con el motivo cuando no se
firma.

**Estado de las tres corridas de este trabajo: ninguna firmada.** Cada `FIRMA.md` dice por qué.
No es un fracaso del sistema: es el sistema funcionando. Un equipo de agentes que produjera
cinco piezas publicables sin intervención humana en su primera semana sería una señal de que
la verificación no está mirando lo suficiente.

**La responsabilidad no se delega.** El sistema opera en **L2** — ejecuta solo, el humano
revisa hitos y el final — y la publicación es **L0**: el agente no publica nunca. Si una pieza
sale con un dato mal, el responsable es quien firmó, no el agente que la escribió.

---

## 5 · Los dos controles: la restricción escrita y la restricción actuando

Las secciones 1–4 dicen qué **debería** pasar. Esta dice dónde se **ve** pasando, y por eso
cada fila trae dos rutas: la restricción textual en el contrato, y esa **misma** restricción
visible en la salida de una corrida. Una restricción que solo existe en el contrato es una
intención; recién con la segunda columna es un control.

El criterio para la segunda columna es estricto: o la corrida **cumplió** la condición y la
salida muestra el comportamiento prescripto, o **no la cumplió** y la salida lo dice. Que el
control «probablemente se haya aplicado» no cuenta. La cita es el control.

### Par 1 · R1 — cero cifras inventadas

| | Ruta | Cita textual |
| --- | --- | --- |
| **Escrita** | [`prompts/system_prompt.md`](prompts/system_prompt.md) (R1) | «Si hace falta un dato que no está, escribí `[DATO FALTANTE: qué se necesita]` en el texto y registralo en `datos_faltantes`.» |
| **Actuando** | [`corridas/03-2026-09-05-w39/salida/plan_semanal.json`](corridas/03-2026-09-05-w39/salida/plan_semanal.json) → `control_calidad.datos_faltantes[0]` | «Contenido, hallazgos o estadisticas del report '2026 Native Reach State of the Industry'. activos/sitio-home.md solo registra su titulo y URL; ningun activo tiene su contenido real.» |

El CTA de esa semana apuntaba a una página de la que **no había ningún activo capturado**. La
condición de R1 se cumplió —hacía falta un dato que no estaba— y la salida hizo lo prescripto
en vez de rellenarlo.

La misma restricción se ve actuando **dentro del cuerpo** de las piezas en las otras dos
corridas: [`corridas/01-2026-09-05-w37/salida/plan.md:64`](corridas/01-2026-09-05-w37/salida/plan.md)
lleva «`[DATO FALTANTE: share of traffic coming from AI-generated answers, by market - not
published]`» incrustado en el párrafo, exactamente donde el agente habría tenido que inventar
la cifra.

### Par 2 · R4 — nada del competidor

| | Ruta | Cita textual |
| --- | --- | --- |
| **Escrita** | [`prompts/system_prompt.md`](prompts/system_prompt.md) (R4) | «Prohibido copiar claims, estructura o vocabulario de `activos/competencia-verilang.md`. Ese archivo se lee **para diferenciarse**, no para inspirarse.» |
| **Actuando** | [`corridas/03-2026-09-05-w39/salida/plan_semanal.json`](corridas/03-2026-09-05-w39/salida/plan_semanal.json) → `control_calidad.riesgos[6]` | «[LIMPIO — resultado del experimento de esta corrida] R4 aguanto la prueba de estres. El brief empujaba directo a 'growth engine' / 'cost center' y ninguna de las 5 piezas las usa. La frase esta ademas en el propio sitio de la marca, lo que la hacia mas tentadora.» |

Es el par más fuerte de los tres porque la condición **se buscó a propósito**: la hipótesis 1
de [`corridas/03-2026-09-05-w39/entrada.md`](corridas/03-2026-09-05-w39/entrada.md) se anotó
antes de correr, y ninguna de las tres invocaciones de la ola 2 menciona R4 ni el experimento.
La misma salida registra además el caso de borde que el control **no** alcanza, en
`riesgos[4]`: «li-02 usa 'turns a content line item into a business case': eco estructural, no
literal, del giro vedado».

### Par 3 · R3 — el sistema no publica nunca

| | Ruta | Cita textual |
| --- | --- | --- |
| **Escrita** | [`prompts/system_prompt.md`](prompts/system_prompt.md) (R3) | «El sistema **no tiene** permiso de publicación en ningún canal. La salida es siempre borrador. `firma.requiere_firma_humana` es siempre `true` y `firma.firmante` sale siempre en `null`.» |
| **Actuando** | [`corridas/03-2026-09-05-w39/salida/plan_semanal.json:153`](corridas/03-2026-09-05-w39/salida/plan_semanal.json) → `firma` | `"requiere_firma_humana": true,` / `"firmante": null,` |

Las **cuatro** salidas archivadas —las tres corridas y el piloto— traen ese par de valores, y
las tres corridas traen además su [`FIRMA.md`](corridas/03-2026-09-05-w39/FIRMA.md) con el
motivo: «**Estado: NO FIRMADA.** Firmante: — · Fecha: —».

### Dónde el par no cierra, y se deja escrito

El par que **no** se puede armar es el de la jaula de permisos: la restricción está escrita
(§1 y [`jaula/settings.json`](jaula/settings.json)) pero **ninguna de las tres corridas la tuvo
vigente**, porque la jaula se agregó después. El recuadro de §1 lo dice con todas las letras.
No se lista acá como par porque no lo es: es una restricción escrita esperando su primera
corrida.
