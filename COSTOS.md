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
ventana archivada de la corrida 03 (`.inicio` → `.fin`, 2026-09-05T22:20:40Z → 22:54:42Z) sale
**USD 3,9551** contra los **USD 3,9551** guardados en su `consumo.json` en el momento de
correrla: 46 llamadas, 89.494 tokens de salida, los mismos dos modelos. La cifra de este
documento no es una cifra que haya que creer: es una que se recalcula.

**Tres trampas de medición que este trabajo encontró y corrigió** (la historia completa está
en `DECISIONES.md` §4). Las tres empujaban en la misma dirección — hacer parecer el sistema
más barato de lo que es:

| # | Trampa | Efecto si no se corrige |
| --- | --- | --- |
| T1 | Cada respuesta se repite en el transcript una vez por `apiBlockIndex` | Multiplica el total |
| T2 | Al deduplicar hay que quedarse con el bloque de **mayor** `output_tokens`; en streaming el primero trae el contador incompleto | **Subestima la salida ~100×** — el token más caro |
| T3 | Los subagentes escriben en transcripts propios; y el id de Haiku llega con sufijo de fecha y no matchea la tabla de precios | Pierde el 89% de las llamadas y cuenta el modelo barato como costo cero |

**Atribución por corrida.** Se usa la ventana temporal (`.inicio` / `.fin` de cada corrida).
Es exacta para corridas secuenciales. La corrida 02 se solapó con el banco de pruebas de
modelo, así que su costo limpio se midió **por transcript individual de cada agente**, no por
ventana. Está dicho en su `metadata.json`.

## 2 · Precios y supuestos declarados

USD por millón de tokens, precios de lista de la API de Anthropic:

| Modelo | Entrada | Salida |
| --- | ---: | ---: |
| `claude-opus-5` | 5,00 | 25,00 |
| `claude-sonnet-5` | 2,00 | 10,00 |
| `claude-haiku-4-5` | 1,00 | 5,00 |

**Supuesto declarado:** las lecturas y escrituras de caché se valorizan con los
multiplicadores estándar sobre el precio de entrada — **escritura 1,25× · lectura 0,10×**.
Están como constantes al tope de `herramientas/costo.py` para que se puedan cambiar en un
solo lugar. **Los conteos de tokens son hechos medidos; los dólares dependen de este
supuesto.** Importa más de lo que parece: el 92,5% de los tokens de entrada de este proyecto
son lecturas de caché.

## 3 · Costo medido por corrida

| Corrida | Contrato | Modelo | Llamadas | **Tokens de entrada** | **Tokens de salida** | **USD** |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 00 · piloto (v0, un solo agente) | v0 | Opus 5 | 26 | 2.696.513 | 40.324 | **3,31** |
| 01 · W37 | v1 | Opus 5 | 64 | 5.126.480 | 67.842 | **5,97** |
| 02 · W38 *(ventana incluye el banco)* | v2 | Opus 5 | 79 | 6.614.142 | 96.510 | *7,54* |
| **03 · W39 — configuración de producción** | **v3** | **Sonnet 5** | 46 | 5.276.452 | 89.494 | **3,96** |

«Tokens de entrada» suma las tres formas en que entra el contexto: entrada directa, escritura
de caché y lectura de caché. El desglose de las tres está en cada `corridas/*/consumo.json` y
lo imprime `costo.py`. **El 92,5% son lecturas de caché** — ver §7, que es donde está la
palanca de costo más grande del sistema.

### Desglose de la corrida 03, por agente (medido, transcript por transcript)

| Agente | Llamadas | Caché escr. | Caché lect. | Salida | **USD** |
| --- | ---: | ---: | ---: | ---: | ---: |
| estratega-posicionamiento | 8 | 234.037 | 471.681 | 15.771 | 0,8372 |
| redactor-contenido | 11 | 69.685 | 823.811 | 10.275 | 0,4418 |
| community-social | 7 | 54.829 | 471.279 | 5.029 | 0,2816 |
| seo-analista | 2 | 34.587 | 87.805 | 18.782 | 0,2919 |
| editor-qa | 12 | 106.175 | 1.040.428 | 29.128 | 0,7649 |
| **los 5 especialistas** | **40** | | | | **2,6174** |
| director (esta corrida corrió en Opus) | | | | | 1,3377 |

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
curso. Pasa los nueve criterios por **2,9× menos que Opus**.

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
| **Medido** | **USD 20,77** — suma de las 4 ventanas de corrida, archivadas en cada `consumo.json` | **USD 2,62** (5 especialistas) |
| Naturaleza | Inversión hundida, una sola vez | La cuenta que decide |

> **Reproducible:** la cifra de construcción es la suma de los cuatro `corridas/*/consumo.json`,
> archivados en el repo. Se prefirió esa suma antes que el total de la sesión completa, que
> incluye la escritura de esta documentación y **sigue creciendo mientras se escribe** — con
> lo cual no es una cifra que un tercero pueda reproducir.

**Confundirlas es el error clásico.** Construir salió 8× lo que sale correr una semana. Un
análisis que reporte «USD 26» como el costo del sistema es tan engañoso como uno que reporte
«USD 2,62» como el costo total del proyecto.

## 6 · Proyección

**Costo de una corrida en configuración de producción.** Medido: USD 2,62 los cinco
especialistas. El director de la corrida 03 todavía corrió en Opus (USD 1,34); en producción
correría en Sonnet. Aplicando el ratio Opus/Sonnet **medido en el banco sobre la misma tarea**
(2,85×), el director proyecta a **≈ USD 0,47**.

> **Corrida completa en producción ≈ USD 3,09.** De ese número, 2,62 son medidos y 0,47
> proyectados.

| Escenario | Corridas/semana | **USD/semana** | Corridas/año | **USD/año** |
| --- | ---: | ---: | ---: | ---: |
| 1 marca, 1 plan semanal | 1 | **3,09** | 52 | **≈ 161** |
| 1 marca, plan semanal + 1 rehacer por mes | 1,23 | ≈ 3,80 | 64 | ≈ 198 |
| 4 marcas (el sistema «en serio») | 4 | **12,36** | 208 | **≈ 643** |
| 12 marcas (un equipo de agencia) | 12 | 37,08 | 624 | ≈ 1.928 |

**La lectura de gestión.** Ni siquiera el escenario de agencia —doce marcas, un plan por
semana cada una— llega a **USD 2.000 al año**. En una operación de marketing de contenidos
enterprise, el costo de inferencia de este sistema no es una variable de decisión: es ruido
contra el costo de las personas que revisan y firman su salida. **La variable que decide es
el tiempo humano**, y es la que este trabajo no midió (ver abajo).

**El contraste que corresponde a la decisión.** Una corrida entrega 5 piezas redactadas, el
plan de SEO, y un informe de control de calidad con 6-8 ítems verificables. A USD 3,09, el
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
