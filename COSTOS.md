# COSTOS — análisis económico

Todos los números de tokens de este documento están **medidos**, no estimados. Lo que es
supuesto o proyección está rotulado como tal.

---

## 1 · Método

Claude Code guarda, por cada respuesta del modelo, un bloque `usage` en el transcript de la
sesión (`~/.claude/projects/<slug>/*.jsonl`) y de cada subagente
(`<sesión>/subagents/agent-*.jsonl`):

```json
"usage":{"input_tokens":…,"cache_creation_input_tokens":…,"cache_read_input_tokens":…,"output_tokens":…}
```

`herramientas/costo.py` los suma. Se corre así:

```bash
python3 herramientas/costo.py --desde 2026-09-05T21:36:08Z --hasta 2026-09-05T22:05:00Z
python3 herramientas/costo.py --sesion <ruta al transcript de un subagente>
python3 herramientas/costo.py --desde … --hasta … --transcripts <dir>   # transcripts archivados
```

**El `<slug>` se deriva de la ubicación real del repositorio**, no está escrito a mano: es la
ruta absoluta con todo lo que no es alfanumérico reemplazado por `-`. Antes estaba hardcodeada
la ruta de una laptop, y en cualquier otra máquina el script imprimía «sin datos en ese rango»:
**no fallaba, mentía en silencio**, que es el mismo modo de falla de las tres trampas de abajo.
Ahora, si no encuentra transcripts, lo dice — y una corrida sin consumo medido se declara como
no medida, no se estima.

**Comprobación de que la medición es reproducible.** Volviendo a correr el medidor hoy sobre la
ventana archivada de la corrida 03 (`.inicio` → `.fin`, 2026-09-05T22:20:40Z → 22:54:42Z) salen
las mismas **46 llamadas, 92 tokens de entrada directa, 522.613 de escritura de caché, 4.753.747
de lectura y 89.494 de salida** que están guardadas en su `consumo.json`, sobre los mismos dos
modelos. Los tokens son idénticos; el dólar cambió una vez, cuando se corrigió T4 (abajo): la
misma ventana valía **USD 3,9551** con la regla vieja y vale **USD 4,0424** con la tarifa real.
La cifra de este documento no es una cifra que haya que creer: es una que se recalcula, y cuando
cambia se dice por qué.

**Cuatro trampas de medición que este trabajo encontró y corrigió** (la historia completa está
en `DECISIONES.md` §4). Tres de las cuatro empujaban en la misma dirección — hacer parecer el
sistema más barato de lo que es:

| # | Trampa | Efecto si no se corrige |
| --- | --- | --- |
| T1 | Cada respuesta se repite en el transcript una vez por `apiBlockIndex` | Multiplica el total |
| T2 | Al deduplicar hay que quedarse con el bloque de **mayor** `output_tokens`; en streaming el primero trae el contador incompleto | **Subestima la salida ~100×** — el token más caro |
| T3 | Los subagentes escriben en transcripts propios; y el id de Haiku llega con sufijo de fecha y no matchea la tabla de precios | Pierde el 89% de las llamadas y cuenta el modelo barato como costo cero |
| T4 | La escritura de caché **no tiene un solo precio**: la tarifa publicada cobra 1,25× el precio de entrada con TTL de 5 minutos y **2,00× con TTL de 1 hora**. El campo plano `cache_creation_input_tokens` suma las dos y no distingue; el desglose real está en `usage.cache_creation` | Subestima entre 2,1% y 2,3% por corrida — poco, pero era **un supuesto disfrazado de medición** |

**T4 es la que más enseña de las cuatro.** Hasta encontrarla, este documento declaraba «escritura
1,25×» como *supuesto declarado* y se quedaba tranquilo con haberlo declarado. Declarar un
supuesto no lo vuelve cierto: el dato para verificarlo estaba en el mismo transcript que ya se
estaba leyendo, dos campos más adentro. **Un supuesto que se puede medir no es un supuesto, es
una medición que no se hizo.** Corregirlo movió el costo de construcción de USD 20,77 a
**21,23** y la corrida de producción de 3,09 a **3,12**; las cifras viejas quedan acá para que
la diferencia se pueda auditar.

**Atribución por corrida.** Se usa la ventana temporal (`.inicio` / `.fin` de cada corrida).
Es exacta para corridas secuenciales. La corrida 02 se solapó con el banco de pruebas de
modelo, así que su costo limpio se midió **por transcript individual de cada agente**, no por
ventana. Está dicho en su `metadata.json`.

