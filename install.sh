#!/usr/bin/env bash
# Ultimate Skills Pack — macOS / Linux / WSL Installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
    exec python "${SCRIPT_DIR}/install.py" "$@"
else
    echo "============================================================"
    echo " Ultimate Skills Pack — Shell Installer"
    echo "============================================================"
    echo "[!] Python 3 is recommended for advanced filtering."
    echo "[*] Falling back to standard POSIX linking..."
    
    DEST_DIR="${HOME}/.claude/skills"
    mkdir -p "${DEST_DIR}"
    
    count=0
    for skill in "${SCRIPT_DIR}/skills"/*; do
        if [ -d "${skill}" ]; then
            name="$(basename "${skill}")"
            ln -sfn "${skill}" "${DEST_DIR}/${name}"
            count=$((count + 1))
        fi
    done
    
    echo "[✓] Successfully linked ${count} skills into ${DEST_DIR}"
fi
