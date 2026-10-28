# Code Visuals for Music

A hybrid agent skill for music videos: **Python for analysis and asset preparation; Chitram + GSAP for animation and previews; FFmpeg for delivery.**

[Read the skill](SKILL.md) · [Engine integration](references/hybrid-engine.md) · [Project data contract](references/project-contract.md)

## What this improves

The workflow requires reference matching, narrative actions, and short motion proofs before scaling to a complete song. It addresses common failures in programmatic music videos: attractive stills with weak animation, sliding character sprites, repetitive movement without story progress, inaccurate lyrics, and full renders performed before the motion treatment is proven.

It includes:

- Portable instructions for reference decoding, song mapping, character motion, and review.
- A shared JSON contract for Python tools and browser animation.
- A Python validator/exporter that emits `window.CVM` and Chitram-compatible `window.MUSIC` timing data.
- A media review helper that extracts an audio-synced clip and a frame strip with FFmpeg.
- Codex skill metadata and a synthetic example project.

This is an agent workflow and integration package. It does not automatically generate finished character acting, verify lyrics, or guarantee production quality. The review helpers are not an artistic scoring system.

## Install

For Codex:

```bash
git clone https://github.com/vamshicreates/code-visuals-for-music.git ~/.codex/skills/code-visuals-for-music
```

Start a new session and invoke `$code-visuals-for-music`. If the destination already exists, inspect it before updating; do not overwrite local modifications.

For Claude Code, clone into `~/.claude/skills/code-visuals-for-music` instead. Other agents can read `SKILL.md` directly.

## Chitram integration

Get the upstream engine separately from [santhoshkota11/chitram-frame1](https://github.com/santhoshkota11/chitram-frame1). Follow [the integration notes](references/hybrid-engine.md) for setup and handoff. Python 3.10+ runs the bundled data helper without additional packages. Rendering requires the external Chitram dependencies, Node.js, Chromium, and FFmpeg. Python audio/asset tools may additionally need NumPy, Pillow, SciPy, or a chosen transcription backend.

Quick data check:

```bash
python3 scripts/project.py check assets/example-project.json
python3 scripts/project.py export assets/example-project.json --out /tmp/music-project.js
```

The example is synthetic timing data, not a film or bundled song. Supply actual media before rendering. Timing validation is separate from media-file validation; use `check --require-media` when production files are ready.

## Attribution

The hybrid approach draws on the Chitram engine's song-time timeline, motion toolkit, scene review, and music-video planning, and on Vamshi Creates' Python media workflow. See [PROVENANCE.md](PROVENANCE.md) for the reviewed upstream revision and links.

Upstream engine code, fonts, libraries, music, and generated artwork are **not redistributed** in this repository. The MIT license applies only to the original contents of this package; upstream dependencies retain their own terms.
