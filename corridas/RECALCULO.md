# Recálculo — la reconstrucción que cierra

**Para qué es este archivo.** [`PROCEDENCIA.md`](PROCEDENCIA.md) dice de dónde salió cada
corrida. Este dice **que las cuentas dan**: por cada corrida, números de su propia salida
rehechos desde su propia entrada, con la operación escrita, el resultado y el desvío.

Una corrida es reconstruible cuando un tercero puede rehacer un número sin preguntar nada.
Hasta acá el repo tenía entrada, salida, fecha y dato de origen —lo necesario para *repetir*—
pero ninguna cuenta hecha delante del lector. Eso es lo que falta y lo que agrega esta página.

**Ninguno de estos números lo escribí a mano.** Todos salen de los archivos versionados, y
cualquiera los puede rehacer con los comandos de la última sección.

---

## Cómo leer las tablas

Cada fila es una cuenta: **de qué dato de la entrada sale**, qué operación se hace, qué da,
qué dice la salida archivada y cuánto se separan. El desvío es la columna que importa; si
alguna dejara de ser `0`, el repo estaría mintiendo en ese punto.

---

## Corrida 01 — 2026-W37

Entrada: [`01-2026-09-05-w37/entrada.md`](01-2026-09-05-w37/entrada.md) ·
salida: [`plan_semanal.json`](01-2026-09-05-w37/salida/plan_semanal.json)

| # | Cuenta | Operación | Resultado | Dice la salida | Desvío |
| --- | --- | --- | --- | --- | :-: |
| 1 | Rango de la semana | La entrada declara `2026-W37`. Semana ISO 8601 37 de 2026 → lunes y domingo | `2026-09-07 / 2026-09-13` | `"rango": "2026-09-07 / 2026-09-13"` | **0** |
| 2 | Fechas de las piezas | Las 5 `fecha` de la salida contra el rango de la fila 1 | 5 de 5 dentro | 08, 09, 10 de septiembre | **0** |
| 3 | La única cifra del plan | `63%` aparece en el cuerpo de 2 piezas. Buscarla literal en los activos que la entrada declara | `activos/sitio-home.md:42` — «\| **63%** \| Aumento de conversiones en Brasil vía SEO \|» | «an 63% increase in conversions in Brazil through SEO» | **0** |
| 4 | Costo de la corrida | [`consumo.json`](01-2026-09-05-w37/consumo.json) × tarifas de `COSTOS.md` §2 | `USD 6,102226` | `consumo.json` → `total.usd = 6.102226` | **0** |
| 5 | **Ids según R8** | El contrato manda `<canal>-<NN>`. 1 blog + 1 newsletter + 2 linkedin + 1 x → `blog-01, news-01, li-01, li-02, x-01` | los 5 ids de arriba | `translated-everywhere-cited-nowhere`, `news-w37-one-number-one-market`, `li-01`, `li-02`, `x-01` | **2 ids** |
| 6 | **Enlazado interno** | Cada `seo.enlazado_interno[].desde` tiene que ser el id de una pieza de este mismo plan | 7 enlaces, 7 válidos | 7 enlaces, **5 apuntan a `blog-01` y `blog-02`, que no existen en este plan** | **5 enlaces** |

**Las filas 5 y 6 no dan cero, y es el punto.** Ésta es la corrida donde el sistema falló, y su
salida se archiva sin retocar. Las dos filas son la medición exacta del hallazgo que
`DECISIONES.md` §8 cuenta en prosa: el validador de entonces salió con `exit 0` sobre un plan
con 5 de 7 enlaces rotos. De ahí salieron **R8** en el contrato y **C3** en el validador. La
cuenta de la fila 6 es la que hoy hace fallar a esa misma salida contra el validador actual.

---

## Corrida 02 — 2026-W38

Entrada: [`02-2026-09-05-w38/entrada.md`](02-2026-09-05-w38/entrada.md) ·
salida: [`plan_semanal.json`](02-2026-09-05-w38/salida/plan_semanal.json)

| # | Cuenta | Operación | Resultado | Dice la salida | Desvío |
| --- | --- | --- | --- | --- | :-: |
| 1 | Rango de la semana | Semana ISO `2026-W38` → lunes y domingo | `2026-09-14 / 2026-09-20` | `"rango": "2026-09-14 / 2026-09-20"` | **0** |
| 2 | Fechas de las piezas | Las 5 `fecha` contra el rango | 5 de 5 dentro | 15, 16, 17 de septiembre | **0** |
| 3 | La fecha citada en `blog-01` | La pieza dice «in March» por el post #9. Buscar ese post en el activo que la entrada declara | `activos/blog-indice.md:17` — «\| 9 \| "Guided Translation, Transcreation, and Creation: Understanding the Difference" \| A. Moreau \| 9 mar 2026 \|» | «We defined the three levels in March» | **0** |
| 4 | Reparto de firmas | `firma_autor` de las 2 piezas de blog contra la columna de autor del mismo activo | A. Moreau y D. Reyes, ambos firmas reales del índice | A. Moreau en `blog-01`, D. Reyes en `blog-02` | **0** |
| 5 | Costo de la corrida | [`consumo.json`](02-2026-09-05-w38/consumo.json) × tarifas de `COSTOS.md` §2 | `USD 7,699374` | `consumo.json` → `total.usd = 7.699374` | **0** |
| 6 | Ids según R8 | 2 blog + 2 linkedin + 1 x → `blog-01, blog-02, li-01, li-02, x-01` | los 5 ids de arriba | los mismos 5 | **0** |
| 7 | Enlazado interno | Cada `desde` tiene que existir como pieza | 8 enlaces, 8 válidos | 8 enlaces, 0 rotos | **0** |

