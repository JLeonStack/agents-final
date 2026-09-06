# Plan de contenidos — Acme · semana 2026-W37

**Rango:** lunes 2026-09-07 → domingo 2026-09-13
**Generado:** 2026-09-05T21:26:06Z · **Modelo:** claude-opus-5
**Estado:** borrador · **`apto_para_firma`: false** — requiere firma humana antes de publicar

---

## Ángulo de la semana

**La brecha de descubrimiento: invisible en IA fuera del mercado principal**

Una marca puede estar perfectamente traducida y aun así no aparecer en las respuestas generadas
por IA de su segundo mercado. Eso no es un problema de traducción: es un problema de marketing,
y se resuelve **InRegion**.

**Por qué este ángulo, esta semana:**

| Razón | Evidencia |
| --- | --- |
| Es el activo más fresco de la marca | Partnership con Searchline sobre *AI search intelligence*, publicado el 3 sep 2026 (`activos/blog-indice.md`) |
| Hay un hueco de contenido abierto | La entrada #12 del blog, "Making sense of AI visibility", plantea que "AI-generated answers are changing how visibility works" y no está desarrollada |
| Tiene un CTA real detrás | `/global-visibility-audit/` — Free Global Visibility Audit (`activos/sitio-home.md`) |
| Es territorio propio, no de la competencia | Verilang parte de *traducción* y sube hacia marketing; Acme parte de *marketing* y baja hacia idioma (`activos/competencia-verilang.md`) |
| El último post de opinión es del 7 ago | Desde entonces solo hubo dos posts de partnership (`activos/calendario.csv`) |

**Pilar Native Reach:** InRegion
**Público:** CMOs y responsables de marketing global en enterprise que ya publican en varios
idiomas y no saben si aparecen en las respuestas de IA de cada mercado.
**CTA de la semana:** Free Global Visibility Audit — `acme-multilingual.example/global-visibility-audit/`

---

## Calendario de publicación

> El esquema `plan_semanal.schema.json` no admite fecha por pieza (`additionalProperties: false`).
> El calendario vive acá. Es una costura conocida: ver `riesgos` en el JSON.

| Día | Canal | Pieza | Firma sugerida |
| --- | --- | --- | --- |
| Lun 08:00 | LinkedIn | `linkedin-competencia-local` — siembra la tesis | D. Reyes |
| **Mar** | **Blog** | `blog-invisible-en-respuestas-ia` — pieza pilar | D. Reyes |
| Mié | X | `x-hilo-traducido-pero-invisible` — hilo de 6 | cuenta de marca |
| **Jue** | **Blog** | `blog-auditoria-cuatro-preguntas` — pieza práctica | A. Moreau |
| Jue 08:00 | LinkedIn | `linkedin-gramatica-vs-contexto` — acompaña el post | A. Moreau |

Las firmas siguen el reparto observado en el blog: Reyes en SEO y estrategia,
Moreau en localización y cultura (`activos/blog-indice.md`).

**Nota de idioma:** las piezas están redactadas en inglés porque acme-multilingual.example publica en
inglés. El marco estratégico y el control de calidad van en español, que es el idioma de trabajo
del equipo.

---

## Las cinco piezas

### 1 · Blog (martes) — pieza pilar

**"Why Your Brand Is Invisible in AI Answers Outside Your Home Market"**

Argumento: los motores de respuesta no rankean páginas, ensamblan una respuesta desde las fuentes
que consideran creíbles para la pregunta *tal como se formuló* — en el idioma local, contra
competidores locales. Una traducción literal hereda la pregunta en inglés que la página original
respondía. Si nadie en ese mercado pregunta así, la página es correcta e invisible a la vez.

Cierra con un test de tres pasos sobre el segundo mercado por facturación.

Enlaza a `/native-reach/`, a "Global SEO in 2026: What Changed" y a "How Content
Strategy Impacts International SEO Performance".

### 2 · Blog (jueves) — pieza práctica

**"The Discoverability Audit: Four Questions for Every Market You Publish In"**

