#!/usr/bin/env python3
"""
Valida una salida del equipo de agentes contra esquemas/plan_semanal.schema.json.

Sin dependencias: solo biblioteca estándar. Se corre así:

    python3 herramientas/validar.py corridas/01-*/salida/plan_semanal.json

Además de la validación de esquema, aplica dos controles que un JSON Schema no puede expresar
y que son el corazón del contrato:

  C1 · Trazabilidad — cada ruta declarada en `fuentes` tiene que existir en el repo.
  C2 · Antialucinación — toda cifra con % o multiplicador (12%, 3x) que aparezca en el cuerpo
       de una pieza tiene que aparecer literalmente en algún archivo de activos/.
  C3 · Integridad referencial — cada `seo.enlazado_interno[].desde` tiene que ser el id de una
       pieza que exista en este mismo plan. Agregado tras la corrida 01, donde 5 de 7 enlaces
       apuntaban a piezas inexistentes y el validador salió con exit 0 igual.

Sale con código 0 si pasa, 1 si falla. Ese código es la definición operativa de
«output estructurado»: no es una promesa del README, es un proceso que falla.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESQUEMA = RAIZ / "esquemas" / "plan_semanal.schema.json"
ACTIVOS = RAIZ / "activos"

errores: list[str] = []
avisos: list[str] = []


def err(msg: str) -> None:
    errores.append(msg)


def validar_tipo(valor, esperado, ruta: str) -> bool:
    tipos = {
        "object": dict, "array": list, "string": str,
        "boolean": bool, "number": (int, float), "integer": int,
    }
    if isinstance(esperado, list):
        if "null" in esperado and valor is None:
            return True
        return any(validar_tipo(valor, t, ruta) for t in esperado if t != "null")
    if esperado == "boolean":
        return isinstance(valor, bool)
    py = tipos.get(esperado)
    if py is None:
        return True
    if esperado in ("number", "integer") and isinstance(valor, bool):
        return False
    return isinstance(valor, py)


def validar_nodo(dato, esquema: dict, ruta: str = "$") -> None:
    """Subconjunto de JSON Schema suficiente para este contrato."""
    if "enum" in esquema and dato not in esquema["enum"]:
        err(f"{ruta}: '{dato}' no está en {esquema['enum']}")
        return
    if "const" in esquema and dato != esquema["const"]:
        err(f"{ruta}: debe ser {esquema['const']!r}, es {dato!r}")
        return

    if "type" in esquema and not validar_tipo(dato, esquema["type"], ruta):
        err(f"{ruta}: se esperaba tipo {esquema['type']}, llegó {type(dato).__name__}")
        return

    if isinstance(dato, str):
        if "minLength" in esquema and len(dato) < esquema["minLength"]:
            err(f"{ruta}: {len(dato)} caracteres, el mínimo es {esquema['minLength']}")
        if "maxLength" in esquema and len(dato) > esquema["maxLength"]:
            err(f"{ruta}: {len(dato)} caracteres, el máximo es {esquema['maxLength']}")
        if "pattern" in esquema and not re.match(esquema["pattern"], dato):
            err(f"{ruta}: '{dato}' no cumple el patrón {esquema['pattern']}")

    if isinstance(dato, list):
        if "minItems" in esquema and len(dato) < esquema["minItems"]:
            err(f"{ruta}: {len(dato)} elementos, el mínimo es {esquema['minItems']}")
        if "maxItems" in esquema and len(dato) > esquema["maxItems"]:
            err(f"{ruta}: {len(dato)} elementos, el máximo es {esquema['maxItems']}")
        if "items" in esquema:
            for i, item in enumerate(dato):
                validar_nodo(item, esquema["items"], f"{ruta}[{i}]")

    if isinstance(dato, dict):
        for req in esquema.get("required", []):
            if req not in dato:
                err(f"{ruta}: falta la clave obligatoria '{req}'")
        props = esquema.get("properties", {})
        if esquema.get("additionalProperties") is False:
            for k in dato:
                if k not in props:
                    err(f"{ruta}: clave no permitida '{k}'")
        for k, v in dato.items():
            if k in props:
                validar_nodo(v, props[k], f"{ruta}.{k}")


def texto_activos() -> str:
    partes = []
    for p in sorted(ACTIVOS.rglob("*")):
        if p.is_file():
            try:
                partes.append(p.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                pass
    return "\n".join(partes)


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: python3 herramientas/validar.py <ruta a plan_semanal.json>")
        return 2

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"✗ no existe: {ruta}")
        return 1

    try:
        dato = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ JSON inválido: {e}")
        return 1

    esquema = json.loads(ESQUEMA.read_text(encoding="utf-8"))
    validar_nodo(dato, esquema)

    # C1 · trazabilidad: las fuentes declaradas tienen que existir
    for i, pieza in enumerate(dato.get("piezas", []) or []):
        if not isinstance(pieza, dict):
            continue
        for f in pieza.get("fuentes", []) or []:
            if not (RAIZ / f).exists():
                err(f"C1 piezas[{i}].fuentes: '{f}' no existe en el repo")
    for i, c in enumerate((dato.get("control_calidad") or {}).get("cifras_usadas", []) or []):
        if isinstance(c, dict) and not (RAIZ / c.get("fuente", "")).exists():
            err(f"C1 cifras_usadas[{i}]: la fuente '{c.get('fuente')}' no existe en el repo")

    # C2 · antialucinación: toda cifra con % o multiplicador debe estar en activos/
    corpus = texto_activos()
    patron = re.compile(r"\b\d[\d.,]*\s?%|\b\d[\d.,]*\s?[xX]\b")
    for i, pieza in enumerate(dato.get("piezas", []) or []):
        if not isinstance(pieza, dict):
            continue
        for cifra in set(patron.findall(str(pieza.get("cuerpo", "")) + " " + str(pieza.get("titulo", "")))):
            nucleo = re.sub(r"\s", "", cifra)
            if nucleo not in re.sub(r"\s", "", corpus):
                err(f"C2 piezas[{i}] ({pieza.get('id')}): la cifra '{cifra}' no aparece en ningún activo")

    # C3 · integridad referencial: los enlaces internos apuntan a piezas de este plan
    ids_piezas = {p.get("id") for p in (dato.get("piezas") or []) if isinstance(p, dict)}
    for i, e in enumerate((dato.get("seo") or {}).get("enlazado_interno", []) or []):
        if isinstance(e, dict) and e.get("desde") not in ids_piezas:
            err(f"C3 seo.enlazado_interno[{i}]: 'desde' = '{e.get('desde')}' no es el id de "
                f"ninguna pieza de este plan (ids reales: {sorted(ids_piezas)})")

    if (dato.get("firma") or {}).get("firmante") is not None:
        avisos.append("firma.firmante ya está completo: esta salida fue firmada por un humano")

    print(f"── validación de {ruta}")
    for a in avisos:
        print(f"  ⚠ {a}")
    if errores:
        print(f"✗ FALLA — {len(errores)} error(es):")
        for e in errores:
            print(f"  · {e}")
        return 1
    piezas = len(dato.get("piezas", []))
    faltantes = len((dato.get("control_calidad") or {}).get("datos_faltantes", []))
    print(f"✓ PASA — {piezas} piezas · {faltantes} dato(s) marcados como faltantes · "
          f"apto_para_firma={(dato.get('control_calidad') or {}).get('apto_para_firma')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
