#!/usr/bin/env python3
"""
Extrae el consumo real de tokens de los transcripts de Claude Code y calcula el costo.

Los transcripts viven en ~/.claude/projects/<slug>/*.jsonl y guardan, por cada respuesta
del modelo, un bloque `message.usage` con los cuatro campos que importan:

    input_tokens · cache_creation_input_tokens · cache_read_input_tokens · output_tokens

Esto NO es una estimación: son los tokens que la API efectivamente facturó.

    python3 herramientas/costo.py --desde 2026-09-05T21:00:00Z --hasta 2026-09-05T21:40:00Z
    python3 herramientas/costo.py                       # todo lo que haya

DOS TRAMPAS RESUELTAS (ver DECISIONES.md, entrada «el medidor medía mal»):

  T1 · Cada respuesta aparece repetida una vez por `apiBlockIndex`. Sin deduplicar por
       `requestId`, el total sale multiplicado por la cantidad de bloques de streaming.
  T2 · Al deduplicar hay que quedarse con el bloque de MAYOR `output_tokens`, no con el
       primero: en streaming los bloques traen el contador de salida incompleto y el
       total real está en el último. Deduplicar mal subestima la salida ~100x — que es
       justamente el token que más caro se paga.

Los subagentes escriben en transcripts propios, bajo <sesión>/subagents/agent-*.jsonl.
Sin ellos solo se mide al director y el costo de una corrida sale ~5x más barato de lo real.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# USD por millón de tokens. Precios de lista de la API de Anthropic.
PRECIOS = {
    "claude-opus-5":   {"in": 5.00, "out": 25.00},
    "claude-sonnet-5": {"in": 2.00, "out": 10.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
}
# SUPUESTO DECLARADO (ver COSTOS.md §supuestos): multiplicadores de caché estándar
# sobre el precio de entrada. Escritura 1,25× · lectura 0,10×.
MULT_CACHE_ESCRITURA = 1.25
MULT_CACHE_LECTURA = 0.10

# Donde viven los transcripts. Claude Code guarda uno por proyecto, en un directorio cuyo
# nombre es la ruta absoluta del repo con todo lo que no es alfanumerico reemplazado por "-".
# Se deriva de la ubicacion real del repositorio, para que el script tambien mida en la maquina
# de otra persona; si ese directorio no existe se cae al slug de la maquina donde se corrio
# este trabajo, y --transcripts sobreescribe cualquiera de los dos.
SLUG_ORIGINAL = "-Users-jdeleon-Documents-personal-ucema-MBA-Segundo-a-o-Agentes-IA-agents-final"


def slug_de(ruta: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(ruta))


def dir_por_defecto() -> Path:
    proyectos = Path.home() / ".claude" / "projects"
    aqui = proyectos / slug_de(Path(__file__).resolve().parent.parent)
    return aqui if aqui.exists() else proyectos / SLUG_ORIGINAL


DIR_TRANSCRIPTS = dir_por_defecto()


def ts(valor: str | None):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def recolectar(desde, hasta, sesion: Path | None, raiz: Path | None = None):
    global DIR_TRANSCRIPTS
    if raiz:
        DIR_TRANSCRIPTS = raiz
    if sesion:
        archivos = [sesion]
    else:
        archivos = sorted(DIR_TRANSCRIPTS.glob("*.jsonl"))
        archivos += sorted(DIR_TRANSCRIPTS.glob("*/subagents/agent-*.jsonl"))
    mejor: dict[str, dict] = {}
    for archivo in archivos:
        if not archivo.exists():
            continue
        for linea in archivo.open(encoding="utf-8"):
            try:
                d = json.loads(linea)
            except json.JSONDecodeError:
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            uso = msg.get("usage")
            if not uso:
                continue
            clave = d.get("requestId") or d.get("uuid")
            momento = ts(d.get("timestamp"))
            if desde and (momento is None or momento < desde):
                continue
            if hasta and (momento is None or momento > hasta):
                continue
            fila = {
                "modelo": msg.get("model", "desconocido"),
                "subagente": "subagents" in str(archivo),
                "in": uso.get("input_tokens", 0) or 0,
                "cache_w": uso.get("cache_creation_input_tokens", 0) or 0,
                "cache_r": uso.get("cache_read_input_tokens", 0) or 0,
                "out": uso.get("output_tokens", 0) or 0,
            }
            # T2: por requestId nos quedamos con el bloque de mayor salida
            previo = mejor.get(clave)
            if previo is None or fila["out"] > previo["out"]:
                mejor[clave] = fila
    return list(mejor.values())


def normalizar(modelo: str) -> str:
    """Los ids llegan a veces con sufijo de fecha (claude-haiku-4-5-20251001).
    Sin normalizar, el modelo no matchea la tabla y su costo se cuenta como cero —
    que es exactamente como se subestima el brazo mas barato de un banco de pruebas."""
    for base in PRECIOS:
        if modelo == base or modelo.startswith(base + "-"):
            return base
    return modelo


def costo(fila) -> float:
    p = PRECIOS.get(normalizar(fila["modelo"]))
    if not p:
        return 0.0
    return (
        fila["in"] * p["in"]
        + fila["cache_w"] * p["in"] * MULT_CACHE_ESCRITURA
        + fila["cache_r"] * p["in"] * MULT_CACHE_LECTURA
        + fila["out"] * p["out"]
    ) / 1_000_000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--sesion", type=Path)
    ap.add_argument("--transcripts", type=Path,
                    help="Directorio de transcripts (por defecto ~/.claude/projects/<slug>). "
                         "Permite correr el script en otra maquina o sobre transcripts archivados.")
    ap.add_argument("--json", action="store_true", help="salida en JSON para metadata.json")
    a = ap.parse_args()

    filas = recolectar(ts(a.desde), ts(a.hasta), a.sesion, a.transcripts)
    if not filas:
        print("sin datos en ese rango")
        return

    por_modelo: dict[str, dict] = {}
    for f in filas:
        acc = por_modelo.setdefault(f["modelo"], {
            "llamadas": 0, "in": 0, "cache_w": 0, "cache_r": 0, "out": 0, "usd": 0.0, "subagente": 0
        })
        acc["llamadas"] += 1
        acc["subagente"] += int(f["subagente"])
        for k in ("in", "cache_w", "cache_r", "out"):
            acc[k] += f[k]
        acc["usd"] += costo(f)

    total = {"llamadas": 0, "in": 0, "cache_w": 0, "cache_r": 0, "out": 0, "usd": 0.0}
    for acc in por_modelo.values():
        for k in total:
            total[k] += acc[k]

    if a.json:
        print(json.dumps({"por_modelo": por_modelo, "total": total}, indent=2, ensure_ascii=False))
        return

    print(f"| Modelo | Llamadas | (subag.) | Entrada | Caché escr. | Caché lect. | Salida | USD |")
    print(f"| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for m, acc in sorted(por_modelo.items()):
        print(f"| `{m}` | {acc['llamadas']} | {acc['subagente']} | {acc['in']:,} | "
              f"{acc['cache_w']:,} | {acc['cache_r']:,} | {acc['out']:,} | {acc['usd']:.4f} |")
    print(f"| **total** | **{total['llamadas']}** | | **{total['in']:,}** | "
          f"**{total['cache_w']:,}** | **{total['cache_r']:,}** | **{total['out']:,}** | "
          f"**{total['usd']:.4f}** |")


if __name__ == "__main__":
    main()
