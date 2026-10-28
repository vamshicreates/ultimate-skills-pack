# Discovery and compatibility

The common bundle format is documented in the [Agent Skills specification](https://agentskills.io/specification). A shared format makes instructions reusable; execution also depends on the receiving agent's tools and behavior.

These primary references document supported discovery conventions:

- [Claude Code skills](https://code.claude.com/docs/en/skills): personal skill directories and symlinked folders.
- [Antigravity skills](https://antigravity.google/docs/skills): app and IDE global folders, the legacy IDE folder, and the separate CLI location.
- [OpenCode skills](https://opencode.ai/docs/skills/): native, Claude-compatible, and shared Agent Skills directories.
- [Cursor skills](https://cursor.com/help/customization/skills): local and global discovery.
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/): user skills and shared directory aliases.
- [Devin and Windsurf skills](https://docs.devin.ai/desktop/cascade/skills): global locations and shared discovery.
- [Copilot skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills): personal skills and surface-specific support.
- [Continue source](https://github.com/continuedev/continue): skill discovery depends on the installed Continue surface and version.

The `codex` adapter retains the widely used `~/.codex/skills` folder. The `agents` adapter covers the interoperable `~/.agents/skills` convention. The CLI's `agents` command prints all configured adapters.

The release's automated tests exercise filesystem behavior on macOS and Linux. They do not open or invoke skills in every coding agent. Cloud sessions, remote hosts, tool provisioning, and native Windows require separate setup.