Cuatro preguntas, una por sección: qué pregunta hace el comprador local, quién posee hoy esa
respuesta, si la página respeta el contexto o solo la gramática, y si se puede medir la
aparición. Aterriza en el Free Global Visibility Audit.

### 3 · LinkedIn (lunes) — D. Reyes

**"Your German site is not competing with your English site"** — siembra la tesis un día antes
del post pilar y cierra con pregunta abierta.

### 4 · X (miércoles) — hilo de 6

**"Traducido a la perfección y aun así invisible"** — versión comprimida del argumento pilar,
con el test de tres preguntas en el tuit 5.

### 5 · LinkedIn (jueves) — A. Moreau

**"Grammatically native, culturally foreign"** — el modo de falla que no aparece en un score de
QA. Acompaña el segundo post de blog.

El texto completo de las cinco piezas está en `plan_semanal.json`, campo `cuerpo`.

---

## SEO

- **Keyword principal:** `multilingual AI search visibility`
- **Secundarias:** AI discoverability · international SEO · Native Reach ·
  global content strategy · AI answer engines · multilingual content strategy
- **Enlazado interno:** 5 enlaces declarados en el JSON, todos hacia URLs que aparecen en
  `activos/sitio-home.md` o `activos/blog-indice.md`.

---

## Control de calidad — leer antes de firmar

### Cifras usadas (2)

| Cifra | Redacción exacta de la fuente | Fuente |
| --- | --- | --- |
| 63% | "Aumento de conversiones en Brasil vía SEO" | `activos/sitio-home.md` |
| 147% | "Más conversiones a través de contenido localizado" | `activos/sitio-home.md` |

Ninguna otra cifra aparece en las piezas. Verificado por `herramientas/validar.py` (control C2).

### Datos faltantes (6)

1. **Alcance real del Free Global Visibility Audit** — mercados, entregable, plazo. No está
   en `activos/`. Afecta el CTA de las dos piezas de blog.
2. **Contenido del post de Searchline** (3 sep 2026) — solo hay titular y una línea. No se puede
   describir la mecánica de la integración.
3. **Contexto de 63% y 147%** — la fuente no da cliente, período ni línea de base.
4. **Métricas de posts anteriores** — no hay analítica en `activos/`. La cadencia y el formato son
   criterio editorial, no dato.
5. **`activos/calendario.csv` solo tiene piezas publicadas**, ninguna planificada. No se pudo
   verificar colisión con contenido ya comprometido para la semana 37.
6. **Autor y fecha de "Making sense of AI visibility"** — sin datos en el índice. No se enlaza.

### Riesgos (6)

1. **Canibalización** con "Global SEO in 2026: What Changed" y "How Content Strategy Impacts
   International SEO Performance". Se diferencian por el eje de respuestas generadas por IA, pero
   conviene revisar el solapamiento.
2. **Colisión con competencia** — "growth engine" está en el titular de Verilang y también en
   `/native-reach/`. Evitado en las cinco piezas.
3. **El ángulo asume un segundo mercado identificable.** Para clientes monomercado multilingües
   el marco pierde fuerza.
4. **Las cifras van sin atribución completa** porque la fuente no la da.
5. **Dependencia de un solo ángulo.** Si se cae en revisión, se cae la semana entera.
6. **El calendario vive fuera del JSON** y puede derivar respecto de él.

### Checklist de firma

- [ ] Confirmar alcance del Free Global Visibility Audit antes de publicar los CTA
- [ ] Verificar que 63% y 147% se puedan publicar sin atribución completa
- [ ] Revisar solapamiento con los dos posts de SEO ya publicados
- [ ] Confirmar que no hay contenido ya comprometido para la semana 37
- [ ] Leer el post de Searchline completo y decidir si se enlaza
- [ ] Aprobar las firmas propuestas con cada autor

**`apto_para_firma`: false.** Los puntos 1 y 2 del checklist son bloqueantes.

---

**Firma humana:** pendiente · `firmante: null` · `fecha_firma: null`
El sistema no publica. La publicación es L0.
