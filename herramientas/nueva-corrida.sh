#!/usr/bin/env bash
# Arma el directorio de una corrida nueva y lo deja listo para ejecutar.
#
#   bash herramientas/nueva-corrida.sh 2026-W40 2026-09-28 2026-10-04
#
# Crea corridas/<NN>-<hoy>-w<NN semana>/ con entrada.md a completar, salida/ vacio y la
# marca .inicio. NO invoca ningun agente: la corrida la dispara una persona, con el
# prompt que imprime OPERACION.md paso 3.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -lt 1 ]]; then
  echo "uso: bash herramientas/nueva-corrida.sh <SEMANA ISO> [<FECHA INICIO> <FECHA FIN>]"
  echo "ej.: bash herramientas/nueva-corrida.sh 2026-W40 2026-09-28 2026-10-04"
  exit 2
fi

SEMANA="$1"
DESDE="${2:-<AAAA-MM-DD>}"
HASTA="${3:-<AAAA-MM-DD>}"

if [[ ! "$SEMANA" =~ ^[0-9]{4}-W[0-9]{2}$ ]]; then
  echo "✗ la semana se escribe en ISO: AAAA-Wnn (ej. 2026-W40)"; exit 2
fi

WNN=$(echo "$SEMANA" | sed 's/.*-W/w/')
HOY=$(date -u +%Y-%m-%d)
ULTIMA=$(ls -1d corridas/[0-9][0-9]-* 2>/dev/null | sed 's|corridas/||; s|-.*||' | sort -n | tail -1)
NN=$(printf "%02d" $(( 10#${ULTIMA:-0} + 1 )))
DIR="corridas/${NN}-${HOY}-${WNN}"

if [[ -e "$DIR" ]]; then echo "✗ ya existe $DIR"; exit 1; fi

mkdir -p "$DIR/salida"
date -u +%Y-%m-%dT%H:%M:%SZ > "$DIR/.inicio"

cat > "$DIR/entrada.md" <<EOF
# Corrida ${NN} — semana ${SEMANA}

**Contrato:** v3 · **Schema:** v3 · **Modelo:** \`claude-sonnet-5\` en los cinco especialistas.

## Diseño del experimento

<Por qué se corre esta semana y qué se quiere aprender. Si la corrida no prueba nada,
es una ejecución, no un experimento — y conviene decir eso también.>

## Brief enviado

\`\`\`
Armá el plan de contenidos para la semana ${SEMANA} (${DESDE} / ${HASTA}).

CONTEXTO DE ESTA SEMANA
  Disparador:        <qué hecho real justifica hablar de esto ahora>
  Público objetivo:  <a quién le hablamos, con cargo y problema>
  Objetivo:          <demanda | autoridad | activación>
  CTA:               <la url exacta a la que mandamos>
  Pilar sugerido:    <InSpeech | InContext | InRegion | que lo elija el estratega>

RESTRICCIONES DE ESTA SEMANA
  <límites propios de la semana: qué no repetir, qué no nombrar, qué embargo respetar>

ENTREGA
  Escribí ${DIR}/salida/plan_semanal.json y ${DIR}/salida/plan.md.
  Corré python3 herramientas/validar.py sobre el JSON antes de terminar.
  Si el validador falla, arreglá el JSON — no toques el validador ni el schema.
\`\`\`

## Hipótesis anotadas antes de correr

Se escriben ACÁ y ANTES de disparar la corrida. Contrastarlas después es lo que
convierte la corrida en evidencia; escribirlas después es escribir el resultado.

1. <hipótesis principal — la que el diseño de esta semana pone a prueba>
2. <qué se espera que el sistema haga mal>
3. <qué se espera que marque como \`[DATO FALTANTE]\`>
EOF

echo "✓ $DIR creado"
echo "  · .inicio      $(cat "$DIR/.inicio")"
echo "  · entrada.md   completá el brief y las hipótesis ANTES de correr"
echo "  · salida/      lo escribe el director durante la corrida"
echo
echo "Siguiente paso: OPERACION.md paso 3 — abrir Claude Code en este repo y pegar el"
echo "prompt del director con ID de corrida = ${NN}-${HOY}-${WNN}"
