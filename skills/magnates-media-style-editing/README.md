# MagnatesMedia Style Editing (`magnates-media-style-editing`)

> Cinematic business documentaries using dramatic pacing, 2.5D parallax photos, rim lighting, and trailer sound design.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **MagnatesMedia Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/magnates-media-style-editing
git clone https://github.com/vamshicreates/magnates-media-style-editing.git ~/.claude/skills/magnates-media-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\magnates-media-style-editing"
git clone https://github.com/vamshicreates/magnates-media-style-editing.git "$HOME\.claude\skills\magnates-media-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/magnates-media-style-editing
git clone https://github.com/vamshicreates/magnates-media-style-editing.git .agents/skills/magnates-media-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\magnates-media-style-editing"
git clone https://github.com/vamshicreates/magnates-media-style-editing.git ".agents\skills\magnates-media-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `magnates-media-style-editing` style."*
