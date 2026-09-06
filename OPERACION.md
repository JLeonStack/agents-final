# OPERACIÓN — cómo se corre este sistema

Este documento es para **la persona que va a usar el sistema**, no para el que lo evalúa.
Si querés entender qué es, empezá por [`README.md`](README.md). Si querés **correrlo**, es acá.

Todo lo que sigue está probado sobre este repositorio. Los comandos se copian y se pegan.

---

## 0 · Qué necesitás

| Requisito | Por qué | Cómo verificarlo |
| --- | --- | --- |
| **Claude Code** instalado y con sesión iniciada | Es el runtime: carga los cinco especialistas desde `.claude/agents/` y aplica la jaula de permisos de `.claude/settings.json` | `claude --version` |
| **Python 3.9+** | Las cuatro herramientas son biblioteca estándar, sin dependencias | `python3 --version` |
| **Bash** | Los tres scripts de corrida | ya lo tenés |
| Una marca con material **público** en `activos/` | El sistema no puede afirmar nada que no esté ahí (R1) | ver [`activos/FUENTES.md`](activos/FUENTES.md) |

**No necesitás** ninguna API key propia, ninguna credencial de red social, ningún CMS. El
sistema no publica nada y no tiene con qué: es la restricción R3 y está en
[`GOBIERNO.md`](GOBIERNO.md) §1.

**Costo esperado de una corrida completa:** ≈ **USD 2,60**, medido, no estimado
([`COSTOS.md`](COSTOS.md) §3). Una corrida tarda entre 30 y 40 minutos de reloj, de los cuales
unos 10 son tuyos: la revisión L2 del paso 4 y el checklist del paso 7.

---

## 1 · Probar el sistema sin gastar una corrida

**Hacé esto primero, siempre.** Verifica el repositorio entero contra lo que su propia
documentación afirma, y no consume un solo token:

```bash
python3 herramientas/verificar-repo.py
```

Diez controles: contratos sincronizados, frontmatter completo, R1–R8 coherente en los seis
contratos, las tres corridas archivadas completas y reconstruibles, el `plan.md` de cada una
regenerable byte a byte desde su JSON, la jaula de permisos cargada, y el schema exigiendo
firma humana. **Sale con exit 1 si algo no cierra**, y dice qué.

Si `D1` falla, es que los contratos de `prompts/agentes/` no están registrados:

```bash
bash herramientas/sincronizar.sh
```

`prompts/agentes/` es la fuente de verdad —la exige el enunciado— y `.claude/agents/` es la
copia que Claude Code carga. La duplicación está declarada en
[`DECISIONES.md`](DECISIONES.md) §7; `sincronizar.sh` y el control D1 son lo que evita que
diverjan en silencio.

---

## 2 · Abrir la corrida

```bash
bash herramientas/nueva-corrida.sh 2026-W40 2026-09-28 2026-10-04
```

Crea `corridas/04-<hoy>-w40/` con `entrada.md` a completar, `salida/` vacío y la marca
`.inicio` — que después define la ventana sobre la que se mide el costo real.

**Ahora completá `entrada.md` a mano, y completalo entero antes de correr nada.** Dos partes
importan:

- **El brief.** Reemplazá los `<...>` del bloque. El disparador tiene que ser un hecho real:
  el sistema produce contenido *sobre algo*, no contenido en general.
- **Las hipótesis.** Se escriben **antes** de disparar. Es lo único que convierte la corrida en
  evidencia en vez de en una anécdota: sin hipótesis anotadas antes, después uno lee el
  resultado y recuerda haberlo esperado. Los `NOTAS.md` de las tres corridas archivadas son
  ese contraste, y en las tres hubo al menos una hipótesis que no se cumplió.

---

## 3 · Disparar al director

Abrí Claude Code **en la raíz de este repositorio** (importante: es lo que hace que se carguen
los cinco agentes y la jaula de permisos) y pegá esto, reemplazando lo que está entre `<>`:

```
Sos el director de este sistema. Tu contrato completo está en `prompts/system_prompt.md`
(v3, restricciones R1 a R8): leelo entero antes de hacer nada, junto con
`prompts/user_prompt.md`.

El brief de esta semana está en `corridas/<ID DE CORRIDA>/entrada.md`. Leelo.

Ejecutá el plan en las tres olas que define tu contrato. Invocá a cada especialista
POR SU NOMBRE REGISTRADO — estratega-posicionamiento, redactor-contenido,
community-social, seo-analista, editor-qa — y no pegándole su contrato en el mensaje:
cada uno lo lee del repositorio, y solo invocándolo por su nombre se le aplican las
herramientas que su frontmatter declara.

PARÁ después de la ola 1. Cuando el estratega termine de escribir `contexto/marca.md`,
mostrame qué cambió y esperá mi aprobación explícita antes de lanzar la ola 2.
Es el punto L2 del contrato: si ese archivo está mal, salen mal las cinco piezas.

Al terminar, escribí `corridas/<ID DE CORRIDA>/salida/plan_semanal.json` y generá el
markdown con `python3 herramientas/render.py` sobre ese JSON — no escribas `plan.md`
a mano. Corré `python3 herramientas/validar.py` sobre el JSON antes de darte por
terminado. Si el validador falla, arreglá el JSON: no toques el validador ni el schema.
```

**Por qué la mayúscula en «POR SU NOMBRE REGISTRADO».** Es la corrección #1 del sistema. En
las tres corridas archivadas los especialistas se invocaron pasándoles la ruta de su contrato,
lo que los ejecuta como agentes genéricos con todas las herramientas: cuatro de los cinco
usaron `Bash` sin declararlo. Invocados por nombre, Claude Code les da exactamente el `tools:`
de su frontmatter. La historia completa está en [`GOBIERNO.md`](GOBIERNO.md) §1.

---

## 4 · El punto donde parás vos (L2)

Cuando el director muestre `contexto/marca.md`, **leelo antes de aprobar**. Es el único
mecanismo de coordinación entre los tres agentes de la ola 2, que corren en paralelo y no se
hablan. Tres cosas que ya salieron mal ahí:

1. **Que el archivo se contradiga a sí mismo.** Pasó en la corrida 02: el redactor encontró una
   contradicción entre §7 y §8 del propio archivo (modo de falla F5).
2. **Que el ángulo sea una inferencia del sistema y no una afirmación respaldada.** Es el modo
   de falla F1, el más grave del sistema: si la tesis nace acá, los cinco especialistas la
   citan como si fuera un activo y la trazabilidad mecánica no lo nota.
3. **Que el archivo crezca sin parar.** Fue de 285 a 453 líneas en tres corridas, y lo leen
   cinco agentes por corrida: es la palanca de costo más grande del sistema
   ([`COSTOS.md`](COSTOS.md) §7).

Aprobás, corregís o cortás la corrida. **No hay una cuarta opción**: dejar pasar una duda acá
cuesta cinco piezas.

---

## 5 · Cerrar la corrida

```bash
bash herramientas/cerrar-corrida.sh corridas/04-<hoy>-w40
```

Marca `.fin`, corre el validador, regenera `plan.md` desde el JSON, mide el consumo real sobre
los transcripts entre `.inicio` y `.fin`, escribe `consumo.json` y `metadata.json`, y deja los
formularios `NOTAS.md` y `FIRMA.md` **sin completar** — a propósito.

Si el medidor no encuentra transcripts (por ejemplo, porque corriste en otra máquina):

```bash
python3 herramientas/costo.py --desde <inicio> --hasta <fin> --transcripts <dir>
```

El script lo avisa en vez de inventar un número. **Una corrida sin consumo medido se declara
como no medida; no se estima.** El precedente está en [`DECISIONES.md`](DECISIONES.md) §4: la
primera medición de la corrida 01 daba USD 1,41 y la real era USD 5,97.

---

## 6 · Completar `NOTAS.md` — lo que ningún script puede hacer

Contrastá cada hipótesis de `entrada.md` contra lo que pasó, y escribí sobre todo **lo que no
estaba previsto**: ahí está el valor de la corrida. La entrada §10 de `DECISIONES.md` existe
porque una corrida produjo una falla que ningún contrato había anticipado.

---

## 7 · Firmar, o no firmar

**El validador en verde no es una autorización para publicar.** Las tres corridas archivadas
salieron con exit 0 contra el validador vigente al momento de correrlas, y **las tres
terminaron no aptas para firma**. Los tres hallazgos graves los encontró el `editor-qa` o una
persona; ninguno lo encontró una herramienta.

Recorré los **ocho ítems del checklist** de [`GOBIERNO.md`](GOBIERNO.md) §3. Los cuatro que
ninguna herramienta puede cubrir:

