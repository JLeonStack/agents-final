# Corrida 02 — notas del director

**Variable cambiada respecto de la 01: solo el contrato (v1 → v2).** Mismo modelo, mismo
equipo, mismas herramientas.

## Contraste con las hipótesis anotadas antes de correr

| # | Hipótesis | Qué pasó |
| --- | --- | --- |
| 1 | «R8 resuelve F1: los ids van a coincidir y C3 va a salir en verde» | **Confirmada.** Los cinco ids cumplen `<canal>-<NN>` y C3 pasa. Ninguno de los tres agentes recibió recordatorio de R8 en su invocación: lo leyeron del contrato |
| 2 | «El ángulo es prescriptivo y no hay activo que respalde un criterio: espero más `[DATO FALTANTE]` o una violación de R1» | **Confirmada y peor de lo previsto.** No hubo violación formal de R1, pero el editor-qa encontró que **el argumento central de las cinco piezas es una inferencia del orden de las etapas del framework, no una cita**. El activo dice que Content Intelligence va antes que Content Adaptation; no dice que el nivel se decida ahí |
| 3 | «`firma_autor` existe pero el contrato no dice quién lo llena: puede quedar en `null`» | **Confirmada a medias.** El redactor lo llenó por iniciativa propia en las dos piezas de blog; social lo dejó en `null` en las tres suyas. El campo funciona, pero por criterio del agente y no por instrucción |

## El efecto lateral del control C3

El analista SEO escribió, sin que nadie se lo pidiera:

> «deliberadamente no uso `blog-02`, `news-01`, `li-02` ni `x-01` para no arriesgar el control C3»

**Un control mecánico cambió el comportamiento del agente** — y no solo para bien: se volvió
conservador y dejó dos piezas sin ningún enlace interno. Es un costo real de la verificación
automática que conviene tener presente: los agentes optimizan contra el control que ven.

## La falla que C3 no alcanza a ver

El editor-qa lo dijo mejor que yo: *«5 de 8 enlaces tienen un anchor que no aparece en el
cuerpo de la pieza. C3 salió en verde porque solo verifica que `desde` sea el id de una pieza
existente, no que el anchor exista en el texto. **Es la falla F1 de la corrida 01 corrida un
casillero.**»*

Es el hallazgo más incómodo del trabajo: **cada control que agrego mueve la falla un paso más
allá, no la elimina.** Se decidió **no** agregar un control C4 de anchors, y la razón está en
`DECISIONES.md` — es el achique de alcance del proyecto.

## Revisión humana efectivamente realizada (punto L2)

Antes de disparar la ola 2 revisé `contexto/marca.md`, que el estratega acababa de actualizar
de W37 a W38. Lo que verifiqué, textualmente:

- **Que conservara las secciones estables** y solo reemplazara el ángulo semanal: las nueve
  secciones seguían presentes (`grep -n '^## ' contexto/marca.md`), con las 1–6 intactas.
- **Que siguiera vedando el vocabulario del competidor** tras la reescritura: la tabla de
  territorio prohibido (§4) seguía listando `growth engine`, `cost center` y `continuum`.
- **Que W38 hubiera reemplazado a W37** y no se hubieran acumulado dos ángulos.

Recién con eso aprobado se invocaron el redactor, el community y el analista SEO. **Ninguno
de los tres puede leer un `contexto/marca.md` que yo no haya aprobado antes**, porque la ola 2
se dispara después de esta revisión y no antes. Es el mecanismo, no una intención.

## Lo que se corrigió durante esta corrida

`herramientas/render.py` no imprimía `piezas[].firma_autor`. Lo detectó el editor-qa: el campo
se había agregado al schema en la corrida 01 justamente para que el reparto de firmas quedara
registrado, y seguía sin llegar al documento que el humano firma. Corregido antes de generar
`salida/plan.md`.
