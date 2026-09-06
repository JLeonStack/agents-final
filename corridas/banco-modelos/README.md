# Banco de pruebas de modelo

**Diseño.** La misma tarea (el contrato de `redactor-contenido`, semana 2026-W38), el mismo
contrato v2, el mismo `contexto/marca.md`, la misma invocación palabra por palabra. Única
variable: el modelo. Los criterios de aprobación se declararon **antes** de correr y están
en `COSTOS.md` §4.

| Archivo | Modelo | Costo medido | Veredicto |
| --- | --- | ---: | --- |
| `salida-haiku-4-5.md` | `claude-haiku-4-5` | USD 0,0754 | **falla 3 de 9 criterios** |
| `salida-sonnet-5.md` | `claude-sonnet-5` | USD 0,4668 | pasa 9 de 9 — **elegido** |
| `salida-opus-5.md` | `claude-opus-5` | USD 1,3317 | pasa 9 de 9 |

**Nota sobre el brazo de Opus:** no se corrió por separado. Es la salida del redactor de la
corrida 02, que usó **exactamente el mismo prompt y el mismo contrato**. Reutilizarla en vez
de duplicar la corrida es deliberado y se declara acá para que nadie lo lea como una corrida
independiente que no existió.

**Invocación, idéntica en los tres brazos** (solo cambió el modelo):

> Leé completos `prompts/system_prompt.md` (contrato del director v2, restricciones R1-R8) y
> `prompts/agentes/redactor-contenido.md` (TU contrato). Leé `contexto/marca.md` fresco y
> completo. Ahí está el ángulo de la semana 2026-W38, ya aprobado. Ejecutá tu tarea para la
> semana 2026-W38 (2026-09-14 / 2026-09-20). CTA: https://www.acme-multilingual.example/contact-us/
> NO escribas ningún archivo. NO leas la carpeta `corridas/`.
