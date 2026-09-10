# Plan inicial — escrito el 5/9 antes de empezar

> Este archivo es evidencia de proceso, no el estado del proyecto. **Se le agregó este
> encabezado al cierre**; el resto es el texto original, sin retocar. El cronograma de ocho días
> no se cumplió: el trabajo se hizo en una sesión concentrada. El desvío está explicado en
> [`DECISIONES.md`](DECISIONES.md) §0.

> **Sistema:** un equipo de agentes de marketing que produce el plan de contenidos semanal
> de [EMPRESA], leyendo material real de la marca y entregando salida estructurada.
> **Cierre:** domingo 13/9, 23:59. **Hoy:** sábado 5/9 → **quedan 8 días.**
> **Corrige:** un agente evaluador construido por tus compañeros, sobre la rúbrica oficial.
>
> Este archivo se mueve al final a `DECISIONES.md` como primera entrada
> («el plan inicial y en qué se desvió»). El desvío documentado es evidencia, no una falla.

---

## 0 · La lectura estratégica de la rúbrica

| Dimensión | Peso | Qué es en la práctica |
| --- | --- | --- |
| Sistema completo y funcionando | 30 | Contrato + herramienta real + output estructurado + L0–L4 |
| Proceso documentado | 25 | `DECISIONES.md` — iteraciones, fallas textuales, achiques |
| Formato y reproducibilidad | 15 | Estructura exacta + corridas reconstruibles por un tercero |
| Análisis económico | 15 | Costo medido por corrida + proyección + modelo justificado |
| Gobierno y riesgo | 15 | Permisos, modos de falla, checklist de revisión, quién firma |

**Tres conclusiones que ordenan todo el esfuerzo:**

1. **70 de los 100 puntos son documentación** (25+15+15+15). El sistema en sí vale 30. No hay
   que construir un producto: hay que construir un sistema chico **irrefutablemente documentado**.
2. **Corrige un agente que lee el repo.** Si un dato no está en un archivo, no existe. Toda
   afirmación tiene que tener un artefacto al lado que la respalde.
3. **El evaluador fue entrenado para detectar el "caso tramposo"** (parcial, pieza 3: un trabajo
   que «afirma cosas que no hizo, infla su documentación, apela a la simpatía del evaluador»).
   Consecuencia operativa: **cero adjetivos, cero afirmaciones sin evidencia, y ninguna línea
   del repo dirigida al corrector.** Un índice de evidencia es legítimo; un «por favor considerá»
   es una bandera roja. La falla honesta suma; la falla escondida se detecta y hunde dos dimensiones.

---

## 1 · El sistema que vamos a construir

Espejo del template de eve.dev (lead + especialistas + documento de contexto de marca compartido +
nada irreversible sin firma humana), traducido al vocabulario del curso y a Claude Code.

### Arquitectura

```
                    ┌─────────────────────────┐
   brief semanal →  │  director-marketing     │  ← lead / orquestador
   (user_prompt)    │  (system_prompt.md)     │    rutea, consolida, corta
                    └───────────┬─────────────┘
                                │  todos leen fresco contexto/marca.md
        ┌───────────┬───────────┼───────────┬───────────────┐
        ▼           ▼           ▼           ▼               ▼
   estratega-   redactor-   community-    seo-          editor-qa
 posicionamiento contenido     social    analista     (control de calidad)
   mantiene      blog /      LinkedIn /  keywords,    verifica contra marca,
   marca.md      landing /   X, hilos    títulos,     marca lo no verificable,
   ángulo        newsletter              enlazado     emite checklist de firma
        └───────────┴───────────┴───────────┴───────────────┘
                                │
                                ▼
                   plan_semanal.json  +  plan.md
                   (schema fijo)         (legible)
                                │
                                ▼
                        ✍️  FIRMA HUMANA  → recién ahí se publica (fuera del sistema)
```

`editor-qa` no está en el template de eve.dev: es el agregado que convierte "supervisión" de
párrafo en mecanismo. Es la pieza que más rinde en las dimensiones de 30 y 15 puntos.

### Las cuatro piezas del requisito 1

