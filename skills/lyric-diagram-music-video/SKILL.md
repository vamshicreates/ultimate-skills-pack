---
name: lyric-diagram-music-video
description: "Make a HUD/science-diagram lyric music video, all in code, from a song file in the user's folder plus its lyrics (any language, e.g. Telugu, Hindi). Use when the user gives an audio file and a lyric sheet and wants the finished video."
---

# Lyric-diagram music video

The user gives (1) a song file in a local folder and (2) the lyrics (pasted, or a .txt/.md/.docx in the folder). You make a music video **entirely in code**: one HTML page with one canvas and a pure `renderFrame(t)`, captured frame by frame by a headless browser and muxed with the song by ffmpeg at 1920x1080, 30 fps. The look is a calm, premium science-HUD: each lyric's key word is taught like a vocabulary card while its object animates as a diagram.

Code template: `reference/template.index.html` in this skill folder. Copy its helper layer and scene structure instead of rewriting them; set the per-song `SONG` block (title, artist, title syllables, times).

## 0. Ask first: the accent colour (always)
Before any work, ask the user **one question: which accent colour?** The whole video uses one accent, so this decides the look. Use AskUserQuestion when available, with options such as:
- **Orange `#ff5a1f`** (default)
- **Electric blue `#2f7bff`**
- **Magenta `#ff2e88`**
- **Lime `#b6ff3b`**
- or any hex / colour name they type (convert names to hex)

Set it as `ACCENT` at the top of the template; every accent element (lines, glows, IPA, highlights, comets, the beat square, cut bar) follows it. Keep the red stamp `#c62f25` unless the chosen accent is itself a red, then use deep ink-blue `#1d3b8f` for the stamp instead. If the user is not there to answer, use orange and say so. Ask nothing else unless it is truly unclear.

## 0b. Defaults
- Start with a **1-minute sample** that ends on a phrase boundary and, if possible, on the first sung title or hook. Build the full song only after the user approves the sample.
- No artwork or images. Everything is drawn on canvas.
- Language: use the lyrics' script for the big words (Telugu: Anek Telugu; Devanagari: Anek Devanagari; Latin: Anek Latin). Mono labels: JetBrains Mono. IPA: DejaVu Sans Mono (it has the IPA glyphs). Put the script font in the mono stack too, so script text inside labels does not fall back to a system font.

## 1. Style DNA (keep exactly)
- Background near-black `#0a0a0b` with a faint radial lift (`#141416` centre), which stops banding.
- **One** accent: the colour the user picked (`ACCENT`, default orange `#ff5a1f`). Everything else is cream `#ede6da` at different opacities.
- 2 to 3 **cream paper-form scenes** per minute: cream fill, faint fibre specks, a 60 px form grid, a header rule with `FORM 0n · <word> · <ENGLISH TITLE>`, field rows (SUBJECT / OBJECT / MEASURE), ink `#17140f`, and a **red stamp** `#c62f25` (double border, slam-in scale 1.9 to 1 over 0.12 s, rotated ±6 to 9°, ink-wear specks knocked out with destination-out) that lands on a musical hit.
- Thin **HUD corners** (30 px L-brackets, 46 px inset). Tiny mono labels: top-left `TITLE — ARTIST`, top-right `BPM · BAR · BEAT` (live), bottom-left `SCN nn/NN — <word>`, bottom-right `T mm:ss.ss`, plus a small accent square that flashes on every beat.
- **Big glowing word**: script font 600 weight, 150 to 270 px. Draw it on as an accent-coloured dashed stroke (animate lineDashOffset), then fade in a cream fill with an accent shadowBlur glow. Under it go an IPA readout (accent mono), then a tiny label `NOUN · MEANING`.
- **Conjunct / letter-math** in one or two scenes per minute, taken from words actually in the lyric: e.g. `క + ్ + ష = క్ష`, `త + ् + र = त्र`. Build it piece by piece on the beat when that word is sung, with the result in the accent colour.
- Bloom: a second, half-resolution canvas that copies the frame each render, `filter: blur(18px) brightness(1.25)`, mix-blend screen, opacity .55 (.12 on paper scenes). Film grain about .085 opacity; vignette strength .45 (dimmed to .3 on paper).
- Lyric captions sit bottom-left: an accent tick bar, `LYRIC mm:ss` in accent mono, the line in the script at 50 px revealed left to right by a clip, then `ROMANISED — ENGLISH` in mono caps. Fade each line out within 0.22 s of its end so lines never overlap.
- A cut accent on every scene change: an accent 6 px scan bar sweeping top to bottom in 0.2 s, plus a 10 px camera kick that decays as exp(-14t).

