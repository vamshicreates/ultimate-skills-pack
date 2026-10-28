---
name: film-audio-reaper-mix
description: Import a locked film and its generated music, Foley, ambience, and SFX into REAPER, mix against picture, and deliver a verified final audio master. Use when the user wants REAPER to finish an existing film audio package.
metadata:
  short-description: Mix film audio in REAPER and export the master
---

# Finish generated film audio in REAPER

Use the locked picture, the labeled audio package from `$film-audio-python`, and an exact mix plan to build a REAPER session, mix it against picture, and deliver a synchronized WAV master. The source package's scene-by-scene PDF remains the sound breakdown; copy it into the session. If the user also wants a final video, mux this approved WAV with the locked picture and verify the resulting video's sync and picture stream.

## Inputs and preparation

- Confirm the exact picture version and audio package. The mix plan uses seconds from the first presented video frame; resolve cue times against the actual frame rate or timestamps before import. If only the first skill's cue sheet exists, create this exact mix plan from it and verify each entry against picture. Read [the mix plan schema](../film-audio-video-finish/references/mix_plan.md) when that skill is installed. The required fields are `title`, `video`, `audio_package`, `output_dir`, `source_audio`, and `cues` with `id`, `asset`, and `start_seconds`.
- Check whether the picture's existing audio contains dialogue, useful location sound, or baked-in music before choosing `source_audio.mode`. Keep each cue's named mix WAV once. Instrument stems are available for revisions, but never sum a cue mix and its constituent stems together.
- Use Python 3.11+ and FFmpeg/ffprobe on the same computer that runs REAPER. Run `python scripts/prepare_session.py --plan path/to/mix_plan.json` (or `py -3 scripts\prepare_session.py --plan path\to\mix_plan.json` on Windows). This validates the picture and cue files, copies named audio assets into a portable session Media tree, extracts the selected production audio when `source_audio.mode` is `keep`, and writes `00_Documents/Import_To_REAPER.lua`. `--copy-video` also copies the picture when a fully portable session is needed; otherwise keep the original picture path available. The command refuses to overwrite a session.
- Preserve the package's PDF and JSON cue sheet alongside the plan in `00_Documents`. Missing or ambiguous timing must be resolved before building the session.

## Build and mix in REAPER

- Open a **new empty project** in REAPER. Open Actions → Show action list → New action → Load ReaScript, select `Import_To_REAPER.lua`, and run it. The script refuses a nonempty project or an existing destination project. It creates a picture reference item with its audio level at zero, a production track when retained, and one labeled child track per cue under music, Foley, ambience, and SFX buses. It sets cue positions, source offsets, lengths, gains, fades, a full-film region, and saves the `.RPP` project.
- Open View → Video to inspect sync. If picture does not display or production sound is absent, fix that before mixing; never silently proceed with a missing source. Check early, middle, and late sync events and every scene boundary against the PDF/cue sheet.
- Listen through the full film. Balance production dialogue and location sound first, then ambience, Foley/SFX, then music. Adjust clip gains, bus faders, pan, EQ, compression, and automation in REAPER where the picture calls for them. Preserve intelligible speech, transients, room continuity, and deliberate silences. Use short crossfades at joins and check the first and last audible samples. Avoid clipping on tracks, buses, and master. Save the project after substantive changes.
- Choose the delivery loudness and true-peak ceiling from the actual destination. The mix plan's `mastering` values may be a web-preview target; do not apply them blindly to cinema or broadcast. Use REAPER's Render dialog and render statistics to measure the result, adjust gain/limiting as needed, and listen again. Keep processing transparent unless the film requires an audible effect.

## Render and deliver

- In File → Render, choose **Master mix**, bounds **entire project** or the `FULL_FILM` region, sample rate **48,000 Hz**, **stereo WAV, 24-bit PCM**, and a named file in `02_Renders`, such as `Film_Name_Final_Mix_48k24.wav`. Set exact start at picture zero and end at the picture duration; do not include a render tail beyond the locked picture unless the user explicitly wants one. Render the entire film.
- Run `python scripts/verify_master.py --plan path/to/mix_plan.json --master path/to/Film_Name_Final_Mix_48k24.wav --report path/to/02_Renders/Film_Name_Master_Report.json`. Inspect the measured integrated loudness and true peak against the chosen delivery target. Listen to the rendered WAV from start to finish, including quiet passages and every transition; correct and rerender if needed.
- Deliver the WAV, `.RPP` project, copied cue assets, original mix plan, PDF/cue sheet, and verification report in the labeled session folders. Report any unresolved sync, source-audio, or delivery-target decision. Do not claim the REAPER mix is finished from a generated session alone.

## Windows notes

REAPER bundles Lua ReaScript, so the import script does not need a Lua installation. Python and FFmpeg are needed for preparation and verification. Run the preparer on the Windows PC after copying the source video and audio package there; paths embedded in the generated script are local to that PC. Check `py -3 --version`, `ffmpeg -version`, and `ffprobe -version`, then run `py -3 scripts\smoke_test.py`. For an in-app test, run the same command with `--keep path\to\new\disposable-folder`, open its printed `Import_To_REAPER.lua` in REAPER, and render a short WAV. The skill uses REAPER's built-in features and does not depend on third-party plug-ins.
