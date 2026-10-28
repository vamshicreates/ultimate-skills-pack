# AGENTS.md

This repository is an Agent Skill: **pulse-reel-edit**. Any coding agent (Claude Code, Codex, Cursor,
Gemini CLI, Antigravity, OpenCode, Windsurf, Copilot…) should follow **[SKILL.md](SKILL.md)** when the user
asks to edit footage into a reel in this style.

- Entry point: `python pulse.py` (subcommands: doctor, analyze, plan, lookbook, render, qa, luts, filmcraft).
- Use the repo's virtualenv if present: `.venv/bin/python` (macOS/Linux) or `.venv\Scripts\python.exe` (Windows).
- Always **look at** the contact sheets and QA images the tools write before deciding anything.
- FilmCraft (ArtCraft) MCP setup: [references/filmcraft.md](references/filmcraft.md). DaVinci: [references/davinci.md](references/davinci.md).
