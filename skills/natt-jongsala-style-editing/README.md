# Natt Jongsala Style Editing (`natt-jongsala-style-editing`)

> High-end spatial composite short-form editing with multi-plane rotoscoping, 3D background replacements, and orbiting assets.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Natt Jongsala Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/natt-jongsala-style-editing
git clone https://github.com/vamshicreates/natt-jongsala-style-editing.git ~/.claude/skills/natt-jongsala-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\natt-jongsala-style-editing"
git clone https://github.com/vamshicreates/natt-jongsala-style-editing.git "$HOME\.claude\skills\natt-jongsala-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/natt-jongsala-style-editing
git clone https://github.com/vamshicreates/natt-jongsala-style-editing.git .agents/skills/natt-jongsala-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\natt-jongsala-style-editing"
git clone https://github.com/vamshicreates/natt-jongsala-style-editing.git ".agents\skills\natt-jongsala-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `natt-jongsala-style-editing` style."*