## 2 · Precios: de dónde salen, exactamente

**Fuente única, citable y con fecha.** Todos los precios de este documento son los precios de
lista de la API de Anthropic publicados en
**<https://platform.claude.com/docs/en/about-claude/pricing>**, sección *Model pricing*,
**consultada el 2026-09-06**. No hay ningún precio promediado, redondeado ni estimado por este
trabajo: las cinco columnas de precio de abajo son las cinco columnas de precio de esa tabla,
para las tres filas que este sistema usa.

USD por millón de tokens (MTok):

| Modelo | Entrada base | Escritura de caché 5 min | Escritura de caché 1 h | Lectura de caché (hit) | Salida |
| --- | ---: | ---: | ---: | ---: | ---: |
| `claude-opus-5` | 5,00 | 6,25 | 10,00 | 0,50 | 25,00 |
| `claude-sonnet-5` | 2,00 | 2,50 | 4,00 | 0,20 | 10,00 |
| `claude-haiku-4-5` | 1,00 | 1,25 | 2,00 | 0,10 | 5,00 |

Las tres columnas de caché no son números independientes: la misma página las publica como
**multiplicadores sobre el precio de entrada base** — *5-minute cache write 1,25× · 1-hour cache
write 2,00× · cache read (hit) 0,10×*. Por eso en `herramientas/costo.py` están escritas así,
como tres constantes al tope del archivo, y no como una tabla de precios copiada a mano:

```python
MULT_CACHE_ESCRITURA_5M = 1.25
MULT_CACHE_ESCRITURA_1H = 2.00
MULT_CACHE_LECTURA = 0.10
```

**Nada de esto es un supuesto de este trabajo.** Los multiplicadores son tarifa publicada, y
**cuál de los dos TTL se aplicó a cada escritura también está medido**, no supuesto: el
transcript lo trae desglosado en `usage.cache_creation.ephemeral_5m_input_tokens` y
`ephemeral_1h_input_tokens`. Ese desglose es lo que corrige T4. Lo único que queda como
convención declarada es el fallback: si un transcript viejo no trae el desglose, se cobra a 5
minutos, que es el default de Claude Code.

**Dato de contexto sobre el precio de Sonnet 5, porque afecta a este trabajo.** Los USD 2 / 10
por MTok de `claude-sonnet-5` se anunciaron como precio introductorio hasta el 2026-08-31, con
un aumento previsto a USD 3 / 15 el 2026-09-01. La misma página de precios documenta que **ese
aumento no ocurrió y los USD 2 / 10 son ahora el precio estándar**. Importa porque este sistema
eligió Sonnet 5 para producción: como toda la corrida corre en Sonnet, un aumento de 1,5× en
las dos puntas la escala completa, y la corrida de producción costaría **≈ USD 4,68** en vez de
3,12 (3,12 × 1,5), con la proyección anual pasando de ≈ 162 a **≈ 243**. Sigue siendo ruido
contra el costo humano (§6), y por eso la decisión de modelo no cambiaría; pero la sensibilidad
se declara en vez de descubrirse.

**Qué es medido y qué es tarifa.** Los conteos de tokens son hechos medidos, sacados del
`usage` que devuelve la API. Los dólares son esos conteos multiplicados por la tarifa de arriba.
La tarifa puede cambiar mañana —es una lista de precios, no una ley— y por eso está en un solo
lugar del código y citada con fecha acá.

**Un número reconstruido a mano, para que no haya que creerle al script.** El `redactor-contenido`
de la corrida 03 (Sonnet 5) consumió, medido: **22** tokens de entrada directa, **69.685** de
escritura de caché (todos con TTL de 5 min), **823.811** de lectura de caché y **10.275** de
salida. A la tarifa de la tabla:

```
entrada directa   22 × 2,00 / 1.000.000  = 0,000044
caché escritura   69.685 × 2,50 / 1.000.000 = 0,174213      (2,00 × 1,25)
caché lectura     823.811 × 0,20 / 1.000.000 = 0,164762      (2,00 × 0,10)
salida            10.275 × 10,00 / 1.000.000 = 0,102750
                                        total = USD 0,441769  →  0,4418
```

que es exactamente la fila del redactor en la tabla por agente de §3. Reproducirla:

```bash
python3 herramientas/costo.py --sesion <transcript del redactor de la corrida 03>
```

