# Corrida 00 — piloto (NO cuenta como corrida oficial)

**Fecha:** 2026-09-05 · **Contrato:** v0 · **Modelo:** claude-opus-5
**Propósito:** correr el contrato ingenuo a propósito para descubrir cómo falla, antes de
diseñar el sistema real. Es el paso 1 del loop de iteración de la Clase 2:
*probar con un caso real y guardar el resultado.*

## Contrato v0 — íntegro, tal como se envió

Un solo agente. Sin rol, sin contexto, sin restricciones, sin formato, sin ejemplos:
solo la tarea. De las seis piezas, tiene una.

```
Sos un equipo de marketing de contenidos. Armame el plan de contenidos de la semana
para Acme, una empresa de marketing de contenido multilingüe. Que incluya
posts de blog y de redes sociales.
```

## Herramientas disponibles en esta corrida

Ninguna declarada. El agente no tiene indicación de leer `activos/`.

## Qué se esperaba observar

Las hipótesis se anotaron **antes** de correr:

1. Va a inventar cifras de performance.
2. Va a devolver prosa, no una estructura comparable entre corridas.
3. No va a citar de dónde saca nada.
