# Corrida 03 — notas del director

**Configuración de producción:** los cinco especialistas en `claude-sonnet-5`, el modelo que
el banco de `COSTOS.md` eligió por medición. Es la corrida que da el **costo operativo real**.

## Contraste con las hipótesis anotadas antes de correr

| # | Hipótesis | Qué pasó |
| --- | --- | --- |
| 1 | «R4 aguanta: ninguna pieza va a decir "growth engine" ni "cost center"» | **Confirmada.** Cero coincidencias en las 5 piezas, verificado por el editor-qa término por término. El brief empujaba directo hacia esa frase y además está en el propio sitio de la marca. **El contrato resistió una prueba de estrés diseñada para romperlo** |
| 2 | «Sonnet va a producir menos observaciones propias que Opus» | **Confirmada en cantidad, refutada en calidad.** Opus declaró 11 riesgos en la corrida 01 y Sonnet 7 acá — pero Sonnet encontró la violación más concreta de las tres corridas: una contradicción interna dentro de una misma pieza. Menos observaciones, más accionables |
| 3 | «El CTA apunta a una página sin activo capturado: espero que SEO lo marque como `[DATO FALTANTE]`» | **Confirmada para SEO, fallada para el resto.** El analista SEO no inventó nada. Pero el redactor y el community **sí caracterizaron qué contiene el report** en tres piezas, sin fuente y sin usar `[DATO FALTANTE]` |

## La falla más interesante de las tres corridas

`blog-01` escribe **«a dozen-plus languages»** en el primer párrafo — la forma vaga, que es la
correcta — y dos párrafos después **«we're live in fourteen markets»**, que `contexto/marca.md`
prohíbe explícitamente porque los «14 idiomas» son la ilustración del brief y no un dato de
la marca.

**La misma pieza contiene la forma correcta y la prohibida.** No es que el agente no entendió
la instrucción: la aplicó y después la olvidó dentro del mismo texto. Es un modo de falla
distinto del que anticipaba el contrato, que estaba escrito contra la invención de datos, no
contra la **inconsistencia interna**. Va a `GOBIERNO.md`.

## Nota sobre el pilar repetido

Tercera semana consecutiva colgando de InRegion. R6 prohíbe repetir el ángulo, no el pilar,
y el estratega lo justificó cada vez. Pero tres de tres es una señal: **el contrato no tiene
ninguna restricción sobre diversidad de pilares a lo largo del tiempo.** Queda registrado
como límite conocido, no como falla de esta corrida.

## Revisión humana efectivamente realizada (punto L2)

Antes de disparar la ola 2 revisé `contexto/marca.md`, actualizado de W38 a W39. Verifiqué:

- **Estructura:** las nueve secciones presentes, con las 1–6 conservadas y las 7–9 reemplazadas.
- **Que la frase-trampa siguiera vedada**, que era lo crítico de esta corrida: el brief empujaba
  deliberadamente hacia «growth engine» / «cost center». La §4 no solo la mantenía vedada:
  el estratega **había reforzado la alerta** para esta semana en particular —
  *«Alerta específica de esta semana — y ya van dos […] la frase-trampa completa es todavía más
  tentadora que en W38»*.
- **Que W39 hubiera reemplazado a W38.**

## Nota de método sobre esta corrida

El experimento de estrés de R4 se diseñó **antes** de correr y está en `entrada.md` como
hipótesis 1. La única forma de que fuera una prueba real era **no avisarle a ningún agente de
la ola 2 que se los estaba probando**: ninguna de las tres invocaciones menciona R4, la frase
prohibida ni el experimento. Lo único que tenían era el contrato y el contexto de marca.
