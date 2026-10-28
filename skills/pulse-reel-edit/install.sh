#!/usr/bin/env bash
# pulse-reel-edit installer for macOS / Linux.
#   ./install.sh                 create .venv, install packages, run doctor
#   ./install.sh --link-skills   also link this folder into ~/.claude/skills, ~/.agents/skills, ~/.codex/skills
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Python 3.10+ not found. macOS: brew install python  |  Linux: sudo apt install python3 python3-venv"; exit 1
fi
echo "Using $($PY --version) ($PY)"

if [ ! -x .venv/bin/python ]; then "$PY" -m venv .venv; fi
VPY="$HERE/.venv/bin/python"
"$VPY" -m pip install -q --upgrade pip
"$VPY" -m pip install -q -r requirements.txt
if ! "$VPY" -m pip install -q -r requirements-titles.txt; then
  echo "NOTE: rembg (titles behind the subject) did not install. Everything else works; titles will sit in front."
fi

if [ "${1:-}" = "--link-skills" ]; then
  for d in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills"; do
    mkdir -p "$d"
    tgt="$d/pulse-reel-edit"
    if [ "$(cd "$d" && pwd)/pulse-reel-edit" = "$HERE" ]; then continue; fi
    if [ -e "$tgt" ] || [ -L "$tgt" ]; then echo "  exists: $tgt"; else ln -s "$HERE" "$tgt" && echo "  linked: $tgt"; fi
  done
fi

"$VPY" pulse.py doctor || true
echo
echo "Done. Python for this skill: $VPY"
echo "FilmCraft (optional): see README > FilmCraft, then: claude mcp add filmcraft -- /usr/local/bin/filmcraft-cli mcp"