**Cero cifras con `%` en los cuerpos de esta corrida.** No es un hueco de la medición: es el
plan que no usó ninguna. Lo que sí se puede rehacer son las dos afirmaciones verificables que
tiene —la fecha y las firmas—, y las dos cierran contra `activos/blog-indice.md`.

---

## Corrida 03 — 2026-W39 · configuración de producción

Entrada: [`03-2026-09-05-w39/entrada.md`](03-2026-09-05-w39/entrada.md) ·
salida: [`plan_semanal.json`](03-2026-09-05-w39/salida/plan_semanal.json)

| # | Cuenta | Operación | Resultado | Dice la salida | Desvío |
| --- | --- | --- | --- | --- | :-: |
| 1 | Rango de la semana | Semana ISO `2026-W39` → lunes y domingo | `2026-09-21 / 2026-09-27` | `"rango": "2026-09-21 / 2026-09-27"` | **0** |
| 2 | Fechas de las piezas | Las 5 `fecha` contra el rango | 5 de 5 dentro | 22, 23, 24 de septiembre | **0** |
| 3 | Las tres cifras de los cuerpos | `63%`, `147%` y `44%` buscadas literales en los activos que la entrada declara | `activos/sitio-home.md:42`, `:43`, `:44` | las tres, con su lectura | **0** |
| 4 | La cuarta cifra declarada | `cifras_usadas` declara además «21 dias» | `activos/sitio-home.md:41` — «\| **21 días** \| Northvale lanzó sitios en español y polaco \|» | «21 days» en `blog-01` y `news-01` | **0** |
| 5 | Costo de la corrida | [`consumo.json`](03-2026-09-05-w39/consumo.json) × tarifas de `COSTOS.md` §2 | `USD 4,042450` | `consumo.json` → `total.usd = 4.042450` | **0** |
| 6 | Costo de los 5 especialistas | Sólo el brazo Sonnet del mismo `consumo.json` | `USD 2,617293` | `COSTOS.md` §3 declara `2,6173` | **0** |
| 7 | Ids según R8 | 1 blog + 1 newsletter + 2 linkedin + 1 x → `blog-01, news-01, li-01, li-02, x-01` | los 5 ids de arriba | los mismos 5 | **0** |
| 8 | Enlazado interno | Cada `desde` tiene que existir como pieza | 3 enlaces, 3 válidos | 3 enlaces, 0 rotos | **0** |

La fila 6 es la que sostiene la proyección de `COSTOS.md` §6. Ahí la corrida completa vale
**`USD 3,1169`** — los `2,6173` medidos de esta fila más `0,50` proyectados de director — y el
año sale de **`3,1169 × 52 = 162,08 → ≈ USD 162`**. El único término proyectado de esa cuenta
es el `0,50`, y está declarado como tal; los `2,6173` son medición.

---

## La cuenta que decide la elección de modelo

Es la única cifra económica que no sale de una de las tres corridas, así que se rehace aparte.
Los tres brazos del banco corrieron **dentro de la ventana de la corrida 02**, cada uno como un
subagente con transcript propio, y por eso cada uno se mide solo.

| Brazo | Entrada + caché × tarifas de §2 | USD | `COSTOS.md` §4 | Desvío |
| --- | --- | ---: | ---: | :-: |
| Haiku 4.5 | 3 llamadas · 52.064 escr. 5 min · 80.232 lect. · 448 salida | 0,075369 | 0,0754 | **0** |
| Sonnet 5 | 13 llamadas · 91.426 escr. 5 min · 776.675 lect. · 8.285 salida | 0,466802 | 0,4668 | **0** |
| Opus 5 | 15 llamadas · 57.493 escr. 5 min · 990.446 lect. · 19.078 salida | 1,331654 | 1,3317 | **0** |

**La razón que decide:** `1,331654 / 0,466802 = 2,853`. Sonnet pasa los nueve criterios por
**2,85× menos** que Opus, y por eso es el modelo de producción.

**Ninguno de los tres brazos escribió caché con TTL de 1 hora** (`cache_w_1h = 0` en los tres).
Por eso los tres costos son idénticos antes y después de la corrección T4: la comparación de
modelos, que es de donde sale la decisión, no depende de ese arreglo.

---

## Cómo rehacer todo esto

Las filas de costo salen del `consumo.json` archivado de cada corrida, que es el consumo que
la API facturó, no una estimación:

```bash
python3 herramientas/costo.py --desde 2026-09-05T21:36:08Z --hasta 2026-09-05T21:54:26Z  # 01
python3 herramientas/costo.py --desde 2026-09-05T21:57:24Z --hasta 2026-09-05T22:19:25Z  # 02
python3 herramientas/costo.py --desde 2026-09-05T22:20:40Z --hasta 2026-09-05T22:54:42Z  # 03
```

Las filas de ids y de enlazado interno son los controles **C2** y **C3** de `validar.py`, que
corren sobre las tres salidas archivadas:

```bash
python3 herramientas/validar.py corridas/02-2026-09-05-w38/salida/plan_semanal.json  # exit 0
python3 herramientas/validar.py corridas/01-2026-09-05-w37/salida/plan_semanal.json  # exit 1
```

**Que la corrida 01 salga con `exit 1` es el resultado esperado**, no un repo roto: es la fila
6 de su tabla, y está declarado en `metadata.json` (`validador: exit 0` con el de entonces,
`validador_actual: exit 1`) y en `DECISIONES.md` §8.

Las filas de fechas y de ids no necesitan ninguna herramienta: son la semana ISO y un conteo
por canal, y se hacen a mano contra el JSON archivado.
