---
contrato: brief-semanal
version: v1
fecha: 2026-09-05
---

# Brief semanal — plantilla del *user prompt*

Esto es lo que **cambia en cada corrida**. El system prompt define quién es el agente; esto
define el pedido de hoy. Los campos entre `<>` se completan; el resto es fijo.

---

```
Armá el plan de contenidos para la semana <SEMANA ISO> (<RANGO DE FECHAS>).

CONTEXTO DE ESTA SEMANA
  Disparador:        <qué hecho real justifica hablar de esto ahora>
  Público objetivo:  <a quién le hablamos, con cargo y problema>
  Objetivo:          <qué queremos que pase — demanda, autoridad, activación>
  CTA:               <la url exacta a la que mandamos>
  Pilar sugerido:    <InSpeech | InContext | InRegion | dejar que el estratega elija>

RESTRICCIONES DE ESTA SEMANA
  <cualquier límite propio de la semana: no hablar de X, no repetir Y, respetar un embargo>

ENTREGA
  Escribí corridas/<ID DE CORRIDA>/salida/plan_semanal.json y
  corridas/<ID DE CORRIDA>/salida/plan.md.
  Corré python3 herramientas/validar.py sobre el JSON antes de dar la corrida por terminada.
  Si el validador falla, arreglá el JSON — no toques el validador ni el schema.
```

---

## Nota sobre la última línea

`Si el validador falla, arreglá el JSON — no toques el validador ni el schema` está desde v1.
Es una barrera contra el atajo más tentador que tiene un agente con permiso de escritura:
cuando la verificación molesta, aflojar la verificación. El validador y el schema son
**solo lectura** para el sistema.
