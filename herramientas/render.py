#!/usr/bin/env python3
"""
Genera salida/plan.md a partir de salida/plan_semanal.json.

    python3 herramientas/render.py corridas/01-*/salida/plan_semanal.json

Por qué existe: el §5 del contrato exige dos entregables, el JSON (dato) y el markdown
(legible para quien firma). Escribirlos por separado los hace derivar — riesgo que el
editor-qa marcó en la corrida 01. Generando uno del otro, la deriva es imposible por
construcción: el markdown no puede decir algo que el JSON no diga.
"""
import json
import sys
from pathlib import Path

CANAL = {"blog": "Blog", "linkedin": "LinkedIn", "x": "X", "newsletter": "Newsletter"}


def main() -> int:
    origen = Path(sys.argv[1])
    d = json.loads(origen.read_text(encoding="utf-8"))
    destino = origen.parent / "plan.md"
    a = d["angulo_semanal"]
    cc = d["control_calidad"]
    L: list[str] = []

    L.append(f"# Plan de contenidos — semana {d['semana']}")
    L.append("")
    L.append(f"> **Generado automáticamente desde `plan_semanal.json`** con "
             f"`herramientas/render.py`. No editar a mano: los cambios se pierden.")
    L.append(f"> Rango {d['rango']} · generado {d['generado_utc']} · modelo `{d.get('modelo','—')}`")
    L.append("")
    estado = "✅ APTA PARA FIRMA" if cc["apto_para_firma"] else "⛔ NO APTA PARA FIRMA"
    L.append(f"**{estado}** — firmante: `{d['firma']['firmante'] or 'sin firmar'}`")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Ángulo de la semana")
    L.append("")
    L.append(f"### {a['titular']}")
    L.append("")
    L.append(a["tesis"])
    L.append("")
    L.append(f"| | |\n| --- | --- |")
    L.append(f"| **Pilar Native Reach** | {a['pilar_native-reach']} |")
    L.append(f"| **Público** | {a['publico']} |")
    L.append(f"| **CTA** | {a['cta']} |")
    L.append("")
    L.append("## Calendario")
    L.append("")
    L.append("| Fecha | Canal | id | Título |")
    L.append("| --- | --- | --- | --- |")
    for p in sorted(d["piezas"], key=lambda x: (x["fecha"], x["canal"])):
        L.append(f"| {p['fecha']} | {CANAL.get(p['canal'], p['canal'])} | `{p['id']}` | {p['titulo']} |")
    L.append("")
    L.append("## Piezas")
    for p in d["piezas"]:
        L.append("")
        L.append(f"### `{p['id']}` · {CANAL.get(p['canal'], p['canal'])} · {p['fecha']}")
        L.append("")
        L.append(f"**{p['titulo']}**")
        L.append("")
        L.append(p["cuerpo"])
        L.append("")
        L.append(f"**CTA:** {p['cta']}")
        L.append("")
        L.append(f"**Firma:** {p.get('firma_autor') or '_sin firma de autor (voz de marca)_'}")
        if p.get("keywords"):
            L.append("")
            L.append("**Keywords:** " + " · ".join(f"`{k}`" for k in p["keywords"]))
        L.append("")
        L.append("**Fuentes:** " + " · ".join(f"`{f}`" for f in p["fuentes"]))
    L.append("")
    L.append("## SEO")
    L.append("")
    s = d["seo"]
    L.append(f"**Keyword principal:** `{s['keyword_principal']}`")
    L.append("")
    L.append("**Secundarias:** " + " · ".join(f"`{k}`" for k in s["keywords_secundarias"]))
    L.append("")
    L.append("| Desde | Hacia | Anchor |")
    L.append("| --- | --- | --- |")
    ids = {p["id"] for p in d["piezas"]}
    for e in s["enlazado_interno"]:
        marca = "" if e["desde"] in ids else " ⚠️ *id inexistente*"
        L.append(f"| `{e['desde']}`{marca} | `{e['hacia']}` | {e['anchor']} |")
    L.append("")
    L.append("## Control de calidad")
    L.append("")
    L.append(f"**Apto para firma: {'sí' if cc['apto_para_firma'] else 'NO'}**")
    for titulo, clave in (("Cifras usadas", "cifras_usadas"),
                          ("Datos faltantes", "datos_faltantes"),
                          ("Riesgos", "riesgos")):
        L.append("")
        L.append(f"### {titulo} ({len(cc[clave])})")
        L.append("")
        if not cc[clave]:
            L.append("_ninguno registrado_")
        for item in cc[clave]:
            if isinstance(item, dict):
                L.append(f"- **{item['cifra']}** → `{item['fuente']}`")
            else:
                L.append(f"- {item}")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Firma")
    L.append("")
    L.append(f"- Requiere firma humana: **{d['firma']['requiere_firma_humana']}** (R3, siempre)")
    L.append(f"- Firmante: **{d['firma']['firmante'] or 'sin firmar'}**")
    L.append(f"- Fecha de firma: **{d['firma']['fecha_firma'] or '—'}**")
    L.append("")

    destino.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ {destino} — {len(d['piezas'])} piezas, "
          f"{len(cc['riesgos'])} riesgos, apto_para_firma={cc['apto_para_firma']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
