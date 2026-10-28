# Vox Style Editing (`vox-style-editing`)

> Explainer editing with animated maps, clean infographics, archival footage, yellow highlighters, and clear visual storytelling.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Vox Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/vox-style-editing
git clone https://github.com/vamshicreates/vox-style-editing.git ~/.claude/skills/vox-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\vox-style-editing"
git clone https://github.com/vamshicreates/vox-style-editing.git "$HOME\.claude\skills\vox-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/vox-style-editing
git clone https://github.com/vamshicreates/vox-style-editing.git .agents/skills/vox-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\vox-style-editing"
git clone https://github.com/vamshicreates/vox-style-editing.git ".agents\skills\vox-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `vox-style-editing` style."*
