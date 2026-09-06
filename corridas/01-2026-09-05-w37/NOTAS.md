# Corrida 01 — notas del director

**Resultado:** el sistema corrió punta a punta. `validar.py` sale con exit 0.
**`apto_para_firma: false`** — y ese es el resultado correcto, no una falla.

## Contraste con las hipótesis anotadas antes de correr

| # | Hipótesis | Qué pasó |
| --- | --- | --- |
| 1 | «Puede salir un plan desbalanceado (4 de blog, 0 de redes)» | **No pasó.** Salieron 1 blog + 1 newsletter + 2 LinkedIn + 1 X. El reparto se resolvió solo porque cada especialista tiene su canal asignado por contrato — el balance no lo produjo el director, lo produjo la división del trabajo |
| 2 | «`contexto/marca.md` es el punto único de falla» | **Confirmado como punto único, pero funcionó.** Los tres agentes de la ola 2 citaron sus secciones (§4 territorio prohibido, §5 cifras, §7 ángulo, §8 instrucciones). El estratega dejó ahí una advertencia que los tres respetaron, sin hablar entre ellos. **El archivo compartido funcionó como el mecanismo de coordinación que la conversación no puede dar** |
| 3 | «`calendario.csv` con 5 filas puede ser insuficiente para R6» | **Confirmado.** El editor-qa: R6 no es concluyente para 4 de las 5 piezas, porque el calendario solo registra piezas de blog |

## Las tres fallas reales que encontró esta corrida

### F1 · Convención de ids inconsistente entre agentes paralelos (bloqueante)

El redactor nombró sus piezas `translated-everywhere-cited-nowhere` y
`news-w37-one-number-one-market`. El analista SEO enlazó a `blog-01` y `blog-02`.
**5 de las 7 entradas de `enlazado_interno` apuntan a piezas que no existen**, y `blog-02`
además presupone un segundo post de blog que el plan no tiene.

Causa raíz: el contrato v1 define el formato de cada especialista **por separado**, pero la
ola 2 corre **en paralelo**, y nada fija el espacio de nombres compartido. Cada uno inventó
el suyo, coherente consigo mismo.

**Lo que más importa de esta falla: `validar.py` la dejó pasar con exit 0.** El schema valida
cada campo, no las relaciones entre campos.

### F2 · Faltaba el segundo entregable

El §5 exige `plan_semanal.json` **y** `plan.md`. Yo, como director, produje solo el JSON.
Lo detectó el editor-qa, no el validador.

### F3 · El medidor de costo medía mal

Al deduplicar por `requestId` me quedaba con el primer bloque de streaming, que trae el
contador de salida incompleto, y no escaneaba los transcripts de los subagentes.
**Resultado antes de arreglarlo: USD 1,41. Resultado real: USD 5,97.** Subestimaba 4,2x.

## Lo que el editor-qa vio y ninguna herramienta puede ver

> «La tesis central de la semana no tiene respaldo en ningún archivo de `activos/`. Las cinco
> piezas la afirman en indicativo. No es violación formal de R1, y `validar.py` no lo puede
> ver; pero sostiene el peso de todo el plan y hoy solo la respalda `contexto/marca.md`,
> que lo produjo el propio sistema.»

Es el hallazgo más importante de la corrida: **el sistema puede generar una tesis, escribirla
en su propio documento de contexto, y después citarse a sí mismo como fuente.** La trazabilidad
mecánica (C1, C2) no distingue una fuente externa de una que el sistema fabricó. Va a
`GOBIERNO.md` como modo de falla.

## Revisión humana efectivamente realizada

- Aprobé `contexto/marca.md` antes de la ola 2 (punto L2 del contrato). Lo leí: 285 líneas,
  9 secciones, 6 `[DATO FALTANTE]` anticipados.
- Corrí `validar.py` yo mismo en vez de confiar en que el subagente decía que pasaba.
- Verifiqué en disco que los artefactos que los subagentes decían haber escrito existieran.
