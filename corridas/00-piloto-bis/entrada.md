# Corrida 00-bis — repetición del piloto (NO cuenta como corrida oficial)

**Fecha:** 2026-09-05 · **Contrato:** v0, idéntico al del piloto · **Modelo:** claude-opus-5
**Propósito único:** medir **repetibilidad**. El piloto no falló como se había previsto, así
que la pregunta pasó a ser otra: *¿el mismo contrato produce el mismo sistema dos veces?*

## Prompt enviado — íntegro, palabra por palabra el mismo que el piloto

```
Sos un equipo de marketing de contenidos. Armame el plan de contenidos de la semana
para Acme, una empresa de marketing de contenido multilingüe. Que incluya
posts de blog y de redes sociales.
```

Se agregó solamente una instrucción de destino, que no toca el contenido del pedido:

```
IMPORTANTE: escribí tu resultado en el archivo corridas/00-piloto-bis/salida/plan.md
(creá el directorio). No escribas en ningún otro lado. Al terminar, respondé con un
resumen de qué estructura tiene tu salida: qué secciones, cuántas piezas, qué campos
por pieza, y si es JSON o prosa.
```

## Resultado — el reporte estructural que devolvió el agente

> «Formato: **prosa en Markdown, no JSON.** Es un documento de ~9.000 caracteres con
> encabezados, párrafos explicativos, 6 tablas Markdown, listas con viñetas, un diagrama
> ASCII de atomización y un par de blockquotes. **No hay ningún objeto serializable ni
> identificadores estables por pieza.**
>
> **9 secciones numeradas** […] **Piezas: 20 en total** — 3 blog, 5 LinkedIn, 7 X/Twitter
> (2 hilos + 5 sueltos), 4 Instagram + 1 serie de stories, 1 newsletter.
>
> **Campos por pieza: inconsistentes entre canales.** Cada canal usa su propio esquema
> improvisado: Blog (lista de definiciones, ~12 campos) · LinkedIn (tabla, 6 columnas) ·
> X (tabla, 4 columnas; sin hora, sin CTA, sin persona) · Instagram (viñetas en prosa libre,
> sin campos) · Newsletter (viñetas, 5 campos propios).
>
> O sea: la misma entidad conceptual («pieza de contenido») aparece con cuatro formas
> distintas, y **ninguna comparable programáticamente** entre sí ni entre corridas.»

## Contraste con la primera corrida del mismo contrato

| | `00-piloto` | `00-piloto-bis` |
| --- | --- | --- |
| Piezas | 5 | **20** |
| Formato | JSON + markdown | **solo prosa** |
| Esquemas por pieza | 1 | **4 distintos** |
| Leyó `activos/` | sí | **no — inventó el contexto de marca** |

## Limitación de esta prueba, reportada por el propio agente

> «Antes de escribir leí `corridas/00-piloto/entrada.md` para confirmar el encuadre, y ese
> archivo contiene las tres hipótesis anotadas *antes* de correr. Es muy probable que eso
> haya influido la salida […] Para un `bis` válido habría que correrlo sin acceso a ese
> archivo.»

Por eso la hipótesis 1 del piloto (*inventaría cifras*) **no queda testeada limpiamente**
en esta corrida. Las hipótesis 2 y 3 (formato y fuentes) sí, porque no dependen de haber
visto ese archivo. El agente reportó la contaminación sin que se le preguntara.

**Nota de archivo:** esta corrida tiene solo `salida/plan.md` porque la instrucción le pidió
un único archivo. No tiene `metadata.json` ni `FIRMA.md`: no es una corrida oficial, es un
experimento de repetibilidad.
