# Skills Everywhere

**Share the skills already on your machine across your coding agents. One installation.**

Skills Everywhere is an Agent Skill with a local installer. It finds `SKILL.md` bundles in your agent folders, builds a shared library, and adds symbolic links where other agents discover global skills. Your existing files stay in place.

```text
Existing skill folders ──▶ Shared local library ──▶ Agent global folders
                              ▲
                    Add future skills to inbox/
```

## Install

Requires **Python 3.10+**, Git, and macOS or Linux/WSL. The installer creates an isolated Python environment with a pinned PyYAML dependency.

```sh
curl -fsSL https://raw.githubusercontent.com/vamshicreates/skills-everywhere/v0.1.0/install.sh | bash
```

To inspect the source first:

```sh
git clone --branch v0.1.0 https://github.com/vamshicreates/skills-everywhere.git
cd skills-everywhere
bash install.sh
```

On macOS, installation also enables a user LaunchAgent that refreshes the library at login and every five minutes. On Linux/WSL, run the foreground watcher when needed. Restart your agent or start a new chat to refresh its discovered skills.

The install root is `~/.local/share/skills-everywhere`. Set `SKILLS_EVERYWHERE_ROOT` to choose another location or `SKILLS_EVERYWHERE_NO_WATCH=1` to skip automatic refresh. Keep the install root and original skill source folders in place.

## Use it as an Agent Skill

Install this repository's root `SKILL.md` with your normal Agent Skills installer, or link the repository into your agent's skill folder. Then ask:

> Use skills-everywhere to share my installed skills across my coding agents.

The skill includes the Python helper, setup instructions, and reversible installation workflow. Installing the skill makes the workflow available; the agent runs the helper when you ask it to share your library.

## Everyday use

```sh
# Preview discovery and changes. This command writes nothing.
~/.local/share/skills-everywhere/skills-everywhere plan

# Refresh now.
~/.local/share/skills-everywhere/skills-everywhere sync

# Check registrations.
~/.local/share/skills-everywhere/skills-everywhere status

# Include an additional trusted skill collection.
~/.local/share/skills-everywhere/skills-everywhere --source ~/my-skills sync

# Share only with selected agents.
~/.local/share/skills-everywhere/skills-everywhere --agents codex,claude,antigravity sync

# Prepare every supported destination, including apps not yet installed.
~/.local/share/skills-everywhere/skills-everywhere --all-agents sync

# Foreground refresh, including on Linux/WSL.
~/.local/share/skills-everywhere/skills-everywhere watch --interval 300

# Remove the login service and the global links created by this tool.
~/.local/share/skills-everywhere/skills-everywhere uninstall
```

Add future skills to `~/.local/share/skills-everywhere/inbox/<skill-name>/SKILL.md`. Sources and destination choices persist in a local config file. A sync rebuilds the shared manifests; bundled supporting files are linked to their original locations.

## Destinations

| ID | Global skill folder |
| --- | --- |
| `agents` | `~/.agents/skills` |
| `codex` | `~/.codex/skills` |
| `claude` | `~/.claude/skills` |
| `cursor` | `~/.cursor/skills` |
| `antigravity` | `~/.gemini/config/skills` |
| `antigravity-legacy` | `~/.gemini/antigravity/skills` |
| `antigravity-cli` | `~/.gemini/antigravity-cli/skills` |
| `gemini` | `~/.gemini/skills` |
| `windsurf` | `~/.codeium/windsurf/skills` |
| `devin` | `~/.config/devin/skills` |
| `opencode` | `~/.config/opencode/skills` |
| `continue` | `~/.continue/skills` |
| `copilot` | `~/.copilot/skills` |

These are local filesystem discovery locations. Registration is tested with isolated homes; it is not a claim of end-to-end invocation testing in every listed app. Supported paths can change with app versions. [See the official references](docs/compatibility.md).

## How conflicts and undo work

- Existing agent files and links win at their current paths.
- Different bundles with the same name receive hash-suffixed variants, available across destinations. Supporting file contents contribute to the fingerprint.
- Invalid YAML, missing metadata, and overlong descriptions are reported and skipped.
- Generated link ownership is recorded in a local journal and state file. Uninstall removes a registration only when its target still matches the recorded link.
- Uninstall preserves the original skills and local library. Delete the library yourself only after you no longer need it.

The default scan covers agent skill folders. Add project collections with `--source`; plugin caches require `--include-plugin-caches`. Discovery reads files and never runs a discovered skill. It never uploads your collection or changes the agent's tool permissions.

## Limits

Sharing instructions does not set up MCP servers, OAuth connections, environment variables, app-specific execution APIs, or required binaries. Local skill folders do not synchronize with remote machines or cloud agent sessions. A skill that depends on a host app may require adaptation before use elsewhere. Native Windows symlink support is outside this release; use WSL.

Only the installer and this skill are published here. Your existing third-party skills retain their own licenses and remain on your machine.

## Development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Tests use temporary home directories and do not touch your actual coding agent configuration.

## Why this exists

I was using several coding agents and had skills spread across their folders. The first local setup brought together 897 skill names and 981 distinct instruction versions, while preserving the originals. That experiment led to this reusable installer. Those figures describe one local inventory, not skills bundled with the project or a compatibility benchmark.

Related tools such as [Vercel's Skills CLI](https://github.com/vercel-labs/skills) install skills from repositories. Skills Everywhere focuses on consolidating and repeatedly sharing an existing local collection.

MIT licensed. Built by [VamshiCreates](https://www.vamshicreates.tech).
