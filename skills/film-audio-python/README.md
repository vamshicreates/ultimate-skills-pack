# Film audio skills

This repository contains two separate Codex skills that work in sequence:

1. [`film-audio-python`](SKILL.md) analyzes a locked film, creates a detailed cue sheet and PDF, and generates labeled local Python music and sound assets.
2. [`film-audio-video-finish`](skills/film-audio-video-finish/SKILL.md) places those assets against the locked picture, mixes and masters them, and exports a final video plus a 48 kHz/24-bit WAV master.

Install both skill folders as siblings under your Codex skills directory. On Windows, follow [the setup guide](references/windows_setup.md). Run each skill's `scripts/smoke_test.py` on the computer that will perform the work before processing a film. The finishing skill uses Python's standard library and FFmpeg; the first skill additionally needs the packages in [`requirements.txt`](requirements.txt).
