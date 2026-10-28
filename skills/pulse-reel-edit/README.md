# Pulse Reel Edit (`pulse-reel-edit`)

> Raw clips + a song → a beat-synced vertical reel where the picture **breathes in and out of focus on
> the music**, cuts hide inside the blur, the colour drains to grey while **one colour stays** (the red
> dress), a **white flash** hits the drop, a script **title sits behind the subject**, and the grade goes
> **moody → airy → overcast**.

An Agent Skill that **actually edits**: a cross-platform Python engine (FFmpeg + OpenCV + librosa), a
skill file the agent follows, and an optional bridge that builds the edit inside **FilmCraft**
(the open-source Premiere-class editor from **ArtCraft**) through its **MCP server**, plus LUTs for
**DaVinci Resolve**.

Works with **Claude Code, Codex, Cursor, Gemini CLI, Antigravity, OpenCode, Windsurf, GitHub Copilot**
and any agent that reads `SKILL.md` / `AGENTS.md`. Runs on **macOS, Windows and Linux**.

---

## What it does

| Stage | Command | Output |
|---|---|---|
| Check setup | `python pulse.py doctor` | what's installed and how to fix what isn't |
| Analyse footage + song | `python pulse.py analyze footage/ --song song.mp3` | `analysis.json`, beat map, the drop, **contact sheets** the agent looks at |
| Draft the edit | `python pulse.py plan work/analysis.json --title "Baby"` | `timeline.json` in the reference structure (cuts on beats) |
| Compare looks | `python pulse.py lookbook clip.mov` | one frame through every look |
| Render | `python pulse.py render work/timeline.json [--preview]` | 1080×1920 H.264 with music |
| QA | `python pulse.py qa renders/reel.mp4 --timeline work/timeline.json` | rhythm chart + contact sheets + metrics vs the reference |
| FilmCraft | `python pulse.py filmcraft work/timeline.json` | an editable `.fcproj` built over MCP (effects + keyframes) |
| DaVinci | `python pulse.py render … --grade none --prores` + `python pulse.py luts` | flat ProRes + `.cube` looks |

The style was measured frame by frame from a reference reel. See
[`references/style-reference.md`](references/style-reference.md).

---

## Installation

### 1. Python 3.10+ and Git

- **macOS**: `brew install python git` (or python.org installer). Check: `python3 --version`.
- **Windows**: install Python from python.org (tick **"Add python.exe to PATH"**) and Git for Windows.
  Check in PowerShell: `py --version`.
- **Linux**: `sudo apt install python3 python3-venv git` (or your distro's equivalent).

You do **not** need to install FFmpeg: the `imageio-ffmpeg` package brings a static FFmpeg for every OS.
A system FFmpeg on PATH is used if present.

### 2. Get the skill into your agent's skills folder

Pick the folder your agent reads (you can clone once and symlink it into the others):

| Agent | Personal skills folder |
|---|---|
| Claude Code | `~/.claude/skills/pulse-reel-edit` |
| Codex CLI | `~/.codex/skills/pulse-reel-edit` |
| Cursor, Antigravity, OpenCode, Gemini CLI, Windsurf, Copilot (shared convention) | `~/.agents/skills/pulse-reel-edit` |
| Project-local (any agent) | `<project>/.agents/skills/pulse-reel-edit` or `<project>/.claude/skills/pulse-reel-edit` |

**macOS / Linux**
```bash
git clone https://github.com/vamshicreates/pulse-reel-edit.git ~/.claude/skills/pulse-reel-edit
cd ~/.claude/skills/pulse-reel-edit
./install.sh --link-skills          # venv + packages + model check; links into ~/.agents/skills and ~/.codex/skills too
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/vamshicreates/pulse-reel-edit.git "$HOME\.claude\skills\pulse-reel-edit"
cd "$HOME\.claude\skills\pulse-reel-edit"
powershell -ExecutionPolicy Bypass -File .\install.ps1 -LinkSkills
```

The installer creates `.venv` inside the skill folder, installs `requirements.txt` and
`requirements-titles.txt` (subject cut-out for titles behind the person), and runs `doctor`.
Manual alternative: `python -m pip install -r requirements.txt -r requirements-titles.txt`.

> First title render downloads a 176 MB segmentation model (u2net_human_seg) to `~/.u2net`. One time only.

### 3. FilmCraft (ArtCraft) + its MCP server (to edit inside FilmCraft)

**macOS**
1. Download FilmCraft from <https://getartcraft.com/apps/filmcraft> (or GitHub Releases of
   `storytold/filmcraft`: `filmcraft-<ver>-macos-universal.dmg`) and drag it to Applications.
