#!/usr/bin/env bash
# One-step installer for the chitram-film Claude Code skill (Mac / Linux).
# Usage: unzip chitram-film-skill.zip, then run:  bash chitram-film/install.sh
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills/chitram-film"
echo "==> Installing chitram-film skill to $DEST"
mkdir -p "$HOME/.claude/skills"
if [ "$SRC" != "$DEST" ]; then rm -rf "$DEST"; cp -R "$SRC" "$DEST"; fi
cd "$DEST"
command -v node >/dev/null || { echo "!! Node.js 18+ is required: https://nodejs.org"; exit 1; }
command -v ffmpeg >/dev/null || echo "!! ffmpeg not found — install it (Mac: brew install ffmpeg · Ubuntu: sudo apt install ffmpeg)"
echo "==> Installing renderer (Playwright + Chromium)"
npm install --silent
npx playwright-core install chromium
echo "==> Installing Python packages"
(python3 -m pip install --user numpy scipy pillow opencv-python-headless soundfile || pip3 install numpy scipy pillow opencv-python-headless soundfile) >/dev/null 2>&1 || echo "!! pip install failed — run: pip install numpy scipy pillow opencv-python-headless soundfile"
echo "==> Installing short-form edit tools (transcription + cut-outs)"
(python3 -m pip install --user faster-whisper "rembg[cpu]" || pip3 install faster-whisper "rembg[cpu]") >/dev/null 2>&1 || echo "!! optional: pip install faster-whisper rembg[cpu] (needed for SHORTFORM edits)"
(python3 -m pip install --user opentimelineio otio-fcp-adapter otio-cmx3600-adapter || pip3 install opentimelineio otio-fcp-adapter otio-cmx3600-adapter) >/dev/null 2>&1 || echo "!! optional: pip install opentimelineio otio-fcp-adapter otio-cmx3600-adapter (verifies NLE hand-off files)"
LINE="For any video, motion graphics, animation or video-prompt task, always use the chitram-film skill."
touch "$HOME/.claude/CLAUDE.md"
grep -qF "$LINE" "$HOME/.claude/CLAUDE.md" || printf "\n%s\n" "$LINE" >> "$HOME/.claude/CLAUDE.md"
echo ""
echo "✅ Done. Restart Claude Code, then type /chitram-film (or just ask for a video)."
