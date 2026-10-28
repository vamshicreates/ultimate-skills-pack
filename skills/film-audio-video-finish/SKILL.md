---
name: film-audio-video-finish
description: Assemble, mix, master, and render a locked film with the separate music, Foley, ambience, and effects created by film-audio-python. Use when the user wants a finished video with its soundtrack, not merely audio cue generation.
metadata:
  short-description: Mix film audio and render the finished video
---

# Finish a film with its generated soundtrack

Use the locked picture and the audio package from `$film-audio-python` to deliver a synchronized final video and a separate mastered WAV. If the package is missing, use that skill first to create its cue sheet and labeled music, Foley, ambience, and SFX folders. This skill handles the final assembly and mix; keep both skills installed as separate folders.

## Prepare the edit

- Identify the exact picture master and the matching audio package. Compare title, version, frame rate, duration, and opening/end frames with the cue sheet. Do not assemble against a different cut without re-spotting cue timings.
- Read `00_Documents/Film_Name_Cue_Sheet.json` and validate each delivered asset. The cue sheet's readable time fields need exact positions before rendering. Create a machine-readable [mix plan](references/mix_plan.md) with each cue's asset path and `start_seconds` on the locked picture timeline. Resolve ambiguous timecodes against the actual frame rate or presentation timestamps; do not guess.
- Decide how to treat the source video's audio. Keep production dialogue and useful location sound unless the user has supplied replacement stems or it is clear that source audio must be replaced. If the source audio already contains music that cannot be isolated, flag the overlap and make an explicit mix decision. Preserve sync.

## Mix and master

- Place music, Foley, ambience, and SFX on their own logical buses. Use the labeled **music mix** once per cue; do not also sum its instrument stems. The stems are for revisions to that cue.
- Adjust cue levels and entry/exit fades for the picture. Protect intelligible dialogue; shape masking music by automation or EQ when needed. Preserve transients and room continuity. Listen through transitions, silences, first and last frames, and any high-energy section. Fix clicks, clipping, timing errors, and overly abrupt ambience changes.
- The included [`scripts/finish_film.py`](scripts/finish_film.py) is a deterministic starting renderer. It assembles the plan with FFmpeg, retains production audio when specified, renders a floating-point premix, applies measured loudness normalization with a true-peak ceiling, writes 48 kHz stereo 24-bit WAV, and muxes the locked video stream with AAC audio. It copies video without changing its frames. For edits needing more involved automation, revise the mix plan or perform a controlled DAW/FFmpeg pass, then run the same checks.
- Pick the loudness target for the delivery. The example plan uses `-16 LUFS`, `-1.5 dBTP` for a web preview; do not treat that as a theatrical or broadcast standard. Keep a lossless mastered WAV for handoff.

## Render and check

Run [`scripts/smoke_test.py`](scripts/smoke_test.py) once on the target computer to verify FFmpeg and the final-render path. Then run `python scripts/finish_film.py --plan mix_plan.json` with Python 3.11+ and FFmpeg/ffprobe on PATH. On Windows, use the virtual-environment Python executable in PowerShell. Run `--validate-only` first when adapting an existing audio package. Use a fresh output directory or `--overwrite` for an intentional revision. The script writes a mastered WAV, a final MP4 or MOV, the mix plan, and a render report beside them.

Check that the final file plays from beginning to end, retains the picture's aspect ratio, frame rate, color metadata, and frame count where available, and has one synchronized soundtrack. Compare input/output durations and inspect the final frame. Measure delivered loudness and true peak, listen to the encoded final video as well as the WAV, and check at least each scene boundary and dialogue entrance. Keep the cue sheet, mix plan, master WAV, final video, and render report together. State any remaining audio sources or picture changes that prevent a finished mix.
