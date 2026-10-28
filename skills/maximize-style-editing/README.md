# Maximize Style Editing (`maximize-style-editing`)

> Hyper-retention viral short-form editing with punchy animated subtitles, dynamic zoom-whips, emojis, and continuous riser audio.

A production-grade Agent Skill compatible with **Claude Code, Antigravity, Cursor, Windsurf, OpenCode, Codex**, and video editing workflows (Premiere Pro, After Effects, DaVinci Resolve, Remotion, FFmpeg).

---

## What This Skill Does

This skill equips AI coding agents with the exact visual grammar, cut frequency, motion physics, color palettes, typography specifications, and audio engineering rules to recreate the signature **Maximize Style Editing** aesthetic.

See [`SKILL.md`](SKILL.md) for the full technical breakdown, expressions, and execution recipes.

---

## Installation

### Method A: Install in Claude Code (`~/.claude/skills`)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/maximize-style-editing
git clone https://github.com/vamshicreates/maximize-style-editing.git ~/.claude/skills/maximize-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\maximize-style-editing"
git clone https://github.com/vamshicreates/maximize-style-editing.git "$HOME\.claude\skills\maximize-style-editing"
```

### Method B: Install in Cursor / Antigravity / Agent Workspace (`.agents/skills`)

**macOS / Linux:**
```bash
mkdir -p .agents/skills/maximize-style-editing
git clone https://github.com/vamshicreates/maximize-style-editing.git .agents/skills/maximize-style-editing
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills\maximize-style-editing"
git clone https://github.com/vamshicreates/maximize-style-editing.git ".agents\skills\maximize-style-editing"
```

---

## Usage in Coding Agents

Once installed, invoke the skill directly in any agent prompt:
> *"Edit this script and video footage using the `maximize-style-editing` style."*
