---
name: local-podcast-clips
description: Find and edit short clips from a podcast using local transcription and FFmpeg, including Telugu speech and captions. Use when the user wants a no-credit local workflow rather than OpusClip's hosted processing.
---

# Local podcast clips

Create truthful, watchable clips from user-provided podcast footage without paid video APIs. Default to preserving Telugu speech and Telugu-script captions when the source is Telugu. Never translate, dub, or transliterate unless requested.

## Workflow

1. Inspect the source with `ffprobe` and a visual/audio sample. Keep the original media unchanged. Ask which episode to use only when source identity is genuinely ambiguous.
2. Check local dependencies with `python3 scripts/check_env.py`. If setup is needed on this machine, use [setup](references/setup.md). Do not install packages or download a model silently when the user has only asked for a plan.
3. Transcribe the full relevant source with `scripts/transcribe.py`, setting `--language te` for Telugu. Use a multilingual model; `.en` models cannot transcribe Telugu. The script writes JSON timestamps and an SRT. Review Telugu names, dialect, code-switching, and technical terms against the audio. Transcription is a draft, not verified dialogue.
4. Read the full relevant transcript and inspect promising moments in the actual video. Choose excerpts with a clear opening, enough context, and a payoff; preserve speaker meaning. Give the user timecoded clip choices when the editorial direction is open. Their request to edit a particular moment is sufficient to proceed directly.
5. Render selected excerpts with `scripts/render_clip.py`. It cuts, reframes, exports an MP4, and creates a clip-relative SRT. Burn captions only when requested or needed for delivery. A centered 9:16 crop is a starting point; inspect the full clip and adjust the crop position when a speaker is cut off. For multiple camera angles or noncontiguous cuts, make a deliberate edit plan and use appropriate local tools rather than pretending the helper handles them.
6. Watch the exported clip from start to finish. Correct transcript and caption errors, check lip sync and Telugu glyph shaping, audio cuts, face framing, context, and export duration. Re-render after corrections. Report any checks the current machine could not perform.

Use the existing OpusClip Video Tools Remotion templates only when motion graphics would help and the template source is available. They are optional; this skill works independently of the OpusClip clones, account, and hosted MCP/API.

## Commands

Run these from the skill folder, using absolute paths for media when practical:

```sh
python3 scripts/check_env.py
python3 scripts/transcribe.py /path/to/episode.mp4 --language te --model medium --output /path/to/work/transcript
python3 scripts/render_clip.py /path/to/episode.mp4 --transcript /path/to/work/transcript.json --start 00:12:34 --end 00:13:25 --output /path/to/work/clip.mp4 --aspect 9:16
```

`render_clip.py` creates `clip.srt` beside the MP4. Add `--burn-subtitles` only after confirming a Telugu-capable font is installed. See [setup](references/setup.md) for dependency and caption details.
On Windows, invoke the scripts with `.\.venv\Scripts\python.exe` and use Windows file paths as shown in the setup guide.

## Limits

- Local transcription and rendering avoid per-call API charges, but use disk space and compute. The first model run downloads model weights.
- Automatic highlight ranking, face tracking, speaker diarization, social publishing, and OpusClip's proprietary effects are not provided by these scripts. Use editorial review and other authorized local tools if those are needed.
- Do not upload podcast footage or transcripts to a hosted service without the user's authorization.