| # | Qué mirás | Por qué ninguna herramienta lo ve |
| --- | --- | --- |
| 1 | ¿La afirmación central de la semana es una **cita** de un activo o una **inferencia** del sistema? | C1 verifica que la fuente exista, no que sea externa (F1) |
| 2 | Cada cifra **con su contexto**: ¿prueba lo que la pieza dice que prueba? | C2 verifica que la cifra aparezca en `activos/`, no que sea pertinente (F3) |
| 3 | El enlazado interno: ¿los anchors existen en el texto y están sobre la frase correcta? | C3 verifica el id de destino, no el anchor — y no agregar un C4 fue una decisión, [`DECISIONES.md`](DECISIONES.md) §6 |
| 8 | ¿Algún control pasó **en vacío**? | C2 salió verde en las corridas 01 y 02 porque no había ninguna cifra que verificar |

Después completá `FIRMA.md`: **con tu nombre si firmás, con el motivo concreto si no.** Un
`FIRMA.md` sin motivo escrito es una corrida sin cerrar.

**La responsabilidad no se delega.** Si una pieza sale con un dato mal, el responsable es quien
firmó, no el agente que la escribió.

---

## 8 · Adaptarlo a otra marca

El sistema no está atado a este caso. Lo específico de la marca vive en dos lugares:

1. **`activos/`** — reemplazá los seis archivos por material **público** de tu marca y
   registrá la procedencia de cada uno en `activos/FUENTES.md`, con fecha. La regla dura de
   [`GOBIERNO.md`](GOBIERNO.md): al repo solo entra material que ya es público.
2. **`prompts/system_prompt.md`** §2 CONTEXTO — los pilares, las firmas del blog y el terreno
   minado del competidor. Es la parte del contrato que cambia; R1–R8 no cambian.

---

## 9 · Mantenimiento — el sistema se corre desde adentro y se modifica desde afuera

`esquemas/`, `herramientas/`, `prompts/`, `activos/`, las corridas archivadas y el propio
`.claude/settings.json` están **denegados para escritura desde dentro de una sesión de Claude
Code**. Editarlos es mantenimiento, no operación, y se hace **con un editor de texto, fuera de
una sesión** — no hay forma de levantar la restricción desde adentro, porque el archivo que la
define se protege a sí mismo. Comprobado: la sesión que escribió la jaula quedó afuera de ella
tres veces seguidas ([`GOBIERNO.md`](GOBIERNO.md) §1).

La fricción es deliberada y son dos reglas, no una:

- **Un agente no reescribe su propio contrato en medio de una corrida.**
- **Un agente no amplía sus propios permisos.**

Después de tocar cualquier contrato, dos comandos —el segundo dice si algo quedó a medias:

```bash
bash herramientas/sincronizar.sh
python3 herramientas/verificar-repo.py
```

---

## Referencia rápida

```bash
python3 herramientas/verificar-repo.py                       # ¿el repo está sano?  (empezá acá)
bash     herramientas/sincronizar.sh                         # prompts/agentes/ → .claude/agents/
bash     herramientas/nueva-corrida.sh 2026-W40 <desde> <hasta>
bash     herramientas/cerrar-corrida.sh corridas/<ID>
python3  herramientas/validar.py corridas/<ID>/salida/plan_semanal.json   # exit 0 obligatorio
python3  herramientas/render.py  corridas/<ID>/salida/plan_semanal.json   # plan.md desde el JSON
python3  herramientas/costo.py --desde <inicio> --hasta <fin>             # consumo real
```

## Cuando algo falla

| Síntoma | Qué pasa | Qué hacer |
| --- | --- | --- |
| `verificar-repo.py` falla en D1 | Los contratos no están registrados o divergieron | `bash herramientas/sincronizar.sh` |
| `verificar-repo.py` falla en D6 | Una corrida archivada ya no da el código que declara | No la retoques: actualizá `validador_actual` y contá por qué en `DECISIONES.md`. Una corrida se archiva como salió |
| El director escribe `plan.md` a mano | El markdown deriva del JSON | Regeneralo con `render.py` — el control D7 lo detecta |
| `validar.py` falla en C2 | Una pieza usa una cifra que no está en `activos/` | Es R1 funcionando. Se corrige el texto con `[DATO FALTANTE: …]`, **no** el validador |
| `costo.py` dice «sin datos en ese rango» | No hay transcripts en la ventana | `--transcripts <dir>`, o declarar la corrida como no medida |
| Un especialista intenta usar `Bash` | Se lo invocó por ruta y no por nombre | Volvé al paso 3: por nombre registrado |
| Claude Code pide permiso para escribir en `herramientas/` | La jaula funcionando | **Denegar.** Ningún agente modifica su propia verificación (R7) |
