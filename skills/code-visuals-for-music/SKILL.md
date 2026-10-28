---
name: code-visuals-for-music
description: Build and revise music videos with Python audio and asset preparation, Chitram HTML/SVG/Canvas animation, GSAP timelines, and FFmpeg rendering. Use for narrative music visuals, lyric videos, reference decoding, or motion proofs where visual quality and musical timing matter.
---

# Code Visuals for Music

Build a visual performance of the song. Preserve the user's chosen art direction and make characters, environments, typography, and transitions serve the musical story.

## Choose the scope

- **Decode:** inspect a reference across its full duration and deliver a timecoded account of its visual grammar and feasible construction methods.
- **Prototype:** create a representative motion proof using the intended artwork and animation technique.
- **Build or revise:** preserve accepted assets and choices; implement the requested shots and export the video with an honest review report.
- Do not start a full video when the user requested analysis only. Carry existing render authorization forward; additional permission is not needed for each routine stage.

## Hybrid architecture

Use Python for audio features, transcript alignment, asset preparation, and custom numerical effects. Use Chitram's HTML/CSS/SVG/Canvas + GSAP timeline for composition, typography, eased motion, previews, and transitions. Use FFmpeg for encoding and muxing. Prefer one master song clock and one composition owner per shot.

Read [references/hybrid-engine.md](references/hybrid-engine.md) when setting up or integrating engines. Chitram is an external dependency, not bundled here. This skill includes original preparation and validation helpers; it does not claim to include a complete animation engine.

## Start with evidence

1. Locate the exact audio, visual references, previous concepts, and existing project. Inspect media metadata and actual frames. Record duration, aspect ratio, deliverable size, lyric language/script, and requested story. Ask only for missing inputs that prevent useful work.
2. For a reference video, sample every section plus dense strips around transformations. Identify line behavior, silhouette design, staging, transitions, motion timing, and repetition. A contact sheet establishes composition; it cannot prove motion quality.
3. For an approved concept image, identify which properties must survive animation: character design, proportions, line weight, texture, lighting, spatial depth, and palette. A concept image is a visual target; it is not automatically a usable background plate.
4. Separate measured evidence from interpretations. A song's volume envelope is not its beat grid, and neither establishes lyrical meaning.

## Song and story map

Read [references/music-and-story.md](references/music-and-story.md) for alignment and narrative decisions. Keep data in `project.json`; its contract and a filled synthetic example are in [references/project-contract.md](references/project-contract.md) and [assets/example-project.json](assets/example-project.json).

- Establish verified section boundaries, beat/downbeat candidates, dialogue, and lyric cues on the source audio clock. Check important accents against playback.
- Keep original lyrics, transliteration, translation, and semantic interpretation distinct. Label uncertain transcription. Do not silently substitute a few confident lines for requested full lyric coverage.
- Write shots as state changes: desire → action → resistance → consequence. Every shot needs an observable event. A repeating run cycle needs actual progress, an encounter, or a changed outcome.
- Map color to the story and music. Recurring sections can return to a recognizable setting with a meaningful change. Do not force a generic drop/chorus structure onto every song.

## Prove the look in motion

Read [references/motion-craft.md](references/motion-craft.md) before designing character motion or transitions.

1. Build representative style frames from the intended production assets. If there is an accepted concept, compare directly against it.
2. Render short, audio-synced proofs covering the difficult action and transition. Include a speaking-character proof when dialogue is important. Reuse these shots in the final film.
3. Inspect real-time playback where possible and frame strips for contacts, turns, silhouettes, transitions, and text. If playback is unavailable, disclose that limitation and provide the clip for review.
4. Record `proofs` in the project manifest and the evidence in `review.md`. Resolve visible clipping, foot sliding, sprite jumps, accidental duplicates, and style drift before extending the treatment.
5. If the user rejected a treatment, do not scale it into a longer render. Make a materially different proof. Request their response when their preference is necessary to select the revised direction; continue independent preparation while waiting.

Moving the camera over a painting, warping a whole background, or adding particle effects does not by itself meet a request for character acting and constructed motion graphics. Use those techniques where they support the intended movement.

## Build and verify

- Drive every visible state from absolute song time. Seed procedural variation. Keep asset initialization separate from per-frame evaluation. Seek backward, forward, and directly into a shot to expose state errors.
- Animate separate character parts or deliberately authored cels. Use contact anchors and consistent scale. For substantial acting, build a rig or a sufficient pose sequence; do not assume a few generated poses form a coherent performance.
- Keep small lyrics legible at the actual viewing size, away from faces and action. Use brief, controlled reveals and adequate reading time. Honor transliteration and layout preferences exactly.
- For phone dialogue, stage the speaker, listening character, gaze, handset, and message direction. Place dialogue where requested. Energy-driven mouth cycling is an approximation; precise lip-sync needs phoneme/viseme timing.
- Render bounded frame batches or Chitram workers appropriate to available memory. Prove a short segment at final resolution before a full export; do not silently downscale to meet performance limits.
- Use `scripts/project.py check project.json` for data checks and `export` for browser timing data. These checks do not establish artistic quality or transcript truth.
- Inspect transitions, beginning/end, subtitles, dialogue, and representative motion. Verify the output duration and streams with ffprobe, then decode the full file with FFmpeg. Report visual, technical, and lyric review separately.

## Deliver

Provide the playable video, editable project, timing data, and a concise `review.md`: evidence inspected, actual resolution/FPS/duration, lyric coverage, animation limitations, and unresolved deviations. Do not call a technical pass an artistic approval. Do not promise token savings or faster rendering without measurement.

## Helpers

```bash
python3 scripts/project.py check path/to/project.json
python3 scripts/project.py export path/to/project.json --out path/to/film/assets/project.js
python3 scripts/review_media.py path/to/render.mp4 --start 12 --seconds 4 --out path/to/review
```

The first helper needs Python 3.10+. The second also requires FFmpeg/ffprobe. For setup, attribution, and install instructions, see the repository [README](README.md).