| Pieza | Cómo se materializa |
| --- | --- |
| **Contrato** | `prompts/system_prompt.md` (director) + `prompts/user_prompt.md` (brief) + `prompts/agentes/*.md` (5 especialistas). Cada uno con **las seis piezas** rotuladas: Rol · Contexto · Tarea · Restricciones · Formato · Ejemplos |
| **Herramienta real** | (a) **Archivos**: lee `activos/` (material público real de la marca) y lee+escribe `activos/calendario.csv`. (b) **WebFetch**: GET real al sitio público de la empresa y de 2 competidores. Dos herramientas, cero fricción de auth |
| **Output estructurado** | `esquemas/plan_semanal.schema.json` + `herramientas/validar.py`. **La salida no es "estructurada" porque lo digo: es estructurada porque hay un validador que corre y falla si no lo es** |
| **Supervisión L0–L4** | Tabla por paso del pipeline (abajo), con quién firma |

### Mapa de supervisión (va al README y a `GOBIERNO.md`)

| Paso del pipeline | Nivel | Qué hace solo | Quién revisa / firma |
| --- | --- | --- | --- |
| Leer `activos/`, fetch sitio y competidores | **L3** — ejecutar y avisar | Todo | Auditoría por muestreo (yo, 1 de cada 3 corridas) |
| Actualizar `contexto/marca.md` | **L2** — ejecutar con revisión | Propone el diff | Yo apruebo antes de que otro agente lo use |
| Redactar piezas (blog, posts, newsletter) | **L2** — ejecutar con revisión | Escribe completo | Yo reviso pieza por pieza |
| `editor-qa` verifica y marca `[DATO FALTANTE]` | **L3** — ejecutar y avisar | Todo | Su salida es justamente el insumo de mi revisión |
| Escribir `activos/calendario.csv` | **L2** | Propone las filas | Yo confirmo antes del commit |
| **Publicar en cualquier canal** | **L0 — el agente no publica. Nunca.** | Nada | Yo, con firma registrada en `corridas/NN/FIRMA.md` |

La materia opera en **L2**. Ese es el nivel declarado del sistema, y la única excepción hacia
arriba (L3) es investigación de solo-lectura, que es barata y reversible.

---

## 2 · Estructura del repositorio

Lo **obligatorio** es innegociable y va exactamente así. Lo demás es aditivo.

```
README.md                    ← OBLIGATORIO · README estándar + mapa de evidencia
DECISIONES.md                ← OBLIGATORIO · la historia real de la construcción
prompts/                     ← OBLIGATORIO
  system_prompt.md              el contrato del director (las seis piezas)
  user_prompt.md                la plantilla de brief semanal
  agentes/                      los 5 especialistas — FUENTE DE VERDAD
    estratega-posicionamiento.md
    redactor-contenido.md
    community-social.md
    seo-analista.md
    editor-qa.md
corridas/                    ← OBLIGATORIO
  01-2026-09-07-semana-37/
    entrada.md                  el user prompt exacto + qué activos había
    salida/plan_semanal.json    tal como salió · sin retocar
    salida/plan.md              tal como salió · sin retocar
    transcript.jsonl            la traza completa de la corrida
    metadata.json               fecha, modelo, tokens in/out/cache, duración, costo
    NOTAS.md                    qué salió mal, qué revisé, qué firmé
    FIRMA.md                    quién firma, qué firmó, con qué fecha
  02-2026-09-08-.../
  03-2026-09-09-.../
COSTOS.md                       análisis económico
GOBIERNO.md                     permisos, modos de falla, checklist, firma
contexto/marca.md               el brand context compartido (lo mantiene el estratega)
activos/                        material público real de la marca + calendario.csv
esquemas/plan_semanal.schema.json
herramientas/
  validar.py                    valida la salida contra el schema
  costo.py                      extrae usage del transcript y calcula el costo
  sincronizar.sh                copia prompts/agentes/ → .claude/agents/
.claude/agents/                 copia operativa (la que carga Claude Code)
```

**Nota de diseño sobre `prompts/` vs `.claude/agents/`:** el enunciado exige que los contratos
vivan en `prompts/`. Claude Code los carga desde `.claude/agents/`. Resolución: **`prompts/agentes/`
es la fuente de verdad** y `herramientas/sincronizar.sh` copia hacia `.claude/agents/`. La
duplicación es deliberada, tiene riesgo de deriva, y ese riesgo se declara en `DECISIONES.md`
con su mitigación (correr el script antes de cada corrida). Declarar la costura vale más que
esconderla.

