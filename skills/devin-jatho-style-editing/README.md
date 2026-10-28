# Devin Jatho Style Editing (`devin-jatho-style-editing`)

> Creator-led social content with direct-to-camera hooks, 1.5-2.5s pacing, floating social proof cards, and clean studio grades.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Devin Jatho Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/devin-jatho-style-editing
git clone https://github.com/vamshicreates/devin-jatho-style-editing.git ~/.claude/skills/devin-jatho-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\devin-jatho-style-editing"
git clone https://github.com/vamshicreates/devin-jatho-style-editing.git "$HOME\.claude\skills\devin-jatho-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/devin-jatho-style-editing
git clone https://github.com/vamshicreates/devin-jatho-style-editing.git .agents/skills/devin-jatho-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\devin-jatho-style-editing"
git clone https://github.com/vamshicreates/devin-jatho-style-editing.git ".agents\skills\devin-jatho-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `devin-jatho-style-editing` style."*