**Dónde está la palanca.** El 92,5% de los tokens de entrada de este proyecto son lecturas de
caché, la línea más barata de la tabla (0,10×). Que sea la más barata es justamente por qué el
sistema sale lo que sale — y por qué la optimización pendiente no es cambiar de modelo (§7).

## 3 · Costo medido por corrida

| Corrida | Contrato | Modelo | Llamadas | **Tokens de entrada** | **Tokens de salida** | **USD** |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 00 · piloto (v0, un solo agente) | v0 | Opus 5 | 26 | 2.696.513 | 40.324 | **3,39** |
| 01 · W37 | v1 | Opus 5 | 64 | 5.126.480 | 67.842 | **6,10** |
| 02 · W38 *(ventana incluye el banco)* | v2 | Opus 5 | 79 | 6.614.142 | 96.510 | *7,70* |
| **03 · W39 — configuración de producción** | **v3** | **Sonnet 5** | 46 | 5.276.452 | 89.494 | **4,04** |

«Tokens de entrada» suma las tres formas en que entra el contexto: entrada directa, escritura
de caché y lectura de caché. El desglose de las cuatro líneas que se facturan distinto —entrada
directa, escritura 5 min, escritura 1 h y lectura— está en cada `corridas/*/consumo.json` y lo
imprime `costo.py` columna por columna. **El 92,5% son lecturas de caché** — ver §7, que es
donde está la palanca de costo más grande del sistema.

Las cuatro ventanas, para volver a correrlas:

```bash
python3 herramientas/costo.py --desde 2026-09-05T21:26:09Z --hasta 2026-09-05T21:35:47Z  # 00
python3 herramientas/costo.py --desde 2026-09-05T21:36:08Z --hasta 2026-09-05T21:54:26Z  # 01
python3 herramientas/costo.py --desde 2026-09-05T21:57:24Z --hasta 2026-09-05T22:19:25Z  # 02
python3 herramientas/costo.py --desde 2026-09-05T22:20:40Z --hasta 2026-09-05T22:54:42Z  # 03
```

Las ventanas de 01, 02 y 03 son las `inicio_utc` / `fin_utc` de su `metadata.json`. La del
piloto no está en un `metadata.json` porque el piloto se corrió antes de que existiera ese
archivo: se recuperó del transcript y queda escrita acá.

### Desglose de la corrida 03, por agente (medido, transcript por transcript)

| Agente | Modelo | Llamadas | Caché escr. 5 min | Caché escr. 1 h | Caché lect. | Salida | **USD** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| estratega-posicionamiento | Sonnet 5 | 8 | 234.037 | 0 | 471.681 | 15.771 | 0,8372 |
| redactor-contenido | Sonnet 5 | 11 | 69.685 | 0 | 823.811 | 10.275 | 0,4418 |
| community-social | Sonnet 5 | 7 | 54.829 | 0 | 471.279 | 5.029 | 0,2816 |
| seo-analista | Sonnet 5 | 2 | 34.587 | 0 | 87.805 | 18.782 | 0,2919 |
| editor-qa | Sonnet 5 | 12 | 106.175 | 0 | 1.040.428 | 29.128 | 0,7649 |
| **los 5 especialistas** | **Sonnet 5** | **40** | **499.313** | **0** | **2.895.004** | **78.985** | **2,6173** |
| director (esta corrida corrió en Opus) | Opus 5 | 6 | 0 | 23.300 | 1.858.743 | 10.509 | 1,4252 |

**Los especialistas no tienen ni una escritura de caché de 1 hora y el director las tiene
todas.** No es casual y explica por qué T4 mueve el número del director y deja intacto el de los
especialistas: el director es la sesión larga, que sostiene el mismo contexto durante toda la
corrida y por eso pide TTL largo; los subagentes son sesiones cortas y descartables. **El USD
2,62 de los especialistas —que es la cifra que decide, §5— no cambió ni un centavo al corregir
T4.**

**Dato de gestión:** el `editor-qa` cuesta el 29% de lo que cuestan los especialistas —
casi tanto como el que escribe— y **no produce ni una línea de contenido publicable**.
Es el precio de la verificación, y es el que hace que la salida sea firmable o no.

## 4 · Banco de pruebas de modelo

**Diseño.** Misma tarea (el redactor de la semana 38), mismo contrato v2, mismos activos,
tres modelos. **Los criterios de aprobación se declararon antes de correr.**

