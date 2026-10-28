# Gawx Art Style Editing (`gawx-art-style-editing`)

> Kinetic creative vlog and doodle art editing with frame-by-frame animations, 10fps stop-motion frame drops, and tactile Foley.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Gawx Art Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/gawx-art-style-editing
git clone https://github.com/vamshicreates/gawx-art-style-editing.git ~/.claude/skills/gawx-art-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\gawx-art-style-editing"
git clone https://github.com/vamshicreates/gawx-art-style-editing.git "$HOME\.claude\skills\gawx-art-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/gawx-art-style-editing
git clone https://github.com/vamshicreates/gawx-art-style-editing.git .agents/skills/gawx-art-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\gawx-art-style-editing"
git clone https://github.com/vamshicreates/gawx-art-style-editing.git ".agents\skills\gawx-art-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `gawx-art-style-editing` style."*
