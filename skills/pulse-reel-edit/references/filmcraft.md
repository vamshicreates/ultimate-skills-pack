# FilmCraft (ArtCraft) via MCP

FilmCraft is the free, open-source (MIT / Apache-2.0), Premiere-class video editor from the
**ArtCraft** suite (getartcraft.com · github.com/storytold/filmcraft). Its command-line tool
`filmcraft-cli` includes an **MCP server** (`filmcraft-cli mcp`), so any coding agent can drive the editor.

This skill uses that MCP server two ways:

1. **Automatically.** `python pulse.py filmcraft work/timeline.json` speaks MCP to
   `filmcraft-cli mcp` itself and builds the whole edit (tested: ~740 MCP calls, 0 failures, FilmCraft 0.13).
2. **By hand from your agent.** Register the server (below) and the agent can inspect, tweak and export
   the project with the `command_run`, `sequence_inspect` and `render_frame` tools.

## Install FilmCraft

| OS | App | CLI (`filmcraft-cli`, needed for MCP) |
|---|---|---|
| **macOS** | Download the `.dmg` from getartcraft.com/apps/filmcraft or GitHub Releases (`filmcraft-<ver>-macos-universal.dmg`) | The **separate** asset `filmcraft-cli-<ver>-macos-universal.zip`. Unzip it and move `filmcraft-cli` to `/usr/local/bin` (or `~/bin`) |
| **Windows** | `filmcraft-<ver>-windows-x64.msi` (or `-arm64.msi`) | Installed with the MSI at `%LOCALAPPDATA%\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe` (all-users: `C:\Program Files\ArtCraft\FilmCraft\`). Not on PATH |
| **Linux** | `.deb` / `.rpm` | `/usr/bin/filmcraft-cli` |
| From source | `cargo build --release -p filmcraft -p filmcraft-cli` | `target/release/filmcraft-cli` |

macOS first run: the builds are signed and notarised. If Gatekeeper still complains about the CLI, run
`xattr -d com.apple.quarantine /usr/local/bin/filmcraft-cli`.
Windows: if the app opens to a blank window, set `WGPU_BACKEND=vulkan` (or `dx12`).

Check it: `filmcraft-cli --version`, then `python pulse.py doctor` (it finds the CLI in the usual
places, or set `FILMCRAFT_CLI=/full/path/to/filmcraft-cli`).

## Register the MCP server in your agent

Use the full path to the CLI. Two server flavours:
- `filmcraft-cli mcp`: headless (no window). Edits a project in memory; save it with `file.saveAs`.
- `filmcraft-cli mcp --bridge 127.0.0.1:9876`: drives the **running app**. Start the app with
  `filmcraft --control 9876` and set the same `FILMCRAFT_CONTROL_TOKEN` env var for both
  (`python -c "import secrets;print(secrets.token_hex(32))"`).

**Claude Code**
```bash
# macOS / Linux
claude mcp add filmcraft -- /usr/local/bin/filmcraft-cli mcp
# Windows (PowerShell)
claude mcp add filmcraft -- "$env:LOCALAPPDATA\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe" mcp
```

**Codex CLI** (`~/.codex/config.toml`)
```toml
[mcp_servers.filmcraft]
command = "/usr/local/bin/filmcraft-cli"     # Windows: 'C:\Users\<you>\AppData\Local\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe'
args = ["mcp"]
```

**Cursor** (`~/.cursor/mcp.json`), **Gemini CLI** (`~/.gemini/settings.json`), **Windsurf**
(`~/.codeium/windsurf/mcp_config.json`), **Claude Desktop** (`claude_desktop_config.json`), **Antigravity / OpenCode** (their MCP settings):
```json
{ "mcpServers": { "filmcraft": { "command": "/usr/local/bin/filmcraft-cli", "args": ["mcp"] } } }
```
On Windows, write the path with escaped backslashes:
`"C:\\Users\\<you>\\AppData\\Local\\Programs\\ArtCraft\\FilmCraft\\filmcraft-cli.exe"`.

## What `pulse.py filmcraft` builds

`--mode native` (default) builds a fully editable timeline:

| Track | Content |
|---|---|
| V1 | original clips, cut on the beat (`timeline.place` with `sourceIn`/`duration`), speed via `clip.speedDuration` (frame blending) |
| V1 effects | **Lumetri Color** with our look as Input LUT (`lut.import` → `lumetri.setInputLut`) + exposure correction · **Leave Color** (protected colour, keyframed `amount` = colour pop) · **Gaussian Blur** (keyframed `blurriness` = focus pulse) · **Motion** `scale` keyframes = push-ins |
| V1 transitions | Push (`From West`/`From East`), Cross Dissolve, Dip to White (flash 4 f, bleach 18 f) |
| V2 | title plate: transparent PNG sequence with the subject cut-out baked in, so the text sits behind her |
| V3 | adjustment layer + Noise (grain) |
| A1 | the song, trimmed to the music window |
| Markers | every beat, plus a marker at each look section |
| End | Lumetri exposure flicker keyframes + saturation fade to grey |

`--mode baked` puts the engine's styled shots (exactly the `render` look) on V1 instead. Use it when you want
the exact grade and only need to retime or reorder in FilmCraft.

Options: `--bridge 127.0.0.1:9876` builds live in the open app · `--export out.mp4` exports from FilmCraft
· `--project path.fcproj` · `--script-only` (no CLI: writes `filmcraft/filmcraft_plan.json` for an agent to
replay with the MCP tools).

## Useful MCP calls for hand-tweaks

```text
sequence_inspect                                   -> clip ids, sourceIn/Out, effects, keyframes
command_run lumetri.setInputLut {"clip":12,"lut":"lib:lut15"}
command_run effects.setParam {"clip":12,"effect":"gaussian_blur","param":"blurriness","value":30,"time":<ticks>,"keyframe":true}
command_run effects.setParam {"clip":12,"effect":"leave_color","param":"amount","value":100,"time":<ticks>,"keyframe":true}
command_run timeline.move / timeline.razor / sequence.applyVideoTransition {...}
render_frame {"seconds": 4.2}                      -> look at the result
command_run file.exportMedia {"path":"/abs/out.mp4","format":"h264","wait":true}
```
Time is in ticks: **254,016,000,000 per second** (most commands also take `seconds`).
Discover anything else with `command_list` (≈700 commands).