| Criterio | Haiku 4.5 | Sonnet 5 | Opus 5 |
| --- | :---: | :---: | :---: |
| Piezas entregadas (contrato: 1-2) | 1 | 2 | 2 |
| ids según R8 | ✓ | ✓ | ✓ |
| Extensión 300-600 palabras | ✓ | ✓ | ✓ |
| Cero cifras inventadas (R1) | ✓ | ✓ | ✓ |
| **Cero URLs inventadas** | **✗** placeholder en vez de URL | ✓ | ✓ |
| Sin vocabulario del competidor (R4) | ✓ | ✓ | ✓ |
| Un solo pilar (R5) | ✓ | ✓ | ✓ |
| **Territorio cerrado respetado (R6)** | **✗** propuso una keyword vedada | ✓ | ✓ |
| **Declaró sus propias limitaciones** | **✗** «riesgos: ninguno detectado» | ✓ | ✓ |
| **Costo medido (USD)** | **0,0754** | **0,4668** | **1,3317** |
| **Veredicto** | **falla 3 de 9** | **pasa 9 de 9** | pasa 9 de 9 |

**Decisión: `claude-sonnet-5`** — el más chico que hace bien la tarea, que es el criterio del
curso. Pasa los nueve criterios por **2,9× menos que Opus** (1,3317 / 0,4668 = 2,853).

**Los tres brazos son inmunes a T4** y por eso los tres costos de esta tabla son idénticos antes
y después de la corrección: los tres corrieron como subagentes, y ningún subagente de este
proyecto escribió caché con TTL de 1 hora. La comparación de modelos, que es de donde sale la
decisión, no depende del arreglo.

**El consumo crudo de los tres brazos, separado uno del otro, está en
[`corridas/RECALCULO.md`](corridas/RECALCULO.md).** Importa que esté: el brazo de Opus no se
corrió aparte —es el `redactor-contenido` de la corrida 02— y sin ese desglose sus `1,3317`
habría que creerlos o estimarlos restando del total de la corrida. No hace falta ninguna de las
dos cosas: **ese subagente tiene transcript propio y se mide solo**, y ahí están sus 15 llamadas,
sus 57.493 tokens de escritura de caché, sus 990.446 de lectura y sus 19.078 de salida, con la
multiplicación que da `1,331654` y desvío cero contra esta tabla. La razón que decide la
elección —`1,331654 / 0,466802 = 2,853`— se rehace desde ahí sin salir del repositorio.

**Por qué la tercera falla de Haiku es la que decide.** Haiku hizo la misma inferencia no
publicada que hicieron Sonnet y Opus — pero fue el único que declaró no tener ningún riesgo.
En un sistema cuyo mecanismo de seguridad es que los agentes digan lo que no pueden
respaldar, un modelo que produce texto igualmente plausible pero **no ve sus propios límites**
es peligroso justo donde el sistema confía.

**Límite declarado.** Se midió **una** de las cinco tareas. Extrapolar a las otras cuatro es
inferencia. El experimento pendiente más valioso es correr el banco sobre el `editor-qa`,
porque el criterio que Haiku falló es exactamente el suyo. Al revés, `community-social` es
la candidata más plausible a bajar a Haiku: piezas cortas, sin URLs, sin cifras.

## 5 · Las dos cuentas que hay que separar

| | Construir | Operar |
| --- | --- | --- |
| Qué es | Diseñar el contrato, iterar, depurar, medir | Correr una semana |
| Modelo | Opus 5 (y el banco) | Sonnet 5 |
| **Medido** | **USD 21,23** — suma de las 4 ventanas de corrida, archivadas en cada `consumo.json` | **USD 2,62** (5 especialistas) |
| Naturaleza | Inversión hundida, una sola vez | La cuenta que decide |

> **Reproducible:** la cifra de construcción es la suma de los cuatro `corridas/*/consumo.json`,
> archivados en el repo: **3,3852 + 6,1022 + 7,6994 + 4,0424 = 21,2292 → USD 21,23**. Se suman
> los valores exactos, no los redondeados de la tabla de §3; sumar los redondeados da 21,23
> también, pero eso es suerte y conviene decir cuál de las dos cuentas se hizo. Se prefirió esta
> suma antes que el total de la sesión completa, que incluye la escritura de esta documentación
> y **sigue creciendo mientras se escribe** — con lo cual no es una cifra que un tercero pueda
> reproducir.

