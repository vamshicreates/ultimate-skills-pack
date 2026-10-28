---
name: pulse-reel-edit
description: Edit raw footage and a song into a beat-synced vertical reel in the "focus pulse + colour pop" style. The picture blurs and re-focuses on the beat with cuts hidden in the blur, the colour drains to grey while one colour (e.g. a red dress) stays, a white flash marks the drop, a script title sits behind the subject, and the grade moves moody → airy → overcast. Use when the user shares footage and asks for this edit or a dreamy fashion/dance/pre-wedding reel, or names pulse-reel-edit. Renders with Python + FFmpeg on macOS/Windows/Linux, can build the edit natively in FilmCraft (ArtCraft) through its MCP server, and hands off LUTs to DaVinci Resolve.
compatibility: Python 3.10+, macOS / Windows / Linux. FFmpeg comes with the imageio-ffmpeg wheel. Optional FilmCraft CLI (MCP) and DaVinci Resolve.
---

# pulse-reel-edit

Turn a folder of raw clips and a song into a finished 9:16 reel in this style. The reference
breakdown is in `references/style-reference.md`.
**The picture breathes in and out of focus on the music, colour drains and floods back while the
protected colour (the red dress) stays, and nearly every cut is hidden inside a blur peak.**

Everything runs through one CLI. Below, `PY` means the skill's Python: `<skill>/.venv/bin/python` on macOS/Linux,
`<skill>\.venv\Scripts\python.exe` on Windows, else `python3` / `python`. `<skill>` is this folder.

```
PY <skill>/pulse.py doctor | analyze | plan | lookbook | render | qa | luts | filmcraft
```

## 0. Check the setup (once per machine)

Run `PY <skill>/pulse.py doctor`. If anything shows `[!!]`, run the installer (`install.sh` on macOS/Linux,
`install.ps1` on Windows) or `PY -m pip install -r <skill>/requirements.txt`. `[--]` items are optional
(FilmCraft, rembg). The first title render downloads a 176 MB person-segmentation model once.

## 1. Gather the inputs

Defaults first, then ask only for what can't be defaulted:
- **Footage folder** (required) and **song** (required: the edit is timed to it; any audio file in the
  folder is used if `--song` isn't given).
- **Title word(s)** for the hero shot (reference: "Baby"). Optional.
- **Length**: 30 s default. **Protected colour**: the dominant wardrobe colour (red default; `--protect blue|green|…`).
- **Where it ends up**: a finished MP4 (default) · FilmCraft project (`filmcraft`) · DaVinci grade (`--grade none --prores` + `luts`).

Work in a project folder next to the footage (e.g. `<footage>/../pulse_work`). Keep every output there.

## 2. Analyse, then LOOK at the footage

```
PY pulse.py analyze <footage_dir> --song <song> --out <work> --duration 30 --protect red
```
This writes `<work>/analysis.json` (probe, fps, per-0.25 s sharpness/motion/colour/headroom, best windows,
beats, drop) and `<work>/sheets/Cxx.jpg` contact sheets with timestamps.
**Open every contact sheet.** Note per clip:
- spins / fabric flares (motion shots), calm poses, close-ups, wides, b-roll;
- **in-camera transition moments**: fabric sweeping across the lens, whip pans. These are free wipes.
  Cut on them.
- the **hero shot**: calm, sharp, clean headroom above the subject (for the title);
- unusable bits (focus hunting, people walking through, shaky starts).

## 3. Plan: auto-draft, then refine like an editor

```
PY pulse.py plan <work>/analysis.json --title "Baby" --duration 30 --render-to <work>/renders/reel.mp4
```
This writes `<work>/timeline.json` (schema: `references/timeline-schema.md`) following the reference
structure. The draft picks windows by score only, so **refine it** by editing the JSON:

| Rule | Why |
|---|---|
| Keep every cut on a beat (`dur` values come from the beat grid; if you change one, change the next by the opposite amount) | cuts on the beat are the rhythm |
| Shots 2–4 beats; hero/title shot ~5 beats; final shot ~6 beats | reference average 1.2 s |
| Set each shot's `in` to the **peak moment** you saw on the sheets (spin apex, fabric whip, smile) | the score can't see story |
| Put the hero shot (calm, headroom) with the title at ~10–15 % of the reel | "Baby" lands at 3.6 s in the reference |
| A b-roll breather just before the drop | river shot at 5.7 s |
| Drop at ~31 %: `transition: "flash"`, colour `bw_in`, look section switches to `airy` | the reel's turning point |
| Use in-camera wipes: cut out of a shot where the fabric covers the lens | reference 2.0 s, 13.3 s |
| Alternate wide / close and front / back; don't put the same clip in two neighbouring shots | variety |
| Colour pop sparingly: `bw_in`/`pulse` at the start, `pop_flood`/`pop_out` around spins, mostly `full` after the drop | |
| 60 fps+ clips: `speed` 0.5 with `ramp_out` 0.15–0.2 on motion shots. 30 fps clips: speed 1.0 | smooth slow motion needs frames |
| Close-up push-in: `zoom: [1.0, 1.35–1.45]`; others `[1.0, 1.04–1.08]` | |

Choose looks per section with `PY pulse.py lookbook <clip> --out <work>/lookbook_<clip>.jpg` and **look at it**.
Use `moody,airy,overcast` when the footage has the range (dark start, bright/backlit middle); use
`--looks natural` for a single clean look; mix per shot with `"look"`.

## 4. Preview render, QA, iterate

```
PY pulse.py render <work>/timeline.json --preview
PY pulse.py qa <work>/renders/reel_preview.mp4 --timeline <work>/timeline.json
```
Open `rhythm.png` and every `sheet_XX.jpg` in the `_qa` folder. Pass criteria (reference targets):
- `cuts_on_beat_pct` ≥ 80 and `cuts_in_blur_peak_pct` ≥ 75; blur peaks 5–12 per 10 s; avg shot 0.8–1.6 s;
- the drop flash and the colour switch happen together; the red stays red (not orange/pink) in every look;
- the title is readable, sits **behind** the subject's head, and isn't cut off; no black/frozen frames;
- skin isn't green or grey; no clipped faces in the airy look (lower that shot's `exposure`).
Fix the timeline and re-render the preview. Two or three rounds is normal.

