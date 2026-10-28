#!/usr/bin/env bash
set -euo pipefail

skill_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_root="${CODEX_HOME:-$HOME/.codex}"
skill_dest="$codex_root/skills/film-cast-actor-database"

if [[ "${1:-}" != "" && "${1:-}" != "--force" ]]; then
  echo "Usage: ./install.sh [--force]" >&2
  exit 2
fi

if [[ -e "$skill_dest" || -L "$skill_dest" ]]; then
  if [[ "${1:-}" != "--force" ]]; then
    echo "Already installed at $skill_dest. Run ./install.sh --force to replace it." >&2
    exit 1
  fi
  rm -rf -- "$skill_dest"
fi

mkdir -p -- "$skill_dest"
cp -- "$skill_root/SKILL.md" "$skill_dest/"
cp -R -- "$skill_root/agents" "$skill_root/references" "$skill_root/templates" "$skill_dest/"
echo "Installed film-cast-actor-database at $skill_dest"
echo "Start a new Codex turn, then call \$film-cast-actor-database."
