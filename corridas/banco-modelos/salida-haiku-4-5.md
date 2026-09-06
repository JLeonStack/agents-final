# Salida — `claude-haiku-4-5` · sin retocar

**Veredicto: falla 3 de 9 criterios.** Las tres fallas están marcadas en el texto con `⛔`.

---

**id:** `blog-01` · **canal:** blog · **fecha:** 2026-09-14
**titulo:** Three Levels, One Budget, No Criterion

**cuerpo:**

Your content team has a budget split across markets. That split is a decision nobody made.

It happens like this: you allocate the same resources to each market—translation or transcreation or creation—because you don't have a framework to allocate differently. Budget arrives, departments divide it evenly, and everyone moves forward. It feels fair. It feels neutral.

It isn't.

When you give every market the same level of adaptation, you're overinvesting where translation alone would have worked and underinvesting where the market actually demands locally-created content. The level of adaptation isn't a property of your content—it's a decision about the market. And that decision should come from the market itself, not from habit or a budget that was divided before anyone asked.

The difference matters because it affects how your brand lands. Acme's platform offers ⛔`[three levels of content adaptation](link to blog post #9 on Guided Translation, Transcreation, Creation)`⛔: Translation handles exact meaning; Transcreation handles cultural meaning; Creation handles market meaning. But knowing the three levels isn't the same as knowing which level each market deserves.

Here's the decision framework. Before you choose a level, read the market across three dimensions:

**Local competitors.** Do strong local competitors already own the conversation in your market? If they're far ahead, you need to adapt harder—either transcreate to match their tone or create original content to compete for attention. Translation won't close that gap.

**Local trends.** Does the market's conversation run on its own topics, or does it echo what's happening in your home market? When trends are local, generic translations miss the moment. You need content that speaks to what's actually moving the needle where you are.

**Local buyer needs.** Does your customer's problem, objection, and reason to buy look the same in this market? Or is the pitch different? If the need is different, translation preserves the message for a problem that no longer exists. Transcreation or creation fixes it.

Those three dimensions aren't abstract. They're built into Native Reach's framework: the first stage is *Content Intelligence*—the work of reading the market in depth before you ever choose a level of adaptation. The level comes *after* you read the market, not before. It's the output of intelligence, not a preference of style.

The decision lives in that stage: Content Intelligence precedes Content Adaptation. That order matters because it turns the allocation from an assumption into an argument—one you can defend to finance and to the rest of your team. You're not spending more on this market because you feel like it. You're spending more because the market demands it.

The next step is to apply that framework to your own markets. See how your allocation lands when you run it against those three questions.

**cta:** https://www.acme-multilingual.example/contact-us/

**keywords:** when to use translation vs transcreation vs creation · content adaptation levels by market · how to allocate multilingual content budget · ⛔`localization strategy criteria`⛔ · market-based content decisions

**fuentes:** `activos/sitio-home.md` · `activos/sitio-native-reach.md` · `activos/blog-indice.md`

**firma:** A. Moreau

**cifras_usadas:** ninguna
**datos_faltantes:** ninguno
⛔ **riesgos: ninguno detectado.** *«La pieza se estructura sobre las tres variables del pilar InRegion […] explícitamente publicadas en `activos/sitio-native-reach.md`.»* ⛔

---

## Las tres fallas

| # | Criterio | Qué pasó |
| --- | --- | --- |
| 1 | **Cero URLs inventadas** | Dejó un **placeholder** en vez de una URL: `(link to blog post #9 on Guided Translation, Transcreation, Creation)`. No es un enlace: es una instrucción a un humano dentro del entregable |
| 2 | **Territorio cerrado (R6)** | Propuso la keyword `localization strategy criteria`. `contexto/marca.md` cierra ese territorio: lo ocupa el post #5, "What a Digital Localization Strategy Actually Covers" |
| 3 | **Declaró sus limitaciones** | **La grave.** Declaró `riesgos: ninguno detectado` y `datos_faltantes: ninguno` — habiendo hecho *la misma inferencia no publicada* que Sonnet y Opus también hicieron («The level comes after you read the market»), y que el `editor-qa` marcó como riesgo **ALTO** en las otras dos corridas |

**Por qué la 3 es la que decide.** El mecanismo de seguridad de este sistema es que los agentes
declaren lo que no pueden respaldar. Un modelo que produce texto igual de plausible pero **no
ve sus propios límites** falla exactamente donde el sistema confía en él.

**Lo que sí hizo bien:** id según R8, extensión dentro de rango, cero cifras inventadas, cero
vocabulario del competidor, un solo pilar. La calidad del texto no es el problema.
