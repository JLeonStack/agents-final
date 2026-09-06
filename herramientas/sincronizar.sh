#!/usr/bin/env bash
# Copia los contratos de los especialistas desde prompts/agentes/ (fuente de verdad,
# exigida por el enunciado) hacia .claude/agents/ (donde Claude Code los carga).
# Correr SIEMPRE antes de una corrida. La duplicación y su riesgo están declarados
# en DECISIONES.md, entrada del 2026-09-05.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .claude/agents
cp prompts/agentes/*.md .claude/agents/
echo "sincronizados $(ls -1 prompts/agentes/*.md | wc -l | tr -d ' ') contratos → .claude/agents/"