---

## 3 · Las tres corridas

**Regla dura: la salida se guarda tal como salió.** Si es fea, queda fea y se explica en `NOTAS.md`.
Editar una salida para que se vea mejor es exactamente lo que el evaluador busca detectar.

| # | Cuándo | Entrada real | Qué demuestra |
| --- | --- | --- | --- |
| **00 — piloto** | Dom 6/9 | Brief de la semana en curso | **No cuenta como corrida.** Existe para que las cosas se rompan temprano. Alimenta la entrada 1 de `DECISIONES.md` |
| **01** | Lun 7/9 | Semana real + activos v1 | El sistema corre punta a punta con contrato v1 |
| **02** | Mar 8/9 | Otra semana / otro ángulo | El sistema mejorado por la iteración 1 y 2 |
| **03** | Mié 9/9 | Tercera semana real | Corrida final con el modelo elegido en el banco de pruebas |

**Prueba del tercero (requisito 2):** al final, clonar el repo en una carpeta limpia y seguir el
README al pie de la letra sin usar nada de lo que tengo en la cabeza. Si no se reconstruye,
el README está mal — no el lector.

---

## 4 · `DECISIONES.md` — el formato que el curso enseña

Vale 25 puntos: la segunda dimensión más pesada. La materia enseñó un loop explícito
(*probar → observar textual → ajustar UNA pieza → volver a correr el mismo caso*). Cada entrada
lo replica:

```markdown
## 2026-09-06 · El director inventaba métricas

**Síntoma (textual, copiado de la salida):**
> "...logrando un engagement promedio del 4,2% en LinkedIn..."
Ese número no está en ningún archivo de `activos/`. El agente lo inventó.

**Diagnóstico (¿cuál de las seis piezas falló?):** RESTRICCIONES. El contrato decía qué producir,
no qué estaba prohibido afirmar.

**Cambio (una sola pieza):** agregué a `system_prompt.md`:
> "Prohibido afirmar cifras, fechas o resultados que no estén literalmente en `activos/`.
>  Si falta un dato necesario, escribí `[DATO FALTANTE: qué necesitás]` y seguí."

**Después (mismo caso, vuelto a correr):** corrida 01 — 0 cifras inventadas, 3 marcas de
`[DATO FALTANTE]`. Evidencia: `corridas/01-.../salida/plan.md` líneas 22, 41, 58.
```

**Objetivo: 5–6 entradas**, de las cuales al menos:
- **2 fallas serias** de verdad (no cosméticas), con el texto del error copiado tal cual.
- **1 achique de alcance** — el enunciado lo pide literal: «qué se achicó y por qué».
  El candidato natural: arrancar con 5 especialistas y bajar a 4 si el martes voy atrasado,
  o resignar la escritura automática del calendario y dejarlo en propuesta.
- **1 costura declarada** — la duplicación `prompts/` ↔ `.claude/agents/`.

---

## 5 · Análisis económico — medido, no estimado

**Método real (ya verificado que funciona):** los transcripts de Claude Code guardan `usage` por
mensaje en `~/.claude/projects/<slug>/*.jsonl`, con los cuatro campos que importan:

```
"usage":{"input_tokens":…,"cache_creation_input_tokens":…,"cache_read_input_tokens":…,"output_tokens":…}
```

`herramientas/costo.py` los suma por corrida. **Nada de "aproximadamente X tokens".**

**Precios vigentes (API Anthropic, USD por millón de tokens):**

| Modelo | ID | Entrada | Salida |
| --- | --- | --- | --- |
| Claude Opus 5 | `claude-opus-5` | 5,00 | 25,00 |
| Claude Sonnet 5 | `claude-sonnet-5` | 2,00 | 10,00 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 1,00 | 5,00 |

Las lecturas y escrituras de caché tienen tarifa propia y se contabilizan aparte — el script las
separa en vez de mezclarlas con la entrada.

**Banco de pruebas de modelo (miércoles 9/9).** Misma entrada, tres modelos, criterio de aprobación
declarado *antes* de correr:

