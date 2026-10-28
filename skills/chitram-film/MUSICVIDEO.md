# MUSICVIDEO — music videos, lyric videos and beat-driven edits

Use this when the **song is the spine**: a music video (animated or from footage/photos/AI clips), a
lyric video, a beat-synced montage, a velocity edit, or a Reel cut to a track. MUSIC.md chooses and fits
the music; SOUND.md adds SFX; ENGINE §4 holds the kits. This file is how the whole video is planned,
animated and checked.

Learned from two Claude-made music videos (JohnHeibel/PDoomVideo, "I'm Upping My P(doom)", 156.6 s,
and its base kit ClaudeAnimationBase, local copies in `D:\tools\refs\`): a song-time timeline of
chapters and shots, every shot a pure function of time, beat helpers, a camera with shake on hits,
storyboard-first with "reads", motivated transitions, a recurring set that escalates each chorus, a
palette arc, chapter work split across subagents with one shared guide, and a contact-sheet/strip review
loop. Chitram does the same with HTML/GSAP + its kits, plus measured music (`music.py`) instead of a
hand-typed BPM.

---

## 0. THE LAW of a music video

1. **The song decides the structure.** Analyse it first (`music.py analyse`): BPM, bars, 4-bar phrases,
   sections (intro / verse / build / chorus-drop / break / outro), drops, accents. Every chapter starts on
   a section, every cut on the grid, the biggest visual on the biggest drop.
2. **Something happens in every shot.** A shot is an event (something changes between its first and last
   frame), not a pretty still. One focal action at a time, big silhouette, reads at a glance.
3. **Every seam is a transition, and it is motivated** by the action or the music (a hit, a whip, a
   splat on the snare, a zoom through an eye, a flip on the beat switch). 2–4 transition families per
   video, repeated, with the showpiece transition saved for the drop.
4. **Choruses return to the same set and escalate** (bigger, more people, more FX, harder cuts). The
   viewer recognises the chorus by the place; the escalation is the story.
5. **Text-light.** Lyrics may be on screen (karaoke/kinetic) but never signs that repeat the lyric. Show
   the line, don't write it.
6. **Pure function of time.** Everything visible derives from `t` (seeded noise, no Math.random, no
   carried state): frames render in parallel and out of order.
7. **Look at it.** Contact sheets for every shot, frame strips for every key motion and transition (§6).

## 1. Analyse the song and the lyrics

```bash
python $SKILL/audio/music.py analyse song.mp3                 # grid + sections + drops -> read the png
python $SKILL/tools/shortform/sf.py ingest song.mp3 work/lyr --model medium --prompt "<title, names>"
#   word times for the vocal (Telugu: Sarvam ASR is more reliable here; Whisper medium may run out of RAM)
```
- Fix the lyric words by hand (ASR mishears sung words), then group them into **lines** `[start, end, text]`
  (like PDoom's `lyrics.js`) and keep the word times for karaoke/kinetic type.
- If the video is shorter than the song: `music.py fit song.mp3 --duration 30 --drop-at <reveal>`
  (splices on phrases, real ending). Use `beats.js` (window.MUSIC) for every time in the film.

## 2. The storyboard (write it before any code)

```
Logline: one sentence. <who> wants ___, but ___, so ___.   (or the song's emotional idea)
World: places/sets, a small palette, the colour arc across the song (e.g. warm lamp → sky → violet → red alarm → warm)
Motif: what recurs and pays off (a prop, a character, a meter, a colour)
Chapter map (one per song section, start = section start):
  1 · Intro (0.0–8.2)   set ___  palette ___   [in: ___]
  2 · Verse 1 (8.2–23)  ...
  3 · Chorus 1 (23–38)  the stage set, level 1 of escalation
Shots (per chapter, cut on downbeats/phrases):
  t0–t1  lyric "…"   SHOT: what is seen · the EVENT · camera move · FX     [out: transition + why]
     reads:  t–t  the first thing the viewer must understand (where is the eye?)
             t–t  the next one
```
- A shot is 1.4–4 s (2–8 bars at 100–130 BPM). A shot is as long as its reads need.
- Plan the drop shot first (the showpiece), then the chorus set, then the verses.
- Check: an event in every shot? every read has time? a transition at every seam? no lyric-signs? does the
  ending rhyme with the opening?

## 3. Building it in chitram

- **Song time = film time.** One `index.html` per video (or one per chapter for long songs, joined after).
  Load `assets/<song>.beats.js`; `const G = FX.grid()` gives `beats · downbeats · phrases · accents · drop · sections`.
- **Shots:** full-frame scene containers (`<div class="layer" data-in data-out>`), each with a camera
  rig: `const r = FX.rig("#shotX .content")` → `r.move` (handheld/wiggle), `r.shake`, `r.punch`, so moves
  stack without fighting.
- **Cuts on the grid:** `FX.beatCuts(tl, shots, G.downbeats.filter(...), {punch, flash})`, or set each
  shot's window to downbeats/phrases. Build-ups cut twice as fast (every 2 beats); the drop holds.
- **Lyrics:** a karaoke bar (word fill on the word times) or kinetic type (`MK.wordsRise`, `MK.karaoke`,
  `SF.captions` with the lyric words) in the bottom safe band; keep faces and action above it.
- **Per-frame painters:** `Film.onFrame(t => …)` for anything drawn every frame (particles, custom canvas
  art, p5-style painting). Must be a pure function of `t`.
- **Long songs → subagents:** write a chapter guide (palette, cast, kits, rules, review commands) and
  give each subagent one chapter file; one agent owns the shared files and the final join. Each agent
  checks its chapter with sheets and strips before reporting.

## 4. The animation catalogue (what to use on which asset)

All calls are in `engine/fx-kit.js` (FX) unless marked MK/ED. Times come from the grid.

### Camera moves (any asset)
| Move | Call | Use |
|---|---|---|
| Handheld (slight sway + micro jitter) | `FX.handheld(tl, r.move, t0, t1, {amp:10})` | documentary / phone feel; every static photo |
| Wiggle (AE wiggle) | `FX.wiggle(tl, el, t0, t1, {freq:3, amp:14, rot:2, scale})` | energetic stickers, cut-outs, logos on the beat |
| Slow push / pan | `tl.to(r.punch, {scale:1.08, duration})` · `FX.drift` | holds, emotional lines |
| Zoom punch on beat | `FX.punch` · `FX.beatPulse(tl, r.punch, G.downbeats)` | the edit breathing with the music |
| Camera shake on hits | `FX.shake(tl, r.shake, t, {amp})` | 808 / snare / impact / drop |
| 2.5D parallax dolly | `FX.parallax(tl, [{el:bg,depth:0},{el:cutout,depth:1}], t0, t1, {push, pan})` | one photo + its cut-out → 3D-feeling shot |
| 3D zoom (Z axis) | `FX.zoom3d(tl, el, t, {from:-1400, through})` | title/logo/card flies out of depth (or through the lens) |
| XYZ-axis 3D move | `FX.xyz(tl, el, t, {from:{rotationX, rotationY, rotationZ, z}})` | tilted product/card/phone turning to face camera |
| Depth of field / rack focus | `FX.dof(tl, {bg, subject, blur, at})` | subject sharp, background soft; rack on a lyric turn |
| Speed ramp (velocity) | `FX.speedRamp(footage, [[t,1],[t,.25],[t,3],[t,1]])` | footage/AI clips: slow-mo → snap on the beat |

### Transitions (between shots)
| Transition | Call | Best on |
|---|---|---|
| Zoom-in (push into a point) | `FX.zoomIn(tl, from, to, t, {x, y})` | into an eye, a screen, a window; verse → chorus |
| Zoom blur | `FX.zoomBlur(tl, from, to, t)` + `FX.flash` | drops, beat switches |
| Wipe (left/right/up/down/**all sides**/center/diag) | `FX.wipe(tl, el, t, {dir:"all"})` | clean graphic changes; "all" = box opening |
| Slight slide wipe (left/right) | `FX.slideWipe(tl, from, to, t, {dir:"left", dist:12})` | quick on-beat shot changes, carousels |
| 3D flip (card turn) | `FX.flip3d(tl, from, to, t, {axis:"y"})` | before/after, A/B, reveals on a beat switch |
| Splatter (+ zoom) | `FX.splatter(tl, t, {colors, zoomTarget})` | snare/clap hits, chorus entry, energetic brand colours |
| Tear (torn paper) | `FX.tear(tl, from, t)` (ED.tear when loaded) | collage / scrapbook / editorial worlds |
| Whip / push / iris / blinds / shutter | `MK.transition(tl, t, {type, from, to})` · `MK.whip` · `ED.iris` | travel, focus, rhythm |
| Glitch | `FX.rgbSplit` + `stack:glitch` | tech, error, beat stutter |
| White-out / flash | `FX.whiteOut` · `FX.flash` | the drop, a memory cut |
| Brush/ink wipe | `MK.blobWipe` · `FX.splatter` | chapter breaks (PDoom used fat brush strokes) |

### Reveals and accents (on an element)
| Effect | Call | Use |
|---|---|---|
| Pop-up (squash → overshoot → settle) | `FX.popUp(tl, els, t, {stagger})` | stickers, emojis, cards, cut-outs, captions |
| Shine (gloss sweep) | `FX.shine(tl, el, t)` | logos, product, gold cards, end card |
| Sweep light (beam across frame) | `FX.sweepLight(tl, t, {dir})` | reveals, chapter starts, a beat accent |
| Light leak / film burn | `FX.lightLeak(tl, t)` | memories, warmth, soft transitions |
| Glow / neon | `FX.glow(el, {color})` | night, neon, synthwave titles |
| Particles | `FX.particles(tl, {type:"dust"|"sparks"|"embers"|"confetti"|"snow"|"bokeh"|"burst", at, from, to})` | atmosphere; `burst` on the drop/logo |
| Kinetic type | `MK.wordsRise · MK.blurIn · MK.blockWipe · MK.glitchIn · MK.karaoke` | lyrics, hooks |

### By asset type
- **Photo:** handheld + slow push or parallax (cut-out on top), DoF, light leak/grain; pop-ups for
  stickers; transitions zoomIn / slideWipe / flip3d. Never a dead still.
- **Footage / AI video clip:** speed ramp on 2–3 moments, punch on downbeats, shake on hits, grade + grain,
  zoom-blur on the drop. Keep camera moves on the rig, not on the video element.
- **Cut-out (person/product):** pop-up or zoom3d in, wiggle on beats, parallax over its background,
  shadow; `sf.py cutout` makes them.
- **Logo / title:** zoom3d or xyz in, shine, glow, sweep light, particles burst, `stack:reveal` SFX.
- **Type / lyrics:** kinetic reveals on word times, punch on the stressed word, wipe/flip on line change.
- **Illustrated / character:** squash-stretch, anticipation, overshoot (ClaudeAnimationBase principles:
  faces act, never snap; nothing is still; avoid twinning; exaggerate), dance on beats, boil (ED.boil).

### Taste rules
One look per video (grade + grain + vignette) · 2–4 transition families, repeated · FX on meaningful
beats (downbeats, phrases, accents, the drop), never on every beat · velocity ramps on 2–3 moments ·
the drop gets the biggest combo once · after a dense passage give 1–2 bars of air.

## 5. Escalation map (the chorus)

| Chorus | Set | Energy | FX |
|---|---|---|---|
| 1 | the stage/set introduced | cuts every bar | punch + flash on downbeats |
| 2 | same set, more people/props | cuts every 2 beats in the build | + shake on accents, sparks particles |
| 3 | same set, transformed (night, flood, fire…) | velocity ramps | + splatter / zoomBlur transitions, letterbox |
| final | biggest version, then the reveal/twist | the drop holds longest | the showpiece combo once, then air, then the ending rhyme |

## 6. Review loop (you cannot watch it: look at frames)

```bash
node $SKILL/bin/render.mjs films/<n> --at scenes                       # contact sheet: every shot's middle
node $SKILL/bin/render.mjs films/<n> --at 12.0,12.1,12.2,12.3,12.4      # a strip around a hit/transition
node $SKILL/bin/render.mjs films/<n> --at every:0.5                     # the whole piece, 2 fps
node $SKILL/bin/render.mjs films/<n> --from 22 --to 26 --draft          # a draft section with the music
```
Check per shot: the event reads from its sheet alone; first/last frames of every seam (no flashes of a
lower layer, no blank frames); hits land on beat frames (compare with `music_fit.json`); nothing important
under the lyric band; motion has anticipation and follow-through (strips every 0.1 s); no text that
repeats the lyric; the chorus visibly escalates; the ending rhymes with the opening.

## 7. Delivery

The MP4 (1080×1920 for Reels, 1920×1080 for YouTube), the music licence/credits (or the in-app trending
sound instruction, MUSIC.md §4), the storyboard, and the list of sounds fetched (CREDITS.txt).
