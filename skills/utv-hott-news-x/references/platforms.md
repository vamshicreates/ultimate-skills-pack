# Platform installation and browser requirements

The skill is portable because its publishing contract uses the visible X interface and the host agent's native browser or computer-use capability.

| Agent | Suggested skill location | Publishing requirement |
| --- | --- | --- |
| Codex | `~/.codex/skills/utv-hott-news-x/` | Browser/computer-use access to a user-visible X session |
| Claude Code | `<project>/.claude/skills/utv-hott-news-x/` or `~/.claude/skills/utv-hott-news-x/` | A browser-control or computer-use tool available to Claude |
| Gemini / Antigravity | `<project>/.agents/skills/utv-hott-news-x/` or `~/.gemini/config/skills/utv-hott-news-x/` | Antigravity browser control or an equivalent computer-use tool |
| ChatGPT | Upload the skill folder or ZIP where custom skills are supported | ChatGPT computer-use or browser-control access |

Windows user-level paths begin under `%USERPROFILE%`; macOS paths begin under the user's home folder. Project-local skill folders work on both operating systems.

## Requirements

- A browser the agent is allowed to control.
- An X account that the user signs into manually.
- Python 3.9 or newer only when using `scripts/validate_posts.py`.

The drafting workflow still works when a host does not provide browser control. In that case, return the completed post or thread and clearly state that publishing requires an agent environment with computer use.

Do not copy browser profiles, share login-state files between agents, or include credentials in this skill. Each environment should use its own authenticated browser session.