## 2. Workflow (use a task list)
1. **Find the files.** If the folder isn't connected, ask for it or request access. Read the lyrics. Stage the song into the workspace (or work on the device shell if it is fast enough).
2. **Beats and sections.** Analyse BPM, beats, downbeats, 4-bar phrases and sections. If the chitram-film skill is present, run `python3 <skill>/audio/music.py analyse song.mp3`; otherwise use your own onset/RMS analysis. **Check the downbeat phase against measured onsets** (10 ms RMS jumps over 15 dB); analysers are often off by half a bar. Write `assets/beats.js` (`window.MUSIC = {bpm, beats, downbeats, phrases, hits}`), where `hits` are the measured band entrances, stop-hits and drops.
3. **Envelopes.** Per frame, write all-band, vocal-band (300–3400 Hz) and low (<150 Hz) envelopes, plus about 96 raw voice-band samples per frame for an oscilloscope, to `assets/env.js`. Smooth with attack/release.
4. **Lyric timing.** The user's lyrics are the text truth; ASR is only for **timing**. Run faster-whisper (large-v3 int8 is best; look for already-downloaded models in `~/.cache/huggingface/hub` on the user's machine before downloading) on the original mix in **short vocal-activity chunks (0.6–9 s)** with `language=<lang>`, `beam_size=5`, `condition_on_previous_text=False`, `no_repeat_ngram_size=3`, `repetition_penalty=1.2`. One long pass hallucinates loops under loud bands. A cheap vocal separation (REPET-SIM: per-frame median of the 40 most similar STFT frames at least 1 s away, soft mask, times a centre-pan mask, band 120–7000 Hz) helps find the chunks. Align each given lyric line to the chunk whose transcript matches it best. Word timestamps give the exact sung time of the hook. If there are no lyrics, transcribe, mark each line H/M/L confidence, show only H/M on screen, and write `LYRICS-DRAFT.md` for the user to correct.
5. **Storyboard.** Write `brief.md`: one scene per 4-bar phrase, **every scene starting on a phrase downbeat**, internal events on beats or hits. For each scene pick one key word **from the lyric sung in that phrase** (or the song's central image) and one diagram that physically shows it. Structure: open on a single primitive (the script's headstroke or line, e.g. తలకట్టు / शिरोरेखा) alive with the intro voice, then the title syllables hanging from it with IPA, then a **chart of the script's consonants by place of articulation x voicing** with the title's sounds lighting up on hits and a vocal-tract schematic dot, then the word scenes, and end on the sung title filling with light, syllable by syllable, in a burst (rays plus particles plus a radial flash), then fade.
6. **Build** `index.html` (section 3). Write all scenes, then render **a still of every scene** (mid-scene plus key moments) as a contact sheet and **look at it**. Fix clipping off-frame, overlaps (stamp over labels, words over lines), unreadable labels and empty frames. Re-render the stills you fixed.
7. **Final render** of the sample, then probe it (duration, 1920x1080, audio stream) and look at a 10-frame strip. Deliver an H.264 CRF 22 + AAC 256k file (keep it under 30 MB if it must be written back through the device bridge). Put the MP4 next to the song, and the project plus `LYRICS-DRAFT.md` in `films/<name>/`.
8. After approval, extend to the full song: keep the approved scenes exactly as they are and append new phrases. Bring the chart back on later choruses with more letters lit (escalation).

