# Procedencia de las corridas

**Para qué es este archivo.** Para que alguien que nunca habló conmigo pueda reconstruir
cualquiera de las tres corridas sin preguntar nada: qué entró, qué salió, cuándo, **con qué
datos de origen** y con qué modelo. Cada ruta de esta página es un enlace relativo que
resuelve en GitHub y que verifica el control **D8** de
[`verificar-repo.py`](../herramientas/verificar-repo.py): si alguna dejara de existir, el
verificador falla.

Lo que `activos/FUENTES.md` hace por el material de marca —decir de dónde salió cada archivo—
esta página lo hace por las corridas.

**Y lo que esta página no hace, lo hace [`RECALCULO.md`](RECALCULO.md):** acá está de dónde
salió cada corrida; ahí están las **cuentas hechas**, corrida por corrida, con números de la
salida rehechos desde la entrada, la operación escrita y el desvío. Poder repetir una corrida
y que sus números cierren son dos cosas distintas, y las dos hacen falta.

---

## Las tres corridas reales

| | **01** | **02** | **03** |
| --- | --- | --- | --- |
| Semana ISO | 2026-W37 | 2026-W38 | 2026-W39 |
| **Entrada** | [`entrada.md`](01-2026-09-05-w37/entrada.md) | [`entrada.md`](02-2026-09-05-w38/entrada.md) | [`entrada.md`](03-2026-09-05-w39/entrada.md) |
| **Salida (dato)** | [`plan_semanal.json`](01-2026-09-05-w37/salida/plan_semanal.json) | [`plan_semanal.json`](02-2026-09-05-w38/salida/plan_semanal.json) | [`plan_semanal.json`](03-2026-09-05-w39/salida/plan_semanal.json) |
| **Salida (legible)** | [`plan.md`](01-2026-09-05-w37/salida/plan.md) | [`plan.md`](02-2026-09-05-w38/salida/plan.md) | [`plan.md`](03-2026-09-05-w39/salida/plan.md) |
| **Fecha — inicio UTC** | 2026-09-05T21:36:08Z | 2026-09-05T21:57:24Z | 2026-09-05T22:20:40Z |
| **Fecha — fin UTC** | 2026-09-05T21:54:26Z | 2026-09-05T22:19:25Z | 2026-09-05T22:54:42Z |
| Modelo de los 5 especialistas | `claude-opus-5` | `claude-opus-5` | `claude-sonnet-5` |
| Validador | `exit 0` | `exit 0` | `exit 0` |
| Apto para firma (editor-qa) | `false` | `false` | `false` |
| Firmada por una persona | [no](01-2026-09-05-w37/FIRMA.md) | [no](02-2026-09-05-w38/FIRMA.md) | [no](03-2026-09-05-w39/FIRMA.md) |
| Costo medido | USD 6,10 | USD 7,70 | USD 4,04 |
| Metadata completa | [`metadata.json`](01-2026-09-05-w37/metadata.json) | [`metadata.json`](02-2026-09-05-w38/metadata.json) | [`metadata.json`](03-2026-09-05-w39/metadata.json) |
| Consumo crudo | [`consumo.json`](01-2026-09-05-w37/consumo.json) | [`consumo.json`](02-2026-09-05-w38/consumo.json) | [`consumo.json`](03-2026-09-05-w39/consumo.json) |
| Contraste contra hipótesis | [`NOTAS.md`](01-2026-09-05-w37/NOTAS.md) | [`NOTAS.md`](02-2026-09-05-w38/NOTAS.md) | [`NOTAS.md`](03-2026-09-05-w39/NOTAS.md) |

Las tres cuestan más que el número operativo de `COSTOS.md` porque incluyen al director en
Opus 5 y el trabajo de construcción de esa sesión; el desglose está en
[`COSTOS.md`](../COSTOS.md) §3. **Ninguna está firmada**, y eso no es un olvido: el `editor-qa`
declaró `apto_para_firma: false` en las tres y el motivo está escrito en cada `FIRMA.md`.

---

## El dato de origen: qué leyó cada corrida

Ningún agente salió a la web durante una corrida. Los cinco especialistas leen **solo** los
archivos de [`activos/`](../activos/), que se extrajeron una vez, antes de la corrida 01, y
cuya procedencia —URL y fecha de extracción— está en
[`activos/FUENTES.md`](../activos/FUENTES.md).

| Archivo de origen | Qué es | 01 | 02 | 03 |
| --- | --- | :-: | :-: | :-: |
| [`activos/sitio-home.md`](../activos/sitio-home.md) | Home pública de la marca | ✓ | ✓ | ✓ |
| [`activos/sitio-native-reach.md`](../activos/sitio-native-reach.md) | Página del activo de autoridad | ✓ | ✓ | ✓ |
| [`activos/blog-indice.md`](../activos/blog-indice.md) | Índice del blog público | ✓ | ✓ | |
| [`activos/competencia-verilang.md`](../activos/competencia-verilang.md) | Home pública del competidor | ✓ | | ✓ |
| [`activos/calendario.csv`](../activos/calendario.csv) | Qué se publicó antes — estado del sistema | ✓ | ✓ | |

La marca ✓ es la que **la propia corrida cita**: sale de las rutas nombradas en su `entrada.md`
y en su `plan_semanal.json`, no de mi memoria. Los cinco archivos están en el repositorio; el
sistema no tiene ninguna otra fuente de datos, y R1 le prohíbe afirmar lo que no esté ahí.

Hay un sexto archivo que **no** es entrada sino salida intermedia:
[`contexto/marca.md`](../contexto/marca.md), el documento compartido que escribe el estratega
en la ola 1 y leen los otros cuatro. Está versionado en el estado en que lo dejó la última
corrida.

---

## Cómo reconstruir una corrida

Todo lo necesario está en el repositorio. Nada depende de mi máquina.

```bash
python3 herramientas/verificar-repo.py                                   # 1. el repo está sano
python3 herramientas/validar.py corridas/03-2026-09-05-w39/salida/plan_semanal.json
python3 herramientas/render.py  corridas/03-2026-09-05-w39/salida/plan_semanal.json
git diff --exit-code corridas/03-2026-09-05-w39/salida/plan.md           # 2. sin diferencias
```

El paso 2 es el que importa: **`plan.md` se regenera byte a byte desde el JSON archivado**, así
que el markdown no puede haber derivado del dato. El control **D7** corre exactamente esto
sobre las tres corridas, y **D6** confirma que el validador da hoy el mismo código que cada
`metadata.json` declara.

Para disparar una corrida nueva —lo que sí necesita un modelo y gasta dinero— el procedimiento
completo está en [`OPERACION.md`](../OPERACION.md).

---

## Lo que hay además de las tres

| Dónde | Qué es | Por qué está |
| --- | --- | --- |
| [`00-piloto/`](00-piloto/) y [`00-piloto-bis/`](00-piloto-bis/) | El prompt de una línea, corrido dos veces | La evidencia de por qué hace falta un contrato: mismo modelo, dos sistemas distintos (`DECISIONES.md` §1) |
| [`banco-modelos/`](banco-modelos/) | La misma tarea en Opus 5, Sonnet 5 y Haiku 4.5 | Cómo se eligió el modelo de producción por medición y no por precio (`COSTOS.md` §5) |

Los dos pilotos son anteriores al schema v3 y **no validan** contra él a propósito: está
explicado en `DECISIONES.md` §8. Por eso el verificador solo exige los siete archivos
obligatorios a las tres corridas reales.
