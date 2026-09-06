# Corrida 02 — semana 2026-W38

**Fecha de ejecución:** 2026-09-05 · **Contrato:** v2 · **Schema:** v3
**Modelo:** `claude-opus-5` — **deliberadamente el mismo que la corrida 01.**

## Diseño del experimento

Contra la corrida 01 cambia **una sola variable: el contrato (v1 → v2)**. Mismo modelo,
misma arquitectura, mismo equipo, mismas herramientas. Si el resultado mejora, la mejora es
atribuible al contrato y no al modelo. La elección de modelo se prueba aparte, en el banco
de `COSTOS.md`, para no mezclar dos causas — que es exactamente el riesgo que el editor-qa
señaló en la corrida 01.

## Qué cambió en el contrato v2

| Cambio | Origen |
| --- | --- |
| **R8 · convención de ids compartida** (`blog-01`, `news-01`, `li-01`, `x-01`) | Falla F1 de la corrida 01: la ola 2 en paralelo inventó dos esquemas de nombres |
| **Schema v3: `piezas[].firma_autor`** | El editor-qa detectó que el reparto de firmas no era registrable en la salida |
| **Control C3 en `validar.py`** | La misma F1: el validador la dejaba pasar con exit 0 |
| **`herramientas/render.py`** | Falla F2: faltaba `plan.md`. Ahora se genera del JSON y no puede derivar |

## Brief enviado (el user prompt de esta corrida)

```
Armá el plan de contenidos para la semana 2026-W38 (2026-09-14 / 2026-09-20).

CONTEXTO DE ESTA SEMANA
  Disparador:        El sitio vende tres niveles de adaptación — Guided Translation,
                     Guided Transcreation y Guided Creation — pero el único contenido
                     que los explica es de marzo (activos/blog-indice.md #9) y solo define
                     la diferencia. Nadie contó todavía CÓMO SE DECIDE cuál usar en cada
                     mercado, que es la pregunta real de quien tiene que repartir un
                     presupuesto finito entre 12 mercados.
  Público objetivo:  Heads of localization y content ops leads que rinden cuentas de un
                     presupuesto de contenido multimercado y hoy lo reparten parejo por
                     falta de un criterio defendible.
  Objetivo:          Autoridad y consideración. Instalar el criterio de asignación como
                     territorio de Acme.
  CTA:               https://www.acme-multilingual.example/contact-us/
  Pilar sugerido:    que lo elija el estratega y justifique por qué.

RESTRICCIONES DE ESTA SEMANA
  No repetir el ángulo de descubribilidad en IA de la semana 37: es la semana anterior.
  El post #9 ya definió los tres niveles. No volver a definirlos: hay que dar el criterio
  de elección, que es el paso que falta.

ENTREGA
  corridas/02-2026-09-05-w38/salida/plan_semanal.json y .../plan.md
  Correr python3 herramientas/validar.py sobre el JSON antes de terminar.
  Si el validador falla, arreglar el JSON — no tocar el validador ni el schema.
```

## Hipótesis anotadas antes de correr

1. **R8 resuelve F1.** Los ids van a coincidir entre el redactor, social y SEO, y el control
   C3 va a salir en verde. Es la hipótesis principal de esta corrida.
2. El ángulo de esta semana es **prescriptivo** (un criterio de decisión), no descriptivo.
   El sistema no tiene ningún activo que respalde un criterio de asignación:
   espero muchos más `[DATO FALTANTE]` que en la corrida 01, o una violación de R1.
3. `firma_autor` existe ahora en el schema, pero **el contrato no dice quién lo llena.**
   Puede quedar en `null` en todas las piezas: el campo existe y nadie lo usa.