**Confundirlas es el error clásico.** Construir salió casi 7× lo que sale una corrida completa
de producción (21,23 / 3,12 = 6,8). Un análisis que reporte «USD 21» como el costo del sistema
es tan engañoso como uno que reporte «USD 2,62» como el costo total del proyecto — y **el 2,62
tampoco es el costo de una corrida**: es el de los cinco especialistas, sin el director. La
corrida completa es 3,12, y es ese número, no el 2,62, el que se multiplica en §6.

## 6 · Proyección

**Costo de una corrida en configuración de producción.** Se arma con dos sumandos y ninguno
es un número redondo caído del cielo:

| Sumando | Cuánto | Qué es |
| --- | ---: | --- |
| Los 5 especialistas | **USD 2,6173** | **Medido.** Corrida 03, Sonnet 5, transcript por transcript (tabla de §3) |
| El director | **USD 0,4996** | **Proyectado.** Midió 1,4252 en Opus; ÷ 2,853, el ratio Opus/Sonnet medido en el banco sobre la misma tarea (§4) |
| **Corrida completa** | **USD 3,1169 → ≈ 3,12** | 2,62 medidos + 0,50 proyectados |

> **Corrida completa en producción ≈ USD 3,12.** De ese número, **2,62 son medidos y 0,50
> proyectados**. Todavía no hubo una corrida con el director corriendo en Sonnet: hasta que la
> haya, ese 0,50 es una proyección declarada, no una medición.

**La proyección anual se hace sobre 3,12, no sobre 2,62.** Es la confusión que este documento
más cuida, porque es la que convierte un análisis económico en un folleto: 2,62 × 52 daría 136 y
sería el costo de una corrida a la que le falta el director. La cuenta es **3,1169 × 52 =
162,08 → ≈ USD 162 al año**.

| Escenario | Corridas/semana | **USD/semana** | Corridas/año | **USD/año** |
| --- | ---: | ---: | ---: | ---: |
| 1 marca, 1 plan semanal | 1 | **3,12** | 52 | **≈ 162** |
| 1 marca, plan semanal + 1 rehacer por mes | 1,23 | ≈ 3,83 | 64 | ≈ 200 |
| 4 marcas (el sistema «en serio») | 4 | **12,47** | 208 | **≈ 648** |
| 12 marcas (un equipo de agencia) | 12 | 37,40 | 624 | ≈ 1.945 |

Todas las filas son la misma multiplicación sobre 3,1169: `USD/semana = 3,1169 × corridas/semana`
y `USD/año = 3,1169 × corridas/año`. Cualquiera de las ocho celdas se rehace con una calculadora.

**La lectura de gestión.** Ni siquiera el escenario de agencia —doce marcas, un plan por
semana cada una— llega a **USD 2.000 al año**. En una operación de marketing de contenidos
enterprise, el costo de inferencia de este sistema no es una variable de decisión: es ruido
contra el costo de las personas que revisan y firman su salida. **La variable que decide es
el tiempo humano**, y es la que este trabajo no midió (ver abajo).

**El contraste que corresponde a la decisión.** Una corrida entrega 5 piezas redactadas, el
plan de SEO, y un informe de control de calidad con 6-8 ítems verificables. A USD 3,12, el
sistema se paga si ahorra **más de unos pocos minutos** de trabajo humano calificado por
corrida — un umbral que cualquier reparto realista supera con enorme holgura.

**Pero el ahorro no es la variable que decide, y hay que decirlo.** Las tres corridas
terminaron **sin firmar**. El sistema no reemplaza al humano: le cambia la tarea, de *escribir
cinco piezas* a *resolver ocho ítems verificables*. Si esa segunda tarea toma más tiempo que
la primera, el sistema no conviene por más barato que sea. **Ese es el número que este
trabajo no midió**, porque haría falta operarlo varias semanas con la misma persona.

## 7 · La palanca más grande no es el modelo

El **92,5%** de los tokens de entrada de este proyecto son **lecturas de caché**: los agentes releen
`contexto/marca.md` (453 líneas) y los activos en cada invocación. Es deliberado —el archivo
compartido es el mecanismo de coordinación de la ola 2, y la Clase 2 lo advierte: *contexto
justo en vez de «todo el documento por las dudas»*.

`contexto/marca.md` creció de 285 a **453** líneas en tres corridas, y **lo leen cinco agentes por
corrida**. Cada línea que se agrega se paga cinco veces por semana, para siempre. La
optimización pendiente no es cambiar de modelo: es partir ese archivo en la parte estable
(secciones 1-6, cacheable entre semanas) y la parte semanal (7-9).
