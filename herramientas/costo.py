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

# USD por millon de token. Precios de lista de la API de Anthropic, tomados de
# https://platform.claude.com/docs/en/about-claude/pricing (seccion "Model pricing"),
# consultado el 2026-09-06. No son estimaciones ni promedios: son las dos columnas
# "Base input tokens" y "Output tokens" de esa tabla.
PRECIOS = {
    "claude-opus-5":   {"in": 5.00, "out": 25.00},
    "claude-sonnet-5": {"in": 2.00, "out": 10.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
}
# Multiplicadores de cache sobre el precio de entrada, de la tabla "Prompt caching" de la
# misma pagina. NO son un supuesto de este trabajo: son tarifa publicada.
#   escritura con TTL de 5 minutos -> 1,25x   ·   escritura con TTL de 1 hora -> 2,00x
#   lectura (cache hit)            -> 0,10x
MULT_CACHE_ESCRITURA_5M = 1.25
MULT_CACHE_ESCRITURA_1H = 2.00
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
            # T4: la escritura de cache no tiene UN precio. El transcript trae el desglose
            # por TTL en usage.cache_creation; el campo plano cache_creation_input_tokens
            # los suma y no distingue. Cobrar todo a 1,25x subestima las escrituras de 1 hora,
            # que valen 2,00x. Si el desglose no viene (transcripts viejos), se cae al plano
            # y se cobra a 5m, que es el default de Claude Code.
            cc = uso.get("cache_creation") or {}
            cw_5m = cc.get("ephemeral_5m_input_tokens")
            cw_1h = cc.get("ephemeral_1h_input_tokens")
            if cw_5m is None and cw_1h is None:
                cw_5m, cw_1h = uso.get("cache_creation_input_tokens", 0) or 0, 0
            cw_5m, cw_1h = cw_5m or 0, cw_1h or 0
            fila = {
                "modelo": msg.get("model", "desconocido"),
                "subagente": "subagents" in str(archivo),
                "in": uso.get("input_tokens", 0) or 0,
                "cache_w_5m": cw_5m,
                "cache_w_1h": cw_1h,
                "cache_w": cw_5m + cw_1h,
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
        + fila["cache_w_5m"] * p["in"] * MULT_CACHE_ESCRITURA_5M
        + fila["cache_w_1h"] * p["in"] * MULT_CACHE_ESCRITURA_1H
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
            "llamadas": 0, "in": 0, "cache_w": 0, "cache_w_5m": 0, "cache_w_1h": 0,
            "cache_r": 0, "out": 0, "usd": 0.0, "subagente": 0
        })
        acc["llamadas"] += 1
        acc["subagente"] += int(f["subagente"])
        for k in ("in", "cache_w", "cache_w_5m", "cache_w_1h", "cache_r", "out"):
            acc[k] += f[k]
        acc["usd"] += costo(f)

    total = {"llamadas": 0, "in": 0, "cache_w": 0, "cache_w_5m": 0, "cache_w_1h": 0,
             "cache_r": 0, "out": 0, "usd": 0.0}
    for acc in por_modelo.values():
        for k in total:
            total[k] += acc[k]

    if a.json:
        print(json.dumps({"por_modelo": por_modelo, "total": total}, indent=2, ensure_ascii=False))
        return

    print(f"| Modelo | Llamadas | (subag.) | Entrada | Caché escr. 5m | Caché escr. 1h | Caché lect. | Salida | USD |")
    print(f"| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for m, acc in sorted(por_modelo.items()):
        print(f"| `{m}` | {acc['llamadas']} | {acc['subagente']} | {acc['in']:,} | "
              f"{acc['cache_w_5m']:,} | {acc['cache_w_1h']:,} | {acc['cache_r']:,} | "
              f"{acc['out']:,} | {acc['usd']:.4f} |")
    print(f"| **total** | **{total['llamadas']}** | | **{total['in']:,}** | "
          f"**{total['cache_w_5m']:,}** | **{total['cache_w_1h']:,}** | **{total['cache_r']:,}** | "
          f"**{total['out']:,}** | **{total['usd']:.4f}** |")


if __name__ == "__main__":
    main()
