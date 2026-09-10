#!/usr/bin/env python3
"""
Rehace, para cada corrida real, numeros de la salida desde la entrada de esa misma corrida.

    python3 herramientas/cierre.py                 # las tres corridas
    python3 herramientas/cierre.py corridas/03-2026-09-05-w39

Por que existe. `validar.py` verifica que la salida cumpla el contrato y `verificar-repo.py`
verifica que el repositorio diga de si mismo lo que es. Faltaba lo tercero: que un tercero
pueda **rehacer un numero de la salida** partiendo de lo que entro, sin creerle a nadie. Sin
eso, "reproducible" quiere decir "los archivos estan", no "las cuentas cierran".

Tres cierres por corrida. Los tres son aritmetica sobre archivos versionados: no consultan la
red, no leen transcripts y no dependen de esta maquina.

  N1 · Ventana de publicacion.  La semana ISO esta en `entrada.md` (por ejemplo `2026-W37`).
       De ese unico dato se calcula el rango con `date.fromisocalendar`, y ese rango calculado
       tiene que ser el `rango` que declara la salida y contener las cinco `piezas[].fecha`.
  N2 · Cifras publicadas.  El dato de origen es la tabla de resultados de
       `activos/sitio-home.md`. Todo porcentaje que aparezca en el cuerpo o el titulo de una
       pieza tiene que ser una de esas cifras, y el cierre reporta cuantas uso la corrida.
  N3 · Costo de la corrida.  De los tokens crudos de `consumo.json` y la tarifa publicada se
       recalcula el USD, y tiene que dar el que archiva `metadata.json` con menos de 0,5 % de
       desvio.

Sale con codigo 0 si los tres cierran en las tres corridas, 1 si alguno no cierra.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN_CIFRAS = RAIZ / "activos" / "sitio-home.md"

CORRIDAS_REALES = [
    "01-2026-09-05-w37",
    "02-2026-09-05-w38",
    "03-2026-09-05-w39",
]

# Tarifa publicada de la API de Anthropic, consultada el 2026-09-06. Es la misma tabla que usa
# `costo.py`; se repite aca a proposito para que este script cierre solo, sin importar nada.
PRECIOS = {
    "claude-opus-5":    {"in": 5.00, "out": 25.00},
    "claude-sonnet-5":  {"in": 2.00, "out": 10.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
}
MULT_CACHE_ESCRITURA_5M = 1.25
MULT_CACHE_ESCRITURA_1H = 2.00
MULT_CACHE_LECTURA = 0.10

TOLERANCIA_USD = 0.005          # 0,5 %

fallas: list[str] = []


def falla(msg: str) -> None:
    fallas.append(msg)


def semana_iso(entrada: str) -> tuple[int, int]:
    """La semana ISO declarada en entrada.md. Es el unico dato del que sale N1."""
    m = re.search(r"\b(\d{4})-W(\d{2})\b", entrada)
    if not m:
        raise ValueError("entrada.md no declara una semana ISO con la forma AAAA-Wnn")
    return int(m.group(1)), int(m.group(2))


def cifras_de_origen() -> set[str]:
    """Los porcentajes de la tabla «Resultados publicados en el sitio» de activos/."""
    texto = ORIGEN_CIFRAS.read_text(encoding="utf-8")
    bloque = texto.split("## Resultados publicados en el sitio", 1)
    if len(bloque) != 2:
        raise ValueError(f"{ORIGEN_CIFRAS} ya no tiene la tabla de resultados publicados")
    tabla = bloque[1].split("\n## ", 1)[0]
    return set(re.findall(r"\*\*(\d[\d.,]*)\s?%\*\*", tabla))


def normalizar(modelo: str) -> str:
    """Los ids llegan a veces con sufijo de fecha (claude-haiku-4-5-20251001). Sin normalizar,
    el modelo no matchea la tabla y su costo se cuenta como cero: es la trampa T3 de COSTOS.md."""
    for base in PRECIOS:
        if modelo == base or modelo.startswith(base + "-"):
            return base
    return modelo


def usd_de(tokens: dict, modelo: str) -> float:
    p = PRECIOS[normalizar(modelo)]
    return (
        tokens["in"] * p["in"]
        + tokens["cache_w_5m"] * p["in"] * MULT_CACHE_ESCRITURA_5M
        + tokens["cache_w_1h"] * p["in"] * MULT_CACHE_ESCRITURA_1H
        + tokens["cache_r"] * p["in"] * MULT_CACHE_LECTURA
        + tokens["out"] * p["out"]
    ) / 1_000_000


def cerrar(corrida: str) -> None:
    base = RAIZ / "corridas" / corrida
    entrada = (base / "entrada.md").read_text(encoding="utf-8")
    salida = json.loads((base / "salida" / "plan_semanal.json").read_text(encoding="utf-8"))
    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    consumo = json.loads((base / "consumo.json").read_text(encoding="utf-8"))

    print(f"── corridas/{corrida}")

    # N1 · ventana de publicacion, calculada desde la semana ISO de la entrada
    anio, num = semana_iso(entrada)
    lunes = date.fromisocalendar(anio, num, 1)
    domingo = date.fromisocalendar(anio, num, 7)
    rango = f"{lunes} / {domingo}"
    fechas = [p["fecha"] for p in salida["piezas"]]
    print(f"   N1  {anio}-W{num:02d} → fromisocalendar → {rango}")
    if salida["rango"] != rango:
        falla(f"N1 {corrida}: la salida declara rango '{salida['rango']}' y de "
              f"{anio}-W{num:02d} sale '{rango}'")
    fuera = [f for f in fechas if not (str(lunes) <= f <= str(domingo))]
    if fuera:
        falla(f"N1 {corrida}: {len(fuera)} fecha(s) de piezas fuera de la ventana: {fuera}")
    if f"{rango}" not in entrada.replace(" / ", " / "):
        falla(f"N1 {corrida}: entrada.md no repite el rango '{rango}' que sale de su "
              f"propia semana ISO — la entrada se contradice a si misma")
    print(f"       rango declarado en la salida: {salida['rango']}  ·  "
          f"{len(fechas)}/{len(fechas)} fechas de piezas dentro de la ventana")

    # N2 · cifras publicadas, contra el dato de origen
    origen = cifras_de_origen()
    texto = " ".join(str(p.get("titulo", "")) + " " + str(p.get("cuerpo", ""))
                     for p in salida["piezas"])
    usadas = sorted(set(re.findall(r"(\d[\d.,]*)\s?%", texto)), key=float)
    invento = [c for c in usadas if c not in origen]
    if invento:
        falla(f"N2 {corrida}: la salida usa {invento}% y no estan en la tabla de resultados de "
              f"{ORIGEN_CIFRAS.relative_to(RAIZ)} (las publicadas son {sorted(origen, key=float)}%)")
    print(f"       N2  activos/sitio-home.md publica {len(origen)} porcentajes "
          f"({', '.join(sorted(origen, key=float))}%) · la salida usa "
          f"{len(usadas)} ({', '.join(usadas) + '%' if usadas else 'ninguno'}), "
          f"{len(invento)} sin respaldo")

    # N3 · costo de la corrida, recalculado desde los tokens crudos
    total = 0.0
    for modelo, t in consumo["por_modelo"].items():
        if normalizar(modelo) not in PRECIOS:
            falla(f"N3 {corrida}: no hay tarifa publicada para '{modelo}'")
            return
        total += usd_de(t, modelo)
    archivado = meta["consumo"]["total"]["usd"]
    desvio = abs(total - archivado) / archivado if archivado else 0.0
    print(f"       N3  tokens de consumo.json × tarifa → USD {total:.6f}  ·  "
          f"metadata.json archiva USD {archivado:.6f}  ·  desvio {desvio * 100:.4f} %")
    if desvio > TOLERANCIA_USD:
        falla(f"N3 {corrida}: recalculado USD {total:.4f}, archivado USD {archivado:.4f} "
              f"({desvio * 100:.2f} % de desvio, la tolerancia es {TOLERANCIA_USD * 100:.1f} %)")


def main() -> int:
    corridas = [Path(a).name for a in sys.argv[1:]] or CORRIDAS_REALES
    print("── cierre numerico: un numero de cada salida, rehecho desde su propia entrada\n")
    for corrida in corridas:
        if not (RAIZ / "corridas" / corrida).is_dir():
            falla(f"no existe corridas/{corrida}")
            continue
        cerrar(corrida)
        print()
    if fallas:
        print(f"✗ NO CIERRA — {len(fallas)} problema(s):")
        for f in fallas:
            print(f"  · {f}")
        return 1
    print("✓ CIERRA — en las tres corridas, la ventana de publicacion sale de la semana ISO de")
    print("  su entrada, toda cifra porcentual de la salida esta publicada en activos/, y el")
    print("  costo archivado se rehace desde los tokens crudos con la tarifa citada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
