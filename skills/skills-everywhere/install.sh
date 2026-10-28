#!/usr/bin/env bash
set -euo pipefail

# Install only this project's code and pinned dependency. Existing skills stay local.
release="v0.1.0"
install_root="${SKILLS_EVERYWHERE_ROOT:-${HOME}/.local/share/skills-everywhere}"
python_bin="${PYTHON:-python3}"
if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "Python 3.10 or newer is required. Install Python, then run this command again." >&2
  exit 1
fi
"$python_bin" -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ is required"'
case "$(uname -s)" in
  Darwin|Linux) ;;
  *) echo "This release supports macOS and Linux/WSL." >&2; exit 1 ;;
esac

mkdir -p "$install_root/runtime"
repo_root=""
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  candidate="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -f "$candidate/scripts/skills_everywhere.py" && -f "$candidate/requirements.txt" ]]; then
    repo_root="$candidate"
  fi
fi
if [[ -z "$repo_root" ]]; then
  if ! command -v git >/dev/null 2>&1; then
    echo "Git is required for the remote installer." >&2
    exit 1
  fi
  repo_root="$install_root/runtime/repo-$release"
  if [[ ! -d "$repo_root" ]]; then
    git clone --quiet --depth 1 --branch "$release" -- \
      https://github.com/vamshicreates/skills-everywhere.git "$repo_root"
  fi
fi

"$python_bin" -m venv "$install_root/runtime/venv"
runtime_python="$install_root/runtime/venv/bin/python"
"$runtime_python" -m pip install --disable-pip-version-check --quiet -r "$repo_root/requirements.txt"
mkdir -p "$install_root/runtime/skill/scripts" "$install_root/runtime/skill/agents" "$install_root/inbox"
cp "$repo_root/scripts/skills_everywhere.py" "$install_root/runtime/skill/scripts/skills_everywhere.py"
cp "$repo_root/SKILL.md" "$install_root/runtime/skill/SKILL.md"
cp "$repo_root/agents/openai.yaml" "$install_root/runtime/skill/agents/openai.yaml"
cp "$repo_root/requirements.txt" "$install_root/runtime/skill/requirements.txt"

# Keep a stable launcher path outside the source checkout.
cat > "$install_root/skills-everywhere" <<'LAUNCHER'
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
exec "$root/runtime/venv/bin/python" "$root/runtime/skill/scripts/skills_everywhere.py" --library "$root" "$@"
LAUNCHER
chmod +x "$install_root/skills-everywhere"
"$install_root/skills-everywhere" --source "$install_root/runtime/skill" sync
if [[ "$(uname -s)" == Darwin && "${SKILLS_EVERYWHERE_NO_WATCH:-0}" != 1 ]]; then
  "$install_root/skills-everywhere" watch-install
fi
printf '\nInstalled Skills Everywhere %s\n' "$release"
printf 'Add new skills to: %s/inbox/<skill-name>/SKILL.md\n' "$install_root"
printf 'Inspect: "%s/skills-everywhere" status\n' "$install_root"
printf 'Undo global links: "%s/skills-everywhere" uninstall\n' "$install_root"
if [[ "$(uname -s)" == Linux ]]; then
  printf 'Automatic foreground refresh: "%s/skills-everywhere" watch\n' "$install_root"
fi
