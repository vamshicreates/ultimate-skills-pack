---
name: video-to-screenplay-laya
description: Experimental Laya-assisted transcript triage for dialogue-focused film screenplays with song montages, scene locations, and Telugu/Tinglish dialogue. Use when the user asks to test Laya for speed or token savings.
---

# Video to Screenplay_Laya

This is a separate experimental variant of `video-to-screenplay`. Its purpose is to test whether [Laya](https://github.com/NandhaKishorM/laya), a fast text decision model, can reduce review time and generative-model input while preserving every spoken line. Laya reads **text**, not footage or sound. It cannot replace transcription, listening, visual review, speaker identification, or screenplay writing. Do not claim a speed, cost, or quality improvement until a representative comparison shows one.

## Setup on macOS or Windows

Install and use the existing `video-to-screenplay` skill for FFmpeg, Whisper, video preparation, selection, and rendering. Keep Laya optional and isolated from that skill's environment. The base installer provides `uv`; from this skill's directory, create `.venv-laya` and install Laya as follows:

- **Windows 10/11 x64 (PowerShell):** `uv venv --python 3.12 .venv-laya`, then `uv pip install --python .venv-laya\Scripts\python.exe laya`. Verify with `.venv-laya\Scripts\python.exe -I -c "import laya; print(laya.__version__)"`.
- **macOS 14+ on Apple Silicon (Terminal):** `uv venv --python 3.12 .venv-laya`, then `uv pip install --python .venv-laya/bin/python laya`. Verify with `.venv-laya/bin/python -I -c "import laya; print(laya.__version__)"`.
- **macOS 14+ on Intel (Terminal):** `uv venv --python 3.11 .venv-laya`, then `uv pip install --python .venv-laya/bin/python 'numpy<2' 'torch==2.2.2' 'transformers==4.57.6' laya`. Verify with the same macOS command above. These pins follow [Laya's Intel Mac installation guidance](https://github.com/NandhaKishorM/laya#macos-including-intel-macs).

The first real Laya run downloads a checkpoint. Use a short sample before processing a full film. If package installation or model loading fails, use the base workflow and report the cause; do not omit dialogue. This skill's Laya setup is based on upstream platform instructions and has not yet been run on a Windows or Intel Mac machine by this project.

## Workflow

1. Follow `video-to-screenplay` to inspect the complete source, produce timestamped captions/ASR, classify the whole timeline in `selection.json`, and note uncertain intervals. Dialogue inside action or song intervals remains eligible for inclusion. Preserve `song` intervals for visual montage review; Laya's text labels cannot describe a song's imagery.
2. Run `scripts/triage_laya.py` on a timestamped `.srt` to generate short, source-time transcript windows. Start with `--dry-run` to check parsing and timing without downloading Laya. Then run it with Laya to label windows `dialogue`, `lyrics`, or `other_or_unclear`. It emits a JSON record for **every** caption window, always marked `review_required`. It cannot classify silent or uncaptioned stretches; the source timeline review still covers those.
3. Use the labels as a review queue only. Listen to and inspect uncertain or suspected lyric windows, and spot-check apparent dialogue windows. Keep every line of intelligible spoken dialogue even when Laya labels it otherwise. Use audio and video to decide whether a sequence is song, action, title, or credits. For each video song, record its actual locations, visible performers/characters, and distinctive actions. Do not let raw Laya confidence automatically remove any source interval.
4. Complete the base skill's scene ledger, character roster, Fountain screenplay, and illustrated PDF. Give dialogue scenes and each song location a supported `INT./EXT. LOCATION - DAY/NIGHT` heading; use `TIME UNKNOWN` when needed. Describe songs as concise visual montages without lyrics. Put a matching `Tinglish: ...` line immediately under every Telugu dialogue line in the same spoken turn, keeping it a transliteration rather than an English translation. Use `kind: "song"` for song scene spans in the illustrated renderer so the left-side screenshot comes from the song. For audio-only material, do not invent locations or visual montage beats. Retain the SRT, Laya JSON, source-time selection, and any corrected labels as audit material. For a full film, process ordered 15–30 minute batches and merge the ledger.

Example from this skill's directory on macOS:

```bash
.venv-laya/bin/python scripts/triage_laya.py captions.srt --output triage.json --dry-run
.venv-laya/bin/python scripts/triage_laya.py captions.srt --output triage.json --model multilingual
```

On Windows PowerShell, use:

```powershell
.\.venv-laya\Scripts\python.exe scripts\triage_laya.py captions.srt --output triage.json --dry-run
.\.venv-laya\Scripts\python.exe scripts\triage_laya.py captions.srt --output triage.json --model multilingual
```

Use `--model multilingual` for Telugu or mixed-language films. The script's labels come from text alone and are not scene descriptions.

## Decide whether Laya helped

Before using its labels to reduce normal review, hand-label a representative set of dialogue, song, action-with-dialogue, and uncertain windows. Compare the Laya variant with the base workflow on the **same** source: elapsed time, generative input tokens, retained-dialogue recall, speaker/name errors, and screenplay corrections. Count Laya setup, model download, and inference time separately from repeat-run time. If any dialogue would be lost or quality worsens, keep the base review. Report savings only from measured runs, including the sample size and hardware.