2. Download the **separate CLI** asset `filmcraft-cli-<ver>-macos-universal.zip` (the `.app` doesn't include
   it), unzip, then:
   ```bash
   sudo mv filmcraft-cli /usr/local/bin/ && filmcraft-cli --version
   ```
3. Register the MCP server with your agent (Claude Code shown):
   ```bash
   claude mcp add filmcraft -- /usr/local/bin/filmcraft-cli mcp
   ```

**Windows**
1. Install `filmcraft-<ver>-windows-x64.msi` (or `-arm64.msi`) from the same page or GitHub Releases.
2. The CLI is installed alongside it (not on PATH):
   `%LOCALAPPDATA%\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe`
3. Register the MCP server:
   ```powershell
   claude mcp add filmcraft -- "$env:LOCALAPPDATA\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe" mcp
   ```
   If the app opens blank, set `WGPU_BACKEND=vulkan` (or `dx12`).

**Other agents** (same server, their config format):
```toml
# Codex  ~/.codex/config.toml
[mcp_servers.filmcraft]
command = "/usr/local/bin/filmcraft-cli"
args = ["mcp"]
```
```json
// Cursor ~/.cursor/mcp.json · Gemini CLI ~/.gemini/settings.json · Windsurf ~/.codeium/windsurf/mcp_config.json · Claude Desktop
{ "mcpServers": { "filmcraft": { "command": "/usr/local/bin/filmcraft-cli", "args": ["mcp"] } } }
```

**Live mode** (watch the timeline build in the open app): start the app with
`filmcraft --control 9876` and an env var `FILMCRAFT_CONTROL_TOKEN` (any random hex), set the same variable
for your terminal, then `python pulse.py filmcraft work/timeline.json --bridge 127.0.0.1:9876`.

`python pulse.py doctor` confirms the CLI is found (or set `FILMCRAFT_CLI=/full/path/to/filmcraft-cli`).
Full reference: [`references/filmcraft.md`](references/filmcraft.md).

### 4. DaVinci Resolve (optional final grade)

Install DaVinci Resolve (free) from blackmagicdesign.com. `python pulse.py luts` writes the looks as
`.cube` files; copy them to Resolve's LUT folder. Steps: [`references/davinci.md`](references/davinci.md).

---

## Use it

Tell your agent:

> *"Use **pulse-reel-edit** to edit the clips in `~/Videos/shoot` with `~/Music/song.mp3` into a 30 second
> reel. Title: **Baby**. Build it in FilmCraft too."*

The agent will: check the setup → analyse and **look at** every clip → draft and refine the timeline on the
beat → preview, QA and iterate → render the final 1080×1920 MP4 → (optionally) build the FilmCraft project
and/or the DaVinci hand-off.

Run it yourself:
```bash
PY=.venv/bin/python      # Windows: .venv\Scripts\python.exe
$PY pulse.py analyze ~/Videos/shoot --song ~/Music/song.mp3 --out work
$PY pulse.py plan work/analysis.json --title "Baby" --duration 30 --render-to work/renders/reel.mp4
$PY pulse.py render work/timeline.json --preview
$PY pulse.py qa work/renders/reel_preview.mp4 --timeline work/timeline.json
$PY pulse.py render work/timeline.json
$PY pulse.py filmcraft work/timeline.json            # optional
```

## Shooting for this style

Shoot at **60 or 120 fps** for the slow motion. Get spins, fabric flares, and fabric sweeping across the lens
(free wipes). Get one calm hero shot with headroom for the title, a landscape/b-roll breather, and keep
one strong wardrobe colour (the colour pop protects one hue: `--protect red|blue|green|…`).

## Repository layout

```
SKILL.md            agent instructions (the skill)
AGENTS.md           pointer for agents that read AGENTS.md
pulse.py            CLI
pulsereel/          engine: media, beats, analyze, plan, looks, fx, render, qa, filmcraft, doctor
references/         style breakdown, timeline schema, FilmCraft MCP, DaVinci
assets/fonts/       Great Vibes (OFL) script font
install.sh / install.ps1, requirements*.txt, tests/, .github/workflows/
```

## License

MIT. Great Vibes font: SIL OFL 1.1. FilmCraft and DaVinci Resolve are separate products by their respective
owners; this skill only talks to them.
