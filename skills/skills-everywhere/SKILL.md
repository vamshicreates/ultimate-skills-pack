---
name: skills-everywhere
description: Share existing local Agent Skills across coding agents through one linked library. Use when a user wants to consolidate, globally install, synchronize, inspect, or undo shared skills for Codex, Claude Code, Antigravity, Cursor, OpenCode, Gemini CLI, Devin, Windsurf, Continue, or Copilot.
license: MIT
metadata:
  requirements: Python 3.10+, PyYAML 6.0.3, and macOS or Linux/WSL. Login-based automatic refresh currently requires macOS.
---

# Skills Everywhere

Use `scripts/skills_everywhere.py` relative to this skill's directory. It shares skill files already present on the current machine. It does not install coding agent apps or provision their tools and credentials.

## Plan and install

If `~/.local/share/skills-everywhere/skills-everywhere` exists, prefer that launcher; it uses the installed Python environment. Otherwise run `python3 scripts/skills_everywhere.py --help` to inspect options. If PyYAML is missing, use the repository's `install.sh` or install `requirements.txt` in an isolated Python environment. Paths in the examples are relative to this skill's directory; use absolute paths when the working directory is elsewhere.

- `python3 scripts/skills_everywhere.py plan` inspects existing agent skill folders without writing files.
- `python3 scripts/skills_everywhere.py sync` creates missing links and saves the configuration.
- `--source /trusted/folder` adds an explicitly requested source folder, and can be repeated.
- `--agents codex,claude,antigravity` limits destinations. `--all-agents` prepares all supported global folders, including apps not yet installed.
- `--include-plugin-caches` includes local plugin skill folders when requested. Plugin instructions can depend on tools that another agent does not have.

Global options go before the command. Honor the user's requested sources and destinations. The default destination set includes the shared `.agents` location plus agents whose configuration folders already exist. Project folders, Documents, Downloads, and plugin caches are outside the default scan.

For a request to install or share skills, inspect the plan, then apply within that authorized scope. Report skipped manifests and existing name conflicts. Never execute discovered skill scripts to validate discovery, move source folders, overwrite existing agent skills, or publish a user's skill collection as part of this workflow.

## Keep sharing current

The default library is `~/.local/share/skills-everywhere`. New skills can be placed in `inbox/<name>/SKILL.md` there, or installed in any discovered agent skill folder. `sync` updates generated manifests and linked supporting resources.

- `watch-install` enables a macOS user LaunchAgent at login and every 300 seconds.
- `watch --interval 300` runs foreground refresh on macOS or Linux/WSL.
- `status` checks recorded registrations and missing links.
- `watch-remove` removes the macOS refresh service.
- `uninstall` removes that service and matching global links created by this installer, preserving original skills, user-modified links, and the local library.

Use background refresh when the user asks to keep sharing automatic. Before changing a competing setup, inspect it; a request to install this skill does not authorize removing another service or migrating its state.

Different skill bundles with the same name retain separate hash-suffixed names. Existing agent short names keep their existing behavior. Shared instructions do not guarantee that MCP connections, app-specific APIs, permission settings, binaries, or cloud sessions will work in another agent. Distinguish successful filesystem registration from actual invocation in the destination app.
