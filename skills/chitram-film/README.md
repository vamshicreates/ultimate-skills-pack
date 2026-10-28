# chitram-film

A Claude Code skill that works as a motion studio, editor, sound designer and music-video maker.
It writes a timecoded Production Prompt, builds the film as HTML/CSS/GSAP and renders it
frame-accurately to MP4.

## What it does

- **Motion films**: promos, ads, explainers, reels, kinetic type, logo stings (`ENGINE.md`, `DIRECTOR.md`, `EXAMPLES.md`)
- **Short-form edits** of real footage: natural cuts, captions, cut-outs, B-roll (`SHORTFORM.md`)
- **Long-form YouTube**: script assembly, A/B/C multi-cam, screencasts, briefs, Resolve/Premiere hand-off (`LONGFORM.md`, `CONNECTORS.md`)
- **Music videos / lyric videos / beat edits**: song analysis, storyboard, chorus escalation, animation catalogue (`MUSICVIDEO.md`)
- **Sound and music from the internet**: trend research, licence-checked SFX kits and music search, beat grid, fit-to-length, cinematic SFX stacks, −14 LUFS mix (`SOUND.md`, `MUSIC.md`). The skill ships no audio files.
- **Effects**: speed ramps, beat punches, shake, flash, grain, grades, zoom-in, wiggle, wipes, 3D flip/zoom/xyz, splatter, tear, depth of field, pop-up, shine, light sweep, particles, handheld (`engine/fx-kit.js`)

## Install

Copy this folder to `~/.claude/skills/chitram-film`, then run `install.bat` (Windows) or `install.sh`.
Needs Node.js, Python 3, and ffmpeg.

Start with `SKILL.md`.