| Criterio de aprobación | Cómo se verifica |
| --- | --- |
| El JSON valida contra el schema | `herramientas/validar.py` — pasa / no pasa |
| Cero cifras no presentes en `activos/` | Chequeo manual sobre la salida |
| Respeta tono y ángulo de `contexto/marca.md` | Juicio propio, registrado |
| Las 5 piezas del plan existen y son distintas entre sí | Conteo |

Se elige **el más chico que pasa los cuatro**. Si Haiku falla, se documenta *en qué* falló — eso
es información, no una derrota. Si Haiku pasa, se documenta el ahorro.

**Las dos cuentas que hay que separar (y casi nadie separa):**

| | Costo de **construir** | Costo de **operar** |
| --- | --- | --- |
| Modelo | El grande (diseño, iteraciones, depuración) | El más chico que pasa |
| Volumen | ~15–25 corridas de desarrollo, una sola vez | 1 corrida/semana |
| Es | Inversión hundida | La cuenta que importa para la decisión |

**Proyección:** costo/corrida × 52 semanas (una marca) y × 4 marcas × 52 (el sistema "en serio").
Y el contrapunto que corresponde a un MBA: **cuántas horas de trabajo humano reemplaza y cuánto
valen esas horas.** Si el sistema cuesta USD 40/año y sustituye 3 h/semana, la conclusión se
escribe sola — y si no las sustituye, eso también se dice.

---

## 6 · Gobierno y riesgo

**El problema propio del caso elegido:** el material es de tu empresa actual y el repo es público.

> **Regla dura: solo entra al repo material que ya es público** — sitio web, posts publicados,
> notas de prensa. Nada de datos internos, clientes, precios no publicados o métricas internas.
> Si algo interno resulta imprescindible, se anonimiza **y se dice que se anonimizó.**
> Pasada de sanitización obligatoria antes de cada commit (sábado 12/9, revisión completa).

Esta restricción no es un obstáculo: es la mitad del contenido de la dimensión de gobierno,
y es un riesgo real bien gestionado en vez de uno hipotético bien redactado.

**Contenido de `GOBIERNO.md`:**

1. **Inventario de permisos** — tabla de qué toca y con qué alcance:
   filesystem (lectura de `activos/`, escritura **solo** en `corridas/` y `contexto/`),
   red (WebFetch, GET, lista blanca de 3 dominios).
   Y explícitamente **lo que NO toca**: no publica, no manda mails, no toca el CMS, no toca
   redes, no accede a sistemas internos.
2. **Modos de falla** — 6 concretos, con impacto / detección / mitigación:
   alucinación de cifras · filtración de material interno al repo público · tono fuera de marca ·
   parecido excesivo a un competidor (el agente leyó su sitio) · deriva de `contexto/marca.md`
   entre corridas · dependencia operativa si el sistema deja de estar disponible.
3. **Checklist de firma** — 6–8 ítems verificables que reviso antes de confiar en una salida.
4. **Quién firma** — nombre, rol, y el registro en `corridas/NN/FIRMA.md`.

---

## 7 · Cronograma — 8 días

| Día | Foco | Entregable del día | Commit |
| --- | --- | --- | --- |
| **Sáb 5/9** (hoy) | **Fundar** | Repo público creado · estructura completa con placeholders · empresa y brief semanal reales elegidos · `activos/` con 10–20 archivos públicos reales · contrato v0 (seis piezas) | «estructura + contrato v0» |
| **Dom 6/9** | **Romper temprano** | Los 5 especialistas en `prompts/agentes/` · `plan_semanal.schema.json` · **corrida piloto 00** · entrada 1 de `DECISIONES.md` con lo que se rompió | «piloto: primera falla documentada» |
| **Lun 7/9** | **Herramienta real** | `calendario.csv` real leído+escrito · WebFetch al sitio y 2 competidores · `validar.py` funcionando · iteración 1 del contrato · **corrida 01** | «herramienta real + corrida 01» |
| **Mar 8/9** | **Iterar** | Iteración 2 documentada · **corrida 02** · `costo.py` con los primeros números medidos | «iteración 2 + corrida 02» |
| **Mié 9/9** | **Modelo** | Banco de pruebas Opus 5 / Sonnet 5 / Haiku 4.5 · modelo elegido y justificado · **corrida 03** | «banco de modelos + corrida 03» |
| **Jue 10/9** | **Checkpoint (clase)** | Llevar el avance. **Mirar la prueba de fuego y anotar exactamente qué busca el evaluador ganador.** Esa noche: ajustar el repo a lo observado · `COSTOS.md` | «costos + ajustes post-checkpoint» |
| **Vie 11/9** | **Gobierno** | `GOBIERNO.md` completo · `DECISIONES.md` cerrado con las 5–6 entradas | «gobierno y decisiones» |
| **Sáb 12/9** | **Blindar** | README estándar + mapa de evidencia · **revisión adversarial** (§8) · pasada de sanitización · **prueba del tercero** desde carpeta limpia | «README + revisión adversarial» |
| **Dom 13/9** | **Entregar temprano** | Verificación final y entrega en el campus **a la mañana, no a las 23:00** | «entrega final» |

