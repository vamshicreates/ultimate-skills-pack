---
name: script-to-video
description: Turn a supplied screenplay into character dialogue voices, color or monochrome shot storyboards, an audio-timed animatic, an editable timeline, and a rendered video. Use for end-to-end script-to-video production; use screenplay-storyboards alone for boards only and video-use alone for editing existing footage.
---

# Script to video

Own the whole production from source script through reviewable edit. Use the existing [screenplay-storyboards](../screenplay-storyboards/SKILL.md) method for script coverage, shot design, continuity, reference images, boards, and PDF. Use [video-use](../video-use/SKILL.md) for the edit, overlays, captions, audio fades, preview, visual inspection, iteration, and final render. This skill provides the bridge between storyboard stills, generated dialogue, and video-use's footage-oriented EDL. Read [project format](references/project-format.md) before writing the animatic manifest.

## Decide the deliverable

Identify whether the user wants a **storyboard animatic** (timed stills, camera moves, voices, sound), a **moving film** (shot footage or animation must be supplied or created), or both. Never present still-image movement as filmed performances. Collect only missing creative inputs that matter: script, target format/runtime, color versus monochrome, language/accent, character references, voice choice, captions, and available footage. Use sensible defaults for minor choices and record them in the project.

## Script and voice map

Read the full script. Follow screenplay-storyboards' scene inventory, source anchors, beat map, stable shot IDs, shot list, and continuity bible. Make a separate dialogue ledger with one ID per scripted spoken line: scene/shot, exact text, character, delivery, pronunciation notes, and status. Preserve the script wording unless the user requests a rewrite. Give each character a stable voice ID and short voice direction; vary delivery per line, not the voice identity. Keep narration and off-screen speech distinct from on-screen dialogue. Record intentional silence, reactions, and nonverbal sounds as beats.

Choose voice production per project: user recordings where supplied, an available TTS provider when licensed and affordable, or a local engine for drafts if its language and performance are adequate. Test a small multilingual/emotional sample before generating the full cast. Check the provider's current pricing, commercial use terms, and language support at production time. Clone a real person's voice only with their authorization. Generate one audio file per dialogue ID, keep the source text/provider/voice settings in a voice manifest, inspect and regenerate poor pronunciations or performances, and measure actual audio durations with `ffprobe`. Calculate a cost ceiling before paid calls; reuse accepted clips on reruns.

## Boards and shot assets

Use screenplay-storyboards' shot design and image quality checks. The user chooses `monochrome` or `color`; the storyboard manifest and each board inherit that style. Its composition and PDF helpers now preserve color when requested. Keep text outside generated art. The board PDF is for review, while the animatic needs **one clean 16:9 image per shot**. For dialogue-driven scenes, give each spoken turn a dedicated full-frame image tied to its dialogue ID and shown when that line plays; set `one_image_per_dialogue: true` in the animatic manifest. Add silent establishing or reaction images where the edit needs them. Do not crop a multi-panel triptych and assume each result is a usable full-frame shot: generate or compose dedicated shot images from the approved shot plan and continuity references. Map each image to exactly one shot ID. Lock a character bible and a location/floor-plan bible before generation. Preserve 180-degree geography, character appearance, props, lighting, and adjacent-shot continuity. Estimate and confirm the image-generation call ceiling as required by screenplay-storyboards before the first image call; track actual calls.

## Edit from dialogue timing

Build the edit around accepted voice clips and meaningful pauses. Give every shot a duration long enough for assigned speech and reactions; let one line span shots only after deliberately splitting it into edited audio pieces with clear IDs. Put dialogue text in a subtitle track when requested, never permanently into the shot art. Record shot image, duration, camera note, dialogue clip IDs, and offsets in `animatic.json` using [project format](references/project-format.md). Run:

```bash
python3 ~/.codex/skills/script-to-video/scripts/prepare_animatic.py /absolute/project/path/animatic.json
```

This writes `edit/render_sources/*.mp4` (stills plus dialogue), `edit/picture/*.mp4` (silent picture), `edit/edl.json`, `edit/master.srt`, and `edit/timeline.otio` with separate picture and per-character dialogue tracks. All media paths in the manifest may be absolute or relative to the project root. Resolve input failures, overlapping same-character lines, and duration violations before editing.

Use `~/.codex/skills/video-use/helpers/render.py` on the prepared EDL for the preview and final MP4. Its existing audio fades, overlay timing, subtitles-last order, loudness pass, and cut review apply. Do not run `--build-subtitles` on generated dialogue unless word-level transcripts were separately produced; the bridge already writes the line-timed `master.srt`. To make a no-caption version, pass `--no-subtitles`. Add music, SFX, camera motion, and visual overlays through video-use's normal edit process when the scene calls for them. For an editor-friendly FCPXML, the existing timeline exporter at `$HOME/Documents/VamshiCreates/Caveman Video Editing/helpers/export_timeline.py` can export the video-use EDL; its dialogue is embedded in the preview source clips. Use `timeline.otio` when separate character audio lanes are needed. Verify imports in the intended NLE before calling them production ready.

## Review and delivery

Use a short scene as a pilot before generating a full screenplay. Review script coverage, voice identity/pronunciation, board style/character consistency, actual audio timing, every cut, subtitle position, and beginning/end frames. Show the user the storyboard and preview for creative feedback, then revise only affected assets. Deliver the storyboard PDF, dialogue ledger and clips, clean shot images, `animatic.json`, `edit/edl.json`, `edit/timeline.otio`, preview, and final MP4. If moving footage was requested, add approved footage or animated shots to the same timeline and describe any still-only sections honestly. Keep reruns resumable: stable IDs, original media, provider settings, cost log, and accepted asset paths remain in the project.