## 3. Code architecture (single file)
- `<canvas id=cv 1920x1080>` plus `<canvas id=bloom 960x540>`. Load fonts with @font-face (local files in `assets/fonts/`, variable TTF fine) and put hidden spans that use each font, so they load before the first frame.
- If chitram-film is available, use its runtime: `Film.build(tl => { FX.grain(...); FX.vignette(...); Film.onFrame(renderFrame); })`, with root `data-duration`, `data-fps=30`, `data-audio=assets/song.wav`; render with `node <skill>/bin/render.mjs <film> --at 5,13.5,...` for stills and `--out out/master.mp4` for the film; QA with `bin/check.mjs --fast`. Otherwise write a Playwright loop that calls `window.renderFrame(t)` for each frame, screenshots, pipes the frames to ffmpeg, and muxes the song.
- Helpers: `clamp, lerp, prog(t,a,b), eo (easeOutCubic), eo5, eio, hash(n)` (deterministic noise, **never Math.random or clocks**), `env(key,t)`, `beatIdx/sinceBeat`, `text(s,x,y,{f,w,size,ls,color,glow,blur,stroke,dash,dashOff,align,a})`, `label`, `ipa`, `line`, `circle`, `arrow`, `bigWord`, `stamp`, `paper`, `hud`, `lyric`, `cutAccent`, `typed(s,t,t0,cps)`.
- `const SC = [{a, b, n, tag, fn, paper?}]` on phrase times. `renderFrame(t)`: reset the context, find the scene, fill the background, apply the cut kick, call `sc.fn(t, sc)`, then `lyric`, `hud` and `cutAccent`, fade to black at the end, and copy to bloom. Every pixel must be a pure function of t.

## 4. Diagram vocabulary (pick by the lyric's meaning)
| Lyric idea | Diagram |
|---|---|
| distance, far | paper form: A to B with a dashed musical route, dimension line with ticks, `d = ?`, stamp |
| run, step, feet | footprints landing on every beat scrolling left, gait-cycle dial (stance/swing arcs, phase hand), velocity arrow |
| moment, time, wait | stopwatch, hand stepping on beats, 16 beats = 1 turn = 1 phrase, live seconds readout |
| rainbow, colours, light | paper form: horizon arc (`sky's edge`), prism, white ray, 7 rays with nm labels (only one in the accent), stamp `7 colours` |
| coming closer, searching | radar: rings, rotating sweep wedge, her at the centre, his blip's range stepping down per beat, per-beat bar graph |
| circling, wandering, devotion | Kepler orbit: ellipse, she is the focus, equal-area wedges per beat (show only the last 3), velocity vector |
| voice, call, talk | oscilloscope from `ENV.osc`, RMS/gain readouts, waveform on a paper form |
| eyes, seeing | eye cross-section ray diagram, lens refraction, image on the retina |
| clouds, obstacles | flow field / cloud chamber; projectile arcs over hurdles with apex labels |
| meeting, the end | two lines converge on a point of light, then the final burst |

## 5. Hard-won rules
- Cut **every** scene on a phrase downbeat. Put stamps, highlights and conjunct builds on measured hits or sung words, not guesses.
- Telugu/Indic in mono labels needs the script font in the stack. Check every still for tofu or fallback glyphs.
- Keep big words inside the frame (measure text; if it is wider than ~45 % of the frame, reduce the size). Keep stamps off labels.
- Don't invent lyrics. Low-confidence lines stay off screen; English glosses are approximate and labelled in the draft file.
- Long jobs: run renders in the background (`setsid nohup … &`) and poll the log. Never `pkill -f` a pattern that matches your own shell command.
- Blocked network: fonts can come from `raw.githubusercontent.com/google/fonts/main/ofl/<family>/<File>[wght].ttf`; models from the user's own HF cache via the device bridge (split large files under 400 MB to stage them). Leave temporary copies in `_to_delete/` and tell the user.
- Time guide: 1-minute sample ≈ 1.5–2 h (transcription 30 min, build 45 min, stills/fixes 20 min, render ≈ 16 min at about 2 fps). Full 4-minute song ≈ 3 h.

## 6. Files bundled with this skill (paths relative to this folder)
- `reference/template.index.html` — the working template: copy its helper layer (math, text/label/ipa, bigWord, stamp, paper, hud, lyric, cutAccent, renderFrame) and swap the scenes. Edit its `SONG` block per song. `reference/lyrics.js` / `beats.js` show the data formats.
- `scripts/repet_separate.py song out.wav START DUR` — REPET-SIM vocal separation (numpy/scipy only).
- `scripts/asr_chunks.py song sep.wav out.json --model <faster-whisper dir> --lang te` — phrase-chunked Whisper with word times.
- `scripts/envelopes.py song assets/env.js --dur N` — per-frame all/voc/low envelopes + oscilloscope samples.
- `assets/fonts/` — Anek Telugu (variable) and DejaVu Sans Mono (IPA). For other scripts fetch the matching Anek family.