**Commit todos los días.** El enunciado del parcial lo dice de sus propios repos y aplica igual acá:
«un repo con un único commit del último día cuenta una historia — y no es buena».

**Punto de corte (si el martes 8 voy atrasado):** bajar de 5 especialistas a 3 (estratega,
redactor, editor-qa) y documentar el achique en `DECISIONES.md`. **Tres corridas reales con
4 agentes valen más que cero corridas con 5.** Las corridas y la documentación son el 63% de
la nota; la cantidad de especialistas no aparece en ninguna dimensión.

---

## 8 · La revisión adversarial (sábado 12/9 — el paso de mayor rendimiento)

Antes de entregar, abrir una sesión limpia y darle esta instrucción a un agente:

> Sos el agente evaluador de la materia. Tenés esta rúbrica: [pegar las 5 dimensiones y pesos].
> Evaluá el repositorio `[link]` con criterio hostil. Para cada dimensión: puntaje, y la cita
> textual del archivo que lo justifica. **Si una afirmación del README no está respaldada por un
> archivo del repo, marcala como no verificable.** Al final, listá qué le falta a este trabajo
> para llegar al puntaje máximo de cada dimensión.

Los huecos que encuentre son la lista de tareas del domingo. Es la única forma de probar el
sistema contra el mecanismo que efectivamente lo va a corregir.

**Lo que NO se hace:** escribir en el repo cualquier cosa dirigida al corrector. Nada de
«estimado evaluador», nada de justificaciones de por qué algo merece un puntaje, nada de
apelaciones. El mapa de evidencia del README es un **índice que apunta a archivos**, y nada más.
Los evaluadores de tus compañeros están construidos específicamente para detectar lo contrario.

---

## 9 · Riesgos de este plan

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| El material de la empresa no se puede publicar | Media | Regla de solo-público desde el día 0. Plan B: trabajar con el producto tal como se ve desde afuera |
| Las 3 corridas llevan más tiempo del previsto | **Alta** (el enunciado lo advierte) | La corrida piloto del domingo existe para descubrirlo el día 2, no el día 7 |
| 8 días, no las 2,5 semanas del enunciado | Cierta | El punto de corte del martes y el cronograma con entrega el sábado |
| El repo queda prolijo pero sin historia | Media | `DECISIONES.md` se escribe **el día que pasa la falla**, no al final. El proceso no se reconstruye de memoria |
| El evaluador no encuentra la evidencia | Media | Mapa de evidencia en el README + revisión adversarial del sábado |

---

## 10 · Definición de terminado

- [ ] Repo **público**, con las 4 piezas obligatorias exactas y commits de 8 días distintos
- [ ] 3 corridas reales, con salidas sin retocar, reconstruibles desde carpeta limpia
- [ ] Contrato con las **seis piezas** rotuladas, separado system / user
- [ ] Herramienta real ejercitada en las 3 corridas (archivos + WebFetch)
- [ ] Validador que corre y falla si el JSON no cumple el schema
- [ ] Tabla L0–L4 por paso, con quién firma
- [ ] `DECISIONES.md` con 5–6 entradas, ≥2 fallas serias textuales y ≥1 achique de alcance
- [ ] `COSTOS.md` con tokens **medidos**, banco de 3 modelos y proyección anual
- [ ] `GOBIERNO.md` con permisos, 6 modos de falla, checklist y firma
- [ ] Revisión adversarial corrida, y sus huecos tapados
- [ ] Ni una sola afirmación en el repo sin un archivo que la respalde
