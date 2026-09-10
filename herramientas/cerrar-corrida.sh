#!/usr/bin/env bash
# Cierra una corrida: marca el fin, valida, regenera el markdown, mide el consumo real
# y deja los formularios de FIRMA y NOTAS para que los complete una persona.
#
#   bash herramientas/cerrar-corrida.sh corridas/04-2026-09-28-w40
#
# Deliberadamente NO decide si la corrida es apta para firma: eso lo dice el editor-qa
# en el JSON y lo confirma un humano en FIRMA.md. El script mide y ordena; no firma.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -ne 1 ]]; then echo "uso: bash herramientas/cerrar-corrida.sh <corridas/ID>"; exit 2; fi
DIR="${1%/}"
[[ -d "$DIR" ]] || { echo "✗ no existe $DIR"; exit 1; }
JSON="$DIR/salida/plan_semanal.json"
[[ -f "$JSON" ]] || { echo "✗ falta $JSON — la corrida no produjo salida"; exit 1; }

[[ -f "$DIR/ventana-fin.txt" ]] || date -u +%Y-%m-%dT%H:%M:%SZ > "$DIR/ventana-fin.txt"
INICIO=$(cat "$DIR/ventana-inicio.txt" 2>/dev/null || echo "")
FIN=$(cat "$DIR/ventana-fin.txt")
echo "── ventana de la corrida: ${INICIO:-¿sin ventana-inicio.txt?} → $FIN"

echo
echo "── 1/4 · validador (exit 0 obligatorio para una corrida entregable)"
set +e
python3 herramientas/validar.py "$JSON"
VALIDADOR=$?
set -e
[[ $VALIDADOR -eq 0 ]] && ESTADO="exit 0" || ESTADO="exit $VALIDADOR"

echo
echo "── 2/4 · markdown regenerado desde el JSON (nunca se edita a mano)"
python3 herramientas/render.py "$JSON"

echo
echo "── 3/4 · consumo real medido sobre los transcripts"
if [[ -n "$INICIO" ]]; then
  if python3 herramientas/costo.py --desde "$INICIO" --hasta "$FIN" --json > "$DIR/consumo.json" 2>/dev/null \
     && python3 -c "import json,sys; json.load(open('$DIR/consumo.json'))" 2>/dev/null; then
    python3 herramientas/costo.py --desde "$INICIO" --hasta "$FIN"
  else
    rm -f "$DIR/consumo.json"
    echo "⚠ no se pudo medir: no hay transcripts en esa ventana."
    echo "  Pasá el directorio con --transcripts, o anotá en metadata.json que el consumo"
    echo "  no se midió. Una corrida sin consumo medido se declara, no se estima."
  fi
else
  echo "⚠ sin ventana-inicio.txt no hay ventana que medir."
fi

echo
echo "── 4/4 · metadata y formularios"
python3 - "$DIR" "$ESTADO" <<'PY'
import json, sys, pathlib
d = pathlib.Path(sys.argv[1]); estado = sys.argv[2]
plan = json.loads((d / "salida" / "plan_semanal.json").read_text(encoding="utf-8"))
consumo = json.loads((d / "consumo.json").read_text(encoding="utf-8")) if (d / "consumo.json").exists() else None
meta = d / "metadata.json"
datos = {
    "corrida": d.name.split("-")[0],
    "semana": plan.get("semana"),
    "inicio_utc": (d / "ventana-inicio.txt").read_text().strip() if (d / "ventana-inicio.txt").exists() else None,
    "fin_utc": (d / ".fin").read_text().strip(),
    "contrato": "v3",
    "schema": "v3",
    "modelo_todos_los_agentes": plan.get("modelo"),
    "agentes_invocados": ["estratega-posicionamiento", "redactor-contenido",
                          "community-social", "seo-analista", "editor-qa"],
    "olas": 3,
    "herramientas_reales_usadas": ["Read/Glob/Grep sobre activos/", "Write sobre contexto/marca.md",
                                   "validar.py", "render.py"],
    "validador": estado,
    # Lo que dio al cerrarla y lo que da hoy. Empiezan iguales y pueden separarse: si
    # mas adelante se agrega un control, una corrida vieja pasa a fallar y se actualiza
    # SOLO `validador_actual`, sin retocar la salida. El control D6 de verificar-repo.py
    # compara ese campo contra la realidad. Precedente: la corrida 01 y el control C3.
    "validador_actual": estado,
    "apto_para_firma": (plan.get("control_calidad") or {}).get("apto_para_firma"),
    "consumo": consumo,
    "nota_de_atribucion": "COMPLETAR: ¿la ventana estuvo limpia o hubo algo corriendo en paralelo?",
}
if meta.exists():          # no pisar una metadata ya curada a mano
    previo = json.loads(meta.read_text(encoding="utf-8"))
    previo.update({k: v for k, v in datos.items() if v is not None})
    datos = previo
meta.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"✓ {meta}")

firma = d / "FIRMA.md"
if not firma.exists():
    apto = datos["apto_para_firma"]
    firma.write_text(
        f"# Firma — corrida {datos['corrida']}\n\n"
        f"**Estado: NO FIRMADA.** Firmante: — · Fecha: —\n\n"
        f"> El editor-qa declaró `apto_para_firma: {apto}`. Eso es evidencia, no una firma.\n"
        f"> Firmar es un acto humano: se completa este archivo a mano, después de recorrer\n"
        f"> los 8 ítems del checklist de `GOBIERNO.md` §3.\n\n"
        f"## Por qué no se firma\n\n"
        f"1. <bloqueante concreto, con la pieza y la línea>\n\n"
        f"## O, si se firma\n\n"
        f"Reemplazar el encabezado por firmante y fecha, y dejar escrito qué se verificó\n"
        f"a mano de los 8 ítems del checklist y con qué resultado.\n", encoding="utf-8")
    print(f"✓ {firma} (formulario, sin completar)")
else:
    print(f"· {firma} ya existía, no se toca")

notas = d / "NOTAS.md"
if not notas.exists():
    notas.write_text(
        f"# Notas — corrida {datos['corrida']}\n\n"
        f"## Contraste contra las hipótesis de `entrada.md`\n\n"
        f"| # | Hipótesis anotada antes | Qué pasó | ¿Se cumplió? |\n| --- | --- | --- | --- |\n"
        f"| 1 | | | |\n| 2 | | | |\n| 3 | | | |\n\n"
        f"## Lo que no estaba previsto\n\n"
        f"<El valor de una corrida está acá: lo que apareció y ninguna hipótesis esperaba.>\n\n"
        f"## Qué cambia en el sistema por esta corrida\n\n"
        f"<Restricción nueva, control nuevo, o nada — y por qué nada también es una decisión.>\n",
        encoding="utf-8")
    print(f"✓ {notas} (formulario, sin completar)")
else:
    print(f"· {notas} ya existía, no se toca")
PY

echo
echo "Falta lo que ningún script puede hacer:"
echo "  1. completar $DIR/NOTAS.md contrastando contra las hipótesis de entrada.md"
echo "  2. recorrer los 8 ítems del checklist de GOBIERNO.md §3"
echo "  3. firmar o no firmar en $DIR/FIRMA.md, con el motivo escrito"
