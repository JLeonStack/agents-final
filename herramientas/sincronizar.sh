#!/usr/bin/env bash
# Copia la configuración del sistema desde sus rutas visibles hacia .claude/, que es donde
# Claude Code la carga:
#
#   prompts/agentes/*.md   → .claude/agents/*.md      (los cinco contratos registrados)
#   jaula/settings.json    → .claude/settings.json    (la jaula de permisos)
#
# Las fuentes de verdad son las visibles: prompts/agentes/ porque lo exige el enunciado,
# jaula/ porque una regla que solo existe en una carpeta oculta no la puede auditar un
# tercero (DECISIONES.md §16). .claude/ es espejo, no original.
#
# Correr SIEMPRE antes de una corrida. La duplicación y su riesgo —deriva entre copia y
# original— están declarados en DECISIONES.md §7, y los controles D1 y D11 de
# verificar-repo.py comparan las dos copias byte a byte.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p .claude/agents
cp prompts/agentes/*.md .claude/agents/
echo "✓ $(ls -1 prompts/agentes/*.md | wc -l | tr -d ' ') contratos → .claude/agents/"

if cmp -s jaula/settings.json .claude/settings.json 2>/dev/null; then
  echo "✓ jaula/settings.json ya está sincronizada → .claude/settings.json"
elif cp jaula/settings.json .claude/settings.json 2>/dev/null; then
  echo "✓ jaula de permisos → .claude/settings.json"
  echo
  echo "⚠ CAMBIÓ LA CONFIGURACIÓN DE PERMISOS. Claude Code la carga al ABRIR el proyecto:"
  echo "  cerrá y reabrí la sesión antes de correr, o vas a correr con la jaula anterior."
else
  echo "✗ no se pudo escribir .claude/settings.json."
  echo
  echo "  Si estás adentro de una sesión de Claude Code, es lo correcto: la jaula se deniega"
  echo "  a sí misma para que ningún agente pueda ampliarse los permisos (GOBIERNO.md §1)."
  echo "  Copiala desde una terminal normal, fuera de la sesión, y reabrí el proyecto:"
  echo
  echo "      cp jaula/settings.json .claude/settings.json"
  exit 1
fi
