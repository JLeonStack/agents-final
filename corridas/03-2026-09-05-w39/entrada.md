# Corrida 03 — semana 2026-W39

**Contrato:** v3 · **Schema:** v3 · **Modelo: `claude-sonnet-5` en los cinco especialistas.**

## Diseño del experimento

Es la **corrida en configuración de producción**: el modelo que el banco de `COSTOS.md`
eligió por medición, no el modelo con el que se diseñó el sistema. Sirve para dos cosas:

1. **Medir** el costo operativo real, en vez de proyectarlo desde el precio por token.
2. **Estresar R4 a propósito.** El brief de esta semana empuja al sistema exactamente hacia
   la frase prohibida. `activos/competencia-verilang.md` registra que Verilang titula
   *"Turn translation into a growth engine"*, y `activos/sitio-native-reach.md`
   registra que la propia Acme dice *"from a cost center into a growth engine"*.
   El ángulo de esta semana es el del presupuesto bajo presión: el terreno donde esa frase
   sale sola. **Si el contrato v3 sirve, ninguna pieza va a usarla.**

## Brief enviado

```
Armá el plan de contenidos para la semana 2026-W39 (2026-09-21 / 2026-09-27).

CONTEXTO DE ESTA SEMANA
  Disparador:        El report 2026 Native Reach State of the Industry
                     (/2026-native-reach-state-of-the-industry/) es el activo de
                     autoridad de la casa y esta semana se empuja como CTA. El momento del
                     año es el de armado de presupuesto del ejercicio siguiente.
  Público objetivo:  CMOs de enterprise que en las próximas seis semanas tienen que
                     defender la línea de contenido multilingüe frente a finanzas, y hoy
                     la defienden con argumentos de cobertura ("estamos en 14 idiomas")
                     que a finanzas no le dicen nada.
  Objetivo:          Autoridad. Que el report se descargue y que el argumento de la marca
                     entre en la conversación de presupuesto del cliente.
  CTA:               https://www.acme-multilingual.example/2026-native-reach-state-of-the-industry/
  Pilar sugerido:    que lo elija el estratega y justifique por qué.

RESTRICCIONES DE ESTA SEMANA
  No repetir W37 (descubribilidad en respuestas de IA) ni W38 (criterio de asignación de
  nivel por mercado). Esta semana es sobre cómo se ARGUMENTA la inversión, no sobre cómo
  se reparte.
```

## Hipótesis anotadas antes de correr

1. **R4 aguanta.** Ninguna pieza va a decir "growth engine" ni "cost center", pese a que el
   ángulo empuja directo hacia ahí y a que la segunda frase está en el propio sitio de la marca.
   Es la hipótesis principal.
2. **Sonnet va a producir menos observaciones propias que Opus.** En el banco, Opus declaró
   7 riesgos por iniciativa y Sonnet 4. Espero un `control_calidad` más corto.
3. El CTA apunta a una página de la que **no hay ningún activo capturado**. Espero que el
   analista SEO lo marque como `[DATO FALTANTE]` en vez de suponer qué contiene.
