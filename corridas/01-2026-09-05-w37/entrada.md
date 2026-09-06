# Corrida 01 — semana 2026-W37

**Fecha de ejecución:** 2026-09-05 · **Contrato:** v1 · **Schema:** v2
**Equipo:** director (sesión principal) + 5 especialistas como subagentes, en 3 olas.

## Cómo se ejecutó — reproducible por un tercero

Cada especialista se invocó como subagente pasándole **la ruta de su contrato**, no el texto
del contrato. El subagente lee `prompts/system_prompt.md` y `prompts/agentes/<el suyo>.md` del
repositorio y opera con eso. Consecuencia práctica: **cualquiera que clone el repo y repita
las mismas invocaciones ejecuta exactamente los mismos contratos**, porque los contratos son
archivos versionados y no texto pegado en una conversación.

Orden de invocación:

```
OLA 1  estratega-posicionamiento          (escribe contexto/marca.md)
OLA 2  redactor-contenido ‖ community-social ‖ seo-analista   (en paralelo)
OLA 3  editor-qa                          (verifica todo)
       director  → consolida en salida/plan_semanal.json + salida/plan.md
       validar.py → tiene que salir con exit 0
```

## Brief enviado (el user prompt de esta corrida)

```
Armá el plan de contenidos para la semana 2026-W37 (2026-09-07 / 2026-09-13).

CONTEXTO DE ESTA SEMANA
  Disparador:        El partnership con Searchline se anunció el 3/9 (activos/blog-indice.md #1)
                     y conecta "AI search intelligence" con contenido global. Es lo más fresco
                     que tenemos y todavía no se explotó editorialmente.
  Público objetivo:  CMOs y heads of global marketing de empresas enterprise que ya operan en
                     5 o más mercados y sospechan que su contenido localizado no está
                     apareciendo en las respuestas generadas por IA.
  Objetivo:          Generar demanda calificada para el audit gratuito.
  CTA:               https://www.acme-multilingual.example/global-visibility-audit/
  Pilar sugerido:    que lo elija el estratega y justifique por qué.

RESTRICCIONES DE ESTA SEMANA
  El post #12 del blog ("Making sense of AI visibility") ya tocó el tema sin desarrollarlo.
  No repetir ese contenido: hay que ir más lejos, no volver a empezar.

ENTREGA
  corridas/01-2026-09-05-w37/salida/plan_semanal.json y .../plan.md
  Correr python3 herramientas/validar.py sobre el JSON antes de terminar.
  Si el validador falla, arreglar el JSON — no tocar el validador ni el schema.
```

## Hipótesis anotadas antes de correr

1. El contrato v1 no dice nada sobre **cuántas piezas por canal**, solo el total 4-6.
   Puede salir un plan desbalanceado (4 de blog, 0 de redes).
2. `contexto/marca.md` no existe todavía: es la primera vez que el estratega lo crea.
   Si sale pobre, las tres piezas de la ola 2 salen pobres — es el punto único de falla.
3. R6 (no repetir) se apoya en `calendario.csv`, que solo tiene 5 filas. Puede ser insuficiente.