## 5. Final render

```
PY pulse.py render <work>/timeline.json            # 1080x1920, H.264 CRF 16, music with fade-out
```
Run `qa` on the final too and look at the sheets once more. Deliver the MP4 path, the length, the song
window used, and one line on the choices (looks, title, drop time).

## 6. Optional: build it in FilmCraft (ArtCraft) via MCP

```
PY pulse.py filmcraft <work>/timeline.json                    # native: editable effects + keyframes
PY pulse.py filmcraft <work>/timeline.json --mode baked       # exact engine look, shots on V1
PY pulse.py filmcraft <work>/timeline.json --bridge 127.0.0.1:9876   # build live in the open app
```
This needs `filmcraft-cli` (doctor finds it; or set `FILMCRAFT_CLI`). It writes `<work>/reel.fcproj` and check
frames in `<work>/filmcraft/check/`. **Look at them.** Native mode maps the style onto FilmCraft's own
Lumetri (our LUT), Leave Color, Gaussian Blur and Motion keyframes, Push / Dip to White transitions, a title
plate on V2 and grain on V3. If your agent has the FilmCraft MCP server registered, you can
inspect and tweak the result directly (`sequence_inspect`, `command_run`, `render_frame`).
Details and per-agent MCP registration: `references/filmcraft.md`.

## 7. Optional: grade in DaVinci Resolve

Only after the edit is final: `render --grade none --prores` plus `luts`, then follow `references/davinci.md`
(or drive Resolve through its MCP/scripting connection if one is available).

## Troubleshooting

- **iPhone HDR / Dolby Vision clips look washed out**: the decoder tone-maps HLG/PQ automatically. If
  ffmpeg lacks `zscale`, export SDR from Photos or convert first.
- **Title in front of the subject**: rembg isn't installed (`doctor`), or the mask missed. Raise `pos` y so the
  title overlaps the head less, or set `behind_subject: false`.
- **Slow**: use `--preview` while iterating. Titles behind the subject cost ~0.3–0.6 s per frame on CPU.
- **Wrong drop / music window**: set `music.start` and move the `flash` shot and the section times by hand,
  or re-plan with `--music-start <sec>`.
- **Clip too short for a slot**: shorten `dur` (keep beats) or set `speed` closer to 1.
