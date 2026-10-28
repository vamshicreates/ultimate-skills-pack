# Johnny Harris Style Editing (`johnny-harris-style-editing`)

> Documentary storytelling that combines presenter footage, cinematic B-roll, 3D relief maps, and wax-pencil analog collage.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Johnny Harris Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/johnny-harris-style-editing
git clone https://github.com/vamshicreates/johnny-harris-style-editing.git ~/.claude/skills/johnny-harris-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\johnny-harris-style-editing"
git clone https://github.com/vamshicreates/johnny-harris-style-editing.git "$HOME\.claude\skills\johnny-harris-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/johnny-harris-style-editing
git clone https://github.com/vamshicreates/johnny-harris-style-editing.git .agents/skills/johnny-harris-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\johnny-harris-style-editing"
git clone https://github.com/vamshicreates/johnny-harris-style-editing.git ".agents\skills\johnny-harris-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `johnny-harris-style-editing` style."*
