---
name: film-audio-python
description: Analyze a local film throughout its timeline, design a frame-accurate sound cue sheet, and create synchronized sound effects and original music with local Python. Use for film sound design or scoring requests, not for audio transcription alone.
metadata:
  short-description: Sound design and locally generated Python score for film
---

# Film audio with a local Python score

Create a sound plan and usable audio assets for the **specific locked film**. The music must be composed and rendered locally with Python. Do not use Suno, a remote music generator, or an existing song as the score unless the user explicitly changes that requirement. Deliver separately labeled track folders and a detailed scene-by-scene PDF breakdown.

## Establish the picture

- If several films or versions are present, identify the exact target file before detailed analysis. Keep the source untouched and write outputs to a separate directory.
- Read video and audio stream metadata with `ffprobe`. Record frame rate, duration, dimensions, audio layout, and whether timestamps indicate variable frame rate.
- Decode the full video sequentially and inspect the complete timeline for cuts, motion, entrances, gestures, text, and other possible sync events. Use frame differences, scene detection, contact sheets, and focused full-resolution inspection as aids; review the source audio for dialogue, production sound, music, and silence. Automated detection is a lead, not an artistic decision.
- For a request to examine *every frame*, account for every decoded frame or presentation timestamp in the analysis pass. Do not claim to have visually interpreted every frame when only sampled stills were inspected. Use presentation timestamps for variable-frame-rate material.

## Spot the soundtrack

Create a cue sheet with frame or presentation timestamp in/out, visible action, existing sound, proposed layer, exact sonic description, narrative purpose, and priority under dialogue. Include ambience, Foley, designed effects, transitions, music, and intentional silence where appropriate. Put cues at meaningful events and changes, rather than one cue per frame. Separate sounds that should feel physically present in the scene from sounds used for dramatic emphasis. Give every scene a unique ID and short descriptive name; give every cue a unique ID and descriptive music or sound name.

Before generating the full score, settle a coherent palette: tempo or pulse, tonal center, instrumentation, recurring motif, density, and where the music should enter, develop, and stop. Base these decisions on the picture and story. Share the cue sheet or a short style sample when the user has asked to review suggestions first.

## Create audio locally

- **Music:** Express composition as Python note, rhythm, and automation events. Render original waveforms or local instrument/sample transformations with Python. The included [`scripts/render_score.py`](scripts/render_score.py) converts a JSON event score into synchronized stereo WAV stems and a mix. It is a starting point; write film-specific Python when the cue needs richer orchestration or timing. Generate separate cues for long films to keep memory and iteration manageable.
- **Sound effects:** Synthesize designed effects in Python, layer and process source recordings the user owns or has licensed, or record Foley. Build transient, body, tail, motion, and space deliberately. If a realistic sound cannot be made convincingly from the available source material, say which cue needs a recording rather than disguising a synthetic placeholder as finished Foley.
- Keep a manifest of source recordings and generated files. Do not imitate a named song or artist's recording.

The renderer accepts a JSON file with a required cue `name`, `duration`, optional `sample_rate` (default `48000`) and `seed`, and `events` containing `start`, `duration`, `instrument`, optional `pitch`, `gain`, and `pan`. Supported starter instruments are `pad`, `lead`, `bass`, `pluck`, `kick`, `snare`, `hat`, and `noise`. For example:

```json
{
  "name": "MUS001_Opening_Tension",
  "duration": 4,
  "seed": 7,
  "events": [
    {"start": 0, "duration": 3.8, "instrument": "pad", "pitch": "A3", "gain": 0.16},
    {"start": 1.5, "duration": 0.7, "instrument": "pluck", "pitch": "E5", "gain": 0.2},
    {"start": 2, "duration": 0.35, "instrument": "kick", "gain": 0.26}
  ]
}
```

Run `python3 scripts/render_score.py --spec cue.json --out Film_Sound/SC001_Opening/MUS001_Opening_Tension` on macOS or Linux. On Windows, use the Python executable in the virtual environment, for example `& $Python scripts\render_score.py --spec cue.json --out Film_Sound\SC001_Opening\MUS001_Opening_Tension` in PowerShell. Change the composition and timbre for the film; the example is only a format illustration. The renderer writes a named mix and a separate labeled folder for each instrument stem.

The music renderer needs NumPy; the PDF builder needs ReportLab. Both run locally. Install dependencies from [`requirements.txt`](requirements.txt) into a Python 3.11 or newer virtual environment. Check the active Python environment before use. In Codex desktop, `load_workspace_dependencies` provides a bundled Python with both libraries when the default Python lacks one.

## Windows setup and validation

Follow [the Windows setup guide](references/windows_setup.md) on the actual Windows PC. Confirm Python, FFmpeg, and ffprobe are available, install the Python dependencies, and run `scripts/smoke_test.py` with that PC's virtual-environment Python. The test renders a labeled 48 kHz, 24-bit stereo WAV cue, checks its stem folders, builds a PDF that references the delivered audio, and checks both FFmpeg commands. Do not claim Windows compatibility from a run on another operating system; report the Windows test result and any installation changes made.

## Folder and report deliverables

Use this structure, adapting descriptive names to the film:

```text
Film_Name_Sound/
  00_Documents/
    Film_Name_Sound_Breakdown.pdf
    Film_Name_Cue_Sheet.json
  SC001_Opening/
    MUS001_Opening_Tension/
      MUS001_Opening_Tension_mix.wav
      MUS001_Opening_Tension_pad/
        MUS001_Opening_Tension_pad.wav
    FOL001_Gravel_Footsteps/
      FOL001_Gravel_Footsteps.wav
    AMB001_Night_Exterior/
      AMB001_Night_Exterior.wav
  99_Preview/
    Film_Name_Reference_Mix.wav
```

Every cue/track gets its own uniquely labeled folder and matching audio filename. Every music stem also gets its own folder. Keep intermediate scripts/specifications inside the corresponding cue folder, or in `00_Documents`, so files remain traceable. Use stable IDs in both the folder names and the cue sheet.

Write the source of truth as `00_Documents/Film_Name_Cue_Sheet.json`, following [the cue sheet schema](references/cue_sheet_schema.md). For **every scene**, include its frame/time range, visible action, dialogue/production sound, sound direction, and separate entries for music, Foley, ambience, SFX, and deliberate silence. For **every cue**, include its ID, name, frame/time range, sync event, detailed sound description, generation/source method, mix notes, status, and relative asset path. Record an explicit reason when a category is intentionally absent. Generate the PDF from that data using [`scripts/build_breakdown_pdf.py`](scripts/build_breakdown_pdf.py) or an equivalent local PDF workflow; run it with `--assets-root Film_Name_Sound` for final handoff so every listed audio file is checked. Check the rendered pages and extracted text. The PDF must contain the complete scene-by-scene breakdown, including cue names and actual delivered paths, not just a high-level summary.

## Fit and verify

Align assets to picture using frame indices or presentation timestamps, with short fades at boundaries. Keep dialogue intelligible; adjust effects and music around it. Export separate, named stems and a synchronized reference mix, preferably 48 kHz, 24-bit WAV for audio handoff. Check onset timing, missing or duplicate cues, clicks, clipping, folder names, PDF paths, and the opening and final frames by listening and inspecting the rendered output. Report what is complete and any cues still needing recorded source material.
