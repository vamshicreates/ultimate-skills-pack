---
name: model-guide
description: Set up, inspect, or remove global task-aware model recommendations in Codex, or recommend a model for a supplied task.
---

# Model Guide

For setup, explain that this installs persistent instructions in the user's Codex home AGENTS.md. It recommends models; users switch through the model selector. Installing the skill alone does not activate global routing.

Run `python3 scripts/setup.py install` from this skill directory when the user requests global activation. The script preserves existing instructions and backs up changed files. Respect the environment's approval requirements. Use `--dry-run` to preview and `--codex-home PATH` for a custom location. The default honors CODEX_HOME, falling back to ~/.codex.

For status, run `python3 scripts/setup.py status`. To disable global routing, run `python3 scripts/setup.py uninstall`; this removes only this package's marked instruction block. Removing the skill alone does not remove the global rule. Report any AGENTS.override.md that could take precedence.

Existing chats are in scope: read `policy.md` and adopt its recommendations for later actionable instructions in the current chat. For other already-open chats, provide the activation prompt in `activation-prompt.txt`. Don't claim that editing global instructions retroactively injects them into every running chat. Users can paste that prompt into an existing chat to load the rule without starting over.

For a task-specific recommendation, read `policy.md` and apply its decision criteria. Don't execute the supplied task unless requested. Never claim to have changed a model, verified the current model, or measured token savings without evidence.
