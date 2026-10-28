# ENGINE — code the film in HTML/CSS/GSAP and render it to MP4

Phase 2 of 2. Input: the Production Brief + Build Sheet from `DIRECTOR.md` (saved as `brief.md`).
Output: `out/film.mp4` (H.264 + AAC), plus the project folder (editable, re-renderable).

The engine is ours (no HyperFrames, no Remotion): **a film is one HTML page with one paused GSAP
timeline**; `bin/render.mjs` seeks that timeline frame by frame in headless Chromium, screenshots
each frame, and pipes the frames into ffmpeg. Anything you can build in a browser, you can render.

`$SKILL` below = this skill's folder (`.claude/skills/chitram-film`).

You are a **senior motion developer**: you write animation the way a top After Effects artist
keyframes — deliberate timing, eased curves, layered depth, nothing accidental. Code is your
keyframe editor.

## THE LAW (every build; a violation is a failed job)

1. **Build what the brief says, in the brief's order and times.** The Build Sheet is the contract.
   If something can't be built as written, say so and propose the nearest buildable version —
   never silently change it.
2. **Static layout first, then motion.** No timeline code before the final-state layout has been
   snapshotted and looks right.
3. **Kit before custom.** If §4/§6 has it, use it. Custom code only for `CUSTOM` rows — and only
   after §R if you are not certain how the effect is done.
4. **Deterministic or it doesn't ship:** no randomness, clocks, CSS animations, network, or `play()`.
5. **One reveal per element, one transform owner per element.** Exits use `to`.
6. **Nothing overlaps, nothing is unreadable.** Text beside the hero; `data-clear` on what text must
   never cover; every caption readable for its full reading time.
7. **Prove it.** `check.mjs --strict` clean (or every warning explained), contact sheet read, the
   final MP4 probed. Never report "done" on something you have not looked at.
8. **Edits are surgical** (§E): change only what was asked, then re-check and re-render.
9. **Don't know → research (§R), then build.** Never guess an API, an effect or a look.

---

## R. Research protocol — when you don't know how to do something

Use this whenever you meet an effect, style, technique, API or brand look you are not **certain**
how to build (e.g. "liquid glass", "Apple-style parallax text", "SVG morph", "gooey metaball",
"GSAP SplitText-like stagger", "a CRT scanline look", "how does Stripe's gradient move").

1. **Name the unknown precisely** in one line: "how to make a gooey blob merge between two circles
   in CSS/SVG, deterministic".
2. **Search the web** (WebSearch / WebFetch tools if available). Good queries:
   `"<effect> css"`, `"<effect> svg filter"`, `"<effect> gsap"`, `"<effect> codepen"`,
   `"<brand> motion design breakdown"`, `"<effect> after effects tutorial"` (for how it *looks*
   and moves).
3. **Prefer primary, working sources:** gsap.com/docs (API truth), MDN (CSS/SVG/Canvas), CSS-Tricks
   and Smashing (techniques), Codrops (tympanus.net, polished effects with code), CodePen (working
   demos), web.dev, Shadertoy / The Book of Shaders (GLSL), YouTube/School of Motion (motion
   design principles and breakdowns of how a look is timed).
4. **Read until you can explain the mechanism in two sentences** (what layers, what property
   changes, what makes it look like that). If the source is a video/tutorial, extract: layers,
   timing, easing, and the key trick.
5. **Translate to this engine:** every animation goes on `tl` at absolute times; replace
   `requestAnimationFrame` loops with tweens or `onUpdate` driven by a tweened proxy; replace
   `Math.random` with `MK.rng(seed)`; replace CSS `@keyframes`/`transition` with GSAP tweens;
   replace `setTimeout` sequencing with timeline positions; no GSAP club plugins unless their file
   is bundled locally — build the equivalent with core tweens (split text yourself, draw SVG with
   `strokeDashoffset`, morph with interpolated path points or clip-path).
6. **Prototype small:** a 3–6 s test page (`init.mjs --duration 5`), snapshot at 3–5 times, check
   the look against the source. Only then put it in the film.
7. **Record what you learned** as a short recipe comment in the film (source URL + mechanism), so
   the next edit doesn't re-research.
No web access? Say so, use the closest kit effect, and describe the gap honestly.

## E. Edit protocol — when the user asks for a change

1. Restate the change in one line ("make `#c0` 'you moved to the US.' headline-sized").
2. Find the exact element(s)/cue(s) (grep the id/copy). Touch only those lines — no refactors,
   no "while I'm here" changes, no new effects, no retiming of other scenes.
3. If the change has a knock-on (bigger text now collides with the headline), fix only that
   collision, and say so.
4. Snapshot the affected moment(s), run `check.mjs`, re-render (or `--from/--to` for a quick look).
5. Report: what changed, what else had to move, the new file. Nothing more.

---

## 0. Setup and commands

```bash
# one-time (per machine)
cd $SKILL && npm install            # playwright-core + gsap (gsap is also vendored in engine/)
npx playwright-core install chromium   # skip if Chromium for Playwright 1.56 is already present
pip install numpy scipy pillow opencv-python-headless    # audio + asset tools
# ffmpeg must be on PATH

# per film
node $SKILL/bin/init.mjs films/<name> --duration 30 --size 1920x1080 --fps 30
python3 $SKILL/tools/prep_image.py …                    # assets (§9)
python3 $SKILL/audio/music.py fit track.mp3 --duration 30 --drop-at 12 --out films/<name>/assets/music_fit.wav
python3 $SKILL/audio/mixdown.py films/<name>/mix.json films/<name>/assets/mix.wav
node $SKILL/bin/check.mjs films/<name>                  # QA gate (must be 0 errors)
node $SKILL/bin/render.mjs films/<name> --at 1.5,5,9.8  # snapshots + contact sheet
node $SKILL/bin/render.mjs films/<name> --draft         # half-res 15 fps review video (fast)
node $SKILL/bin/render.mjs films/<name> --out films/<name>/out/film.mp4   # final
node $SKILL/bin/preview.mjs films/<name>                # interactive browser preview (humans)
```

Render speed reference: 1080p ≈ 10–12 frames/s with 4 workers on a laptop-class CPU
(30 s film ≈ 75–90 s). Draft ≈ 4× faster. Snapshots are instant — use them for every check.

---

## 1. The runtime contract (non-negotiable)

1. Root element: `<div id="film" data-film data-duration="30" data-fps="30" data-width="1920" data-height="1080" data-audio="assets/mix.wav">`. These attributes are the single source of truth.
2. Scripts in order: `engine/vendor/gsap.min.js` (head) → markup → `engine/runtime.js` → `engine/motion-kit.js` → your script.
3. All animation lives inside **one** call: `Film.build((tl) => { ... })`. `tl` is a paused GSAP timeline. Position every tween with an **absolute time** (third argument).
4. Deterministic only. **Banned:** `Math.random` (use `MK.rng(seed)`), `Date.now`/`performance.now`, `setTimeout`/`setInterval`/`requestAnimationFrame` for animation, `repeat: -1` (use `MK.repeats(span, period)`), CSS `@keyframes`/`animation`/`transition`, `tl.play()`, network fetches, `<video>.play()`.
5. Offline only: every font, image, script and sound is a local file in the project. No CDN links.
6. **Never** put a CSS `transform` on an element that GSAP moves with x/y/scale/rotation. Set start transforms with `tl.set(el, {...}, 0)` or `fromTo`. Static transforms on elements you never tween are fine.
7. Reveal each element **once** (one `fromTo`/kit reveal per element). Later changes use `to` (`MK.blurOut`, `MK.dim`, `MK.fadeOut`). Two `fromTo`s on the same property of the same element fight at seek time.
8. `.t` elements start at `opacity:0` (kit CSS) and are what `check.mjs` audits for readability. Give every on-screen text element class `t`.
9. Time-scoped layers: add `data-in="12.9" data-out="16"` to a scene container; the runtime hides it outside that window (cheaper frames, no leftovers). Tweens inside still run on the one timeline.
10. Footage: image sequences `<img data-seq="assets/clip/%05d.jpg" data-count="120" data-seq-fps="30" data-at="10">` (most robust) or VP9 `<video src="x.webm" data-at="10" muted>`. Convert with `tools/prep_video.sh`. Never H.264 `<video>` (Chromium may not decode it).

---

## 2. Project structure and layering

```
films/<name>/
  index.html        the film (one page)
  brief.md          Production Brief + Build Sheet (from DIRECTOR.md)
  mix.json          the sound sheet: voice, fitted music, SFX cues/stacks (SOUND.md, MUSIC.md)
  engine/           copied by init (runtime, kit, fonts, gsap) — do not edit per film; optional:
                    if absent, the renderer and check serve the skill's shared engine/
  assets/           screens, logo, photos, footage, music_fit.wav (+ .beats.js), mix.wav
  snapshots/        check images (generated)
  out/              renders (generated)
```

**Layer stack (bottom → top). Build it in this order in the HTML:**

```
bgDark, bgLight            full-frame backgrounds; crossfade with opacity for day/night changes
ambience                   bokeh, light pools, pale type walls
stage                      3D world: device rigs (laptop/phone) and cards lifted from them
scene layers  s1…sN        per-scene content (data-in/data-out), graphic shapes
type                       captions/headlines (in front of the hero, never on its screen)
fx                         transitions (whip streaks, blob wipes, fades) — always on top
end                        brand resolution (logo lockup, bloom)
```

Positioning: layers are `position:absolute; inset:0` (`.layer`). Text uses `.t` + absolute
`left/top/width` from the layout grid (§8.4). Centre with `left:0; right:0; text-align:center` —
**never** with `transform: translate(-50%,-50%)` on an animated element.

---

## 3. Build procedure (do these steps in order)

1. `init` the project. Paste the Build Sheet into `brief.md`.
2. **Tokens:** fill the `:root` variables and type classes from the brief's VISUAL SYSTEM.
3. **Assets:** prepare every file in the "assets to prepare" list (§9). Check each image once by
   reading it.
4. **Static layout first:** write all layers and elements in their **final, fully revealed**
   positions. Temporarily call `tl.set(".t", {opacity:1}, 0)` and snapshot a few times to confirm
   layout, sizes and overlaps. Remove the temporary line.
5. **Timeline, scene by scene,** in time order, one block per Build Sheet scene, each block starting
   with a comment `// SCENE n | 00:03–00:07 | name`. Use kit functions; write raw tweens only for
   camera/device moves and CUSTOM effects.
6. **Audio:** fit the music (MUSIC.md §5), write `mix.json` SFX from the Build Sheet's sfx column (SOUND.md), run `mixdown.py`.
7. `check.mjs` → fix every ERROR and every warning that is a real problem (§11.2).
8. **Snapshots**: `render.mjs <film> --at scenes` (storyboard sheet: every scene midpoint + ends),
   plus explicit times for every transition midpoint. Read the contact sheet. Fix what fails the visual checklist (§11.3). Repeat
   6–8 until clean.
9. **Draft render** (optional for ≤ 20 s films): watch timing/rhythm.
10. **Final render.** Verify with ffprobe (duration, 1920×1080, audio stream) and look at a 6-frame
    strip (§12). Deliver the MP4 path.

### 3.1 Production stages are dependencies, not a queue
```
assets ─┐
audio  ─┼─→ (VO? duration sync: captions follow real phrase times) ─→ transitions ─→ verify ─→ final look ─→ render
layout ─┘        (static layout → storyboard sheet → animate scene by scene)
```
Independent work runs in parallel: analyse/fit the music (`music.py`) and prepare images while you
write the layout. Inside a chain, order is fixed: never animate before the static layout passes
its snapshot; never time captions to a VO you haven't measured; never render before `check.mjs`.
Batch visual checks: one contact sheet beats many single-frame looks (each image you read costs
context).

---

## 4. Kit API (engine/motion-kit.js, global `MK`)

All `t` values are absolute seconds. `target` = selector string or element. Every reveal hides its
target before `t` automatically.

### Text reveals
| Call | Use for | Notes |
|---|---|---|
| `MK.blurIn(tl, el, t, {dur=1, blur=18, y=16, sweep=true, sweepColor})` | premium headline/caption reveal: blur→sharp + light sweep | default reveal for serif luxury type |
| `MK.blurOut(tl, el\|[els], t, {dur=.5, blur=12, y=-10})` | exit | |
| `MK.fadeIn(tl, els, t, {dur=.7, y=10, stagger})` / `MK.fadeOut(tl, els, t, {dur=.5})` | small captions, taglines | |
| `MK.dim(tl, els, t, {to=.28})` | previous list item when the next arrives | "apply. → verify." stacks |
| `MK.popIn(tl, els, t, {from=.6, ease:'back.out(2.2)'})` | overshoot pop (last line, badges) | |
| `MK.blockWipe(tl, el, t, {color, dur=.7, dir:'left'\|'right', radius})` | solid block covers → text appears → block leaves | target must be shrink-to-fit (absolute, inline-block, or flex item `align-self:flex-start`) |
| `MK.maskRise(tl, el, t, {dur=.8})` | line rises from an invisible edge | |
| `MK.wordsRise(tl, el, t, {stagger=.08, dur=.6})` | word-by-word rise | |
| `end = MK.typewriter(tl, el, t, {cps=16, caret=true, caretOff})` | typing | returns end time |
| `times = MK.karaoke(tl, el, t, {step=.32 \| times:[…], pill, active, done, end})` | word highlight pill | returns word times → click SFX |
| `ticks = MK.glitchIn(tl, el, t, {dur=.42, steps=6, colors, seed})` | glitch-block reveal | returns tick times → tick SFX |
| `MK.highlight(tl, wordEl, t, {bg, dur=.55, textColor})` | gradient block wipes behind a word | wrap the word in a `<span id>` |
| `MK.sweep(tl, el, t, {color, dur})` | light sweep only | |
| `MK.blurWipeOut(tl, el, t, {dur=.6, dir})` | line smears out through a horizontal blur mask | |

### Lines & shapes
`MK.lineDraw(tl, paths, t, {dur=1.2, stagger=.12, reverse})`, `MK.lineErase(tl, paths, t)` ·
`MK.tube(svg, d, {width=14, colors, glow=10})` → `{core, glow, head}` + `MK.tubeDraw(tl, tube, t, dur)` ·
`MK.rosette(container, {size=120, petals=8, colors, rx, ry, core})` → `<svg>` ·
`MK.arcText(container, text, {radius, size, font, color, x, y, start=-90, arc=360, spacing})` → element to rotate ·
`MK.band(container, text|[texts], {faces=14, radius=700, height=120, bg, color, font, x, y, tilt=-10, roll})` → element, animate `rotationY` (container needs `perspective`) ·
`MK.typeWall(container, text, {rows=6, font, color, repeat, sep})` → rows + `MK.wallScroll(tl, rows, start, end, {dist})`.

### Transitions (return the swap time — change scene content at that time)
`swap = MK.whip(tl, t, {layer:'#fx', stage:'#stage', colors, count=9, dur=.8, dir, wash=true})` ·
`cover = MK.blobWipe(tl, t, {layer:'#fx', color, dur=1, from:'right', exit=true})` ·
`cover = MK.fadeThrough(tl, t, {layer:'#fx', color:'#000', dur=.8, hold})` ·
`swap = MK.transition(tl, t, {type, from:'#s1', to:'#s2', dur, dir:'left'|'right'|'up'|'down', color, at, layer:'#fx'})`
— scene-to-scene handoff between two full-frame scene containers; types `cut` · `crossfade` ·
`blur` · `zoom` · `push` · `whipPan` · `iris` · `blinds` · `shutter` · `dip` (velocity-matched:
the outgoing side accelerates out, the incoming side decelerates in, fastest at the swap). Both
scenes' `data-in/out` must cover the transition window. (Its test page is archived on D:.)

### Ambience & motion
`els = MK.bokeh(layer, {count=6, colors, size:[260,520], seed, edges=true})` + `MK.drift(tl, els, start, end, {amp=40, period=6})` ·
`MK.hover(tl, el, start, end, {amp=12, period=1.7, tilt})` · `MK.breathe(tl, el, start, end, {scale, opacity, period})` ·
`MK.lift(tl, card, t, {z, x, y, rotationX/Y/Z, scale}, {ghost, dur=1.1})` · `MK.settle(tl, cards, t, {ghosts})` ·
`MK.gloss(tl, bar, t, {dur=1.6})`.

### Devices
`lap = MK.laptop(container, {screenW=1150, screenH=672, lidTilt=9, shadow, perspective})` →
`{stage, rig, bob, lid, screen, lifts, glossBar, floor}` ·
`ph = MK.phone(container, {w=440, h=900, bezel=16, radius=68, island})` → `{stage, rig, phone, screen}`.

Curves (the AE graph editor): `ease: MK.bezier(x1,y1,x2,y2)` (same numbers as CSS `cubic-bezier`) and named
`MK.curves.easyEase · glide · snap · settle · anticipate · whip · exit` (MOTION.md §3).

Utilities: `MK.rng(seed)`, `MK.repeats(span, period)`, `MK.words(el)`, `MK.q`, `MK.qa`.

### Editorial kit (engine/editorial-kit.js, global `ED`) — word-locked, hand-made films
Load it after `motion-kit.js` (`<script src="engine/editorial-kit.js">`). Built for voice-driven films
whose every cut lands on a spoken word (voice from `audio/tts_vo.py` → `assets/vo/timeline.js`).
| Call | Use for |
|---|---|
| `STEP = ED.onTwos(tl, 12)` | whole film holds each pose 2 frames — stop-motion / collage / illustrated feel (render at 24 fps) |
| `T = ED.wordClock(VO)` | `T(line, k)` = film time of word k of line `line` — put EVERY hit on these |
| `ED.setWin(sel, in, out)` | scene windows computed from the word clock instead of hard-coded `data-in/out` |
| `ED.ik(tl, host, {x,y,size,center,italic,color,light,circle,words:[[w,t,css]],kfs:[{t,i,r,dx,dur}]})` | ikigai editorial line: words fade in on the voice, a solid circle glides onto the key word and the text inverts inside it |
| `ED.iris(tl, x, y, color, t)` → cover time | colour circle covers the frame from a point; swap scenes under it (paper ↔ dark worlds) |
| `ED.tear(tl, sel, t)` | torn-paper wipe (collage world → next world) |
| `ED.boil(tl, ".b", D)` | ±1.2 px / ±0.5° paper boil per held frame |
| `ED.pushThrough(tl, room, dark, x, y, t)` → reveal time | camera pushes into a point (laptop screen) while a dark world opens from it — land the music drop on the return value |
| `ED.walk(tl, el, t0, t1, dx)` / `ED.jump(tl, el, t, fromX, toX)` | flat characters: bob-walk on twos · arc jump out of a crowd |

### FX kit (engine/fx-kit.js, global `FX`) — cinematic finish + viral beat-sync
Load after `motion-kit.js`, with the music grid from `audio/music.py fit` (MUSIC.md):
`<script src="engine/fx-kit.js"></script><script src="assets/music_fit.beats.js"></script>`. All seek-safe.

| Call | Use for |
|---|---|
| `G = FX.grid()` | `G.beats · downbeats · phrases · accents · drop · sections · bpm`, in film time |
| `FX.onBeats(times, (t, i) => …, {from, to, every, min})` | run any effect on the grid (clamped to the film) |
| `FX.punch(tl, wrap, t, {scale=1.08, dur=.32})` · `FX.beatPulse(tl, wrap, G.downbeats, {scale, every, from, to})` | beat zoom hit / the edit breathing with the music (animate a WRAPPER, not the footage) |
| `FX.shake(tl, el, t, {amp=16, dur=.45, rot=1.2, freq=26})` · `FX.drift(tl, el, t0, t1, {amp=8})` | impact / 808 shake · handheld life on static frames |
| `FX.speedRamp(videoOrSeq, [[filmT, speed], …])` | velocity edit: slow-mo → snap (writes `data-remap`; the runtime time-remaps the footage) |
| `FX.flash(tl, t, {color, peak=.85, dur=.22})` · `FX.whiteOut(tl, t)` | impact flash on a hit/drop · burn to white for a big swap |
| `FX.lightLeak(tl, t, {dur=1.4, colors, from})` | warm film burn: memory, warmth, soft transition |
| `FX.grain(tl, {opacity=.12, fps=24})` · `FX.vignette(tl, {strength=.55})` · `FX.glow(el, {color, size})` | film texture (keep grain ≤ .14: it raises the bitrate) · corner falloff · neon/bloom on type |
| `FX.grade(tl, el, preset, {at})`, presets in `FX.grades` | `teal-orange · warm-film · cold-thriller · bleach · mono-noir · punch · faded-memory` |
| `FX.letterbox(tl, t, {ratio, bar, out})` | 2.39 bars on 16:9; thin 9 % cinema bars on 9:16 by default |
| `FX.zoomBlur(tl, from, to, t)` · `FX.rgbSplit(tl, el, t, {px=14})` | zoom-through transition (add `FX.flash`) · chromatic glitch on a beat switch |
| `FX.beatCuts(tl, scenes, times, {start, punch, flash, shake})` | photo/clip montage cut exactly on the music |

**Music-video animation pack** (full catalogue by asset type: MUSICVIDEO.md §4):
| Call | Use for |
|---|---|
| `r = FX.rig(el)` | nested wrappers `r.move > r.shake > r.punch > content` so camera moves never fight |
| `FX.handheld(tl, el, t0, t1, {amp})` · `FX.wiggle(tl, el, t0, t1, {freq, amp, rot, scale})` | handheld camera · AE-style wiggle (per-frame, CSS translate/rotate: stacks on GSAP transforms) |
| `FX.zoomIn(tl, from, to, t, {x, y})` · `FX.slideWipe(tl, from, to, t, {dir, dist})` · `FX.flip3d(tl, from, to, t, {axis})` | zoom-into-a-point transition · slight left/right push · 3D card flip (dark backdrop mid-turn) |
| `FX.wipe(tl, el, t, {dir: left·right·up·down·all·center-h·center-v·diag, mode})` | clip-path wipes; `all` = box opening from all sides |
| `FX.splatter(tl, t, {colors, zoomTarget})` · `FX.tear(tl, el, t)` | organic ink splat cover → swap → reveal · torn paper |
| `FX.dof(tl, {bg, subject, blur, at})` · `FX.parallax(tl, [{el, depth}], t0, t1, {push, pan})` | depth of field / rack focus · 2.5D multi-plane dolly |
| `FX.zoom3d(tl, el, t, {from, through})` · `FX.xyz(tl, el, t, {from, to})` | Z-axis fly-in (or through the lens) · rotate on X/Y/Z while zooming |
| `FX.popUp(tl, els, t, {stagger})` · `FX.shine(tl, el, t)` · `FX.sweepLight(tl, t, {dir})` | squash-overshoot pop · gloss sweep on an element · light beam across the frame |
| `FX.particles(tl, {type, at, from, to, x, y, count, colors})` | dust · sparks · embers · confetti · snow · bokeh · burst (canvas, per-frame) |
| `Film.onFrame(t => …)` (runtime) | your own per-frame painter (custom canvas art); must be a pure function of t |

Taste: one look per film (grade + grain + vignette); FX on *meaningful* beats (downbeats, the drop,
accents), never on every beat; velocity ramps on 2–3 moments; the drop gets the biggest combo
(zoomBlur + flash + shake + `stack:drop`), once.

---

## 5. Motion design rules

### 5.1 Easing vocabulary
| Purpose | Ease |
|---|---|
| things arriving / settling | `power3.out` (premium), `power4.out`/`expo.out` (kinetic) |
| camera moves, big travels | `power2.inOut` |
| things leaving | `power2.in` (fast exit, short) |
| ambient loops (bob, drift, breathe) | `sine.inOut` with yoyo + finite repeat |
| overshoot pops | `back.out(1.7–2.5)` |
| linear drifts (walls, bands, rotation of rings) | `none` |
Never use `linear` for arrivals, never `bounce` in premium films.

### 5.2 Timing
- Premium: reveals 0.9–1.2 s, exits 0.4–0.6 s, camera moves 2.5–4 s, holds ≥ reading time.
- Kinetic: reveals 0.35–0.6 s, staggers 0.05–0.12 s, moves 0.5–0.9 s, transitions 0.4–0.8 s.
- **Overlap** actions: the next element starts when the previous is ~60 % done. Dead air > 0.4 s
  with nothing moving feels broken (except the final hold).
- **Stagger lists** 0.4–1.3 s apart when each item has its own caption/SFX; 0.06–0.12 s for
  decorative groups.
- **Anticipation/follow-through:** big moves get a tiny counter-move or overshoot only in
  kinetic/playful personalities. Premium stays smooth.

### 5.3 Camera
The "camera" is the transform of a container: 2D (`x, y, scale` on a scene layer) or 3D
(`x, y, scale, rotationX, rotationY` on `lap.rig`/`ph.rig` inside a perspective stage).
- Orbit: rotationY ±25–40° over 3–5 s. Keep rotationX between −4° and −8° for devices (steeper
  shows too much keyboard).
- Push-in: scale 0.6 → 1.4 plus x/y to keep the target point where you want it. While pushing
  into a screen, blur/darken what's not the subject so overlay text stays readable.
- Parallax: nearer layers move 1.5–3× more than farther ones. Lifted cards at z 150–420 px give
  real parallax during a slow orbit for free.
- Never animate the same property of the rig from two overlapping tweens; chain them end-to-start.

### 5.4 3D rules
- Perspective 1600–2400 px on the stage. `transform-style: preserve-3d` on every wrapper between
  the stage and the 3D children (kit sets this for rigs/lifts).
- `filter`, `overflow:hidden`, `opacity < 1` on a 3D wrapper **flatten** its children. Apply
  blur/opacity on the stage (the root of the 3D context) or on leaf elements only.
- Backfaces: devices have back panels; flat cards seen past 90° look mirrored — keep card rotations
  within ±25°.

### 5.5 Composition
- One focal point per frame. Hero object on one third, text on the other two thirds' side.
- Text block width 30–50 % of the frame; top/left safe margin ≥ 4 % (check.mjs enforces).
- Scale contrast: headline ≥ 2.5× caption size.
- Colour contrast: text vs background ≥ 4.5:1 for captions; accent words may be lower if large.

### 5.6 Professional-editor guardrails (the tells of amateur motion)
- **Vary eases** — no more than two independent tweens with the same ease in one scene. The ease
  is the adverb: `expo.out` = confident, `sine.inOut` = dreamy, `back.out` = playful.
- **Direction rule:** `.out` for entrances, `.in` for exits, `.inOut` for moves between positions.
  (Ease-in entrances feel sluggish; ease-out exits feel reluctant.)
- **Vary speed deliberately** — the slowest move in the film is ≥ 3× the fastest. Weight: 0.15–0.3 s
  urgent · 0.3–0.5 s professional · 0.5–0.8 s luxury · 0.8–2 s cinematic.
- **Vary entry direction** — not everything from `y: 20, opacity: 0`: from the side, from scale,
  from blur, from a mask, opacity only, letter-spacing.
- **Each scene has its own stagger rhythm** and its own ambient motion (drift, slow rotation,
  scale push, colour shift, or deliberate stillness). Stillness after motion is powerful.
- **Don't start at t = 0.** The first move starts 0.1–0.3 s in.
- **Build · breathe · resolve** inside every scene: elements enter in the first ~30 %, the middle
  ~40 % holds with one ambient motion, the last ~30 % resolves or exits (exits faster than entries).
- **Choreography is hierarchy:** the first thing to move is read as most important — stagger by
  importance, not DOM order; overlap entries; decorative group staggers total < 0.5 s.
- **Asymmetry:** entrances longer than exits (a card appears in 0.5 s, leaves in 0.3 s).
- **One transform owner per element at a time.** An entrance `y` and a Ken-Burns `scale` on the
  same element at once kill each other — combine them in one `fromTo`, or put the entrance on a
  wrapper and the drift on the child.
- **Ambient loops live on the timeline** (`MK.drift/hover/breathe`, finite repeats) — a bare
  `gsap.to` outside `tl` never renders.
- **Match velocity across cuts:** exit with an accelerating ease + blur ramp, enter with a
  decelerating ease + blur clear, so the fastest moments meet at the swap.

### 5.7 Video is not a web page
- **Scale up:** headlines 64–130 px, body 28–42 px, labels ≥ 20 px at 1080p (in-feed/phone
  viewing: headlines ≥ 90, body ≥ 32). Borders 2–4 px, decorative opacity 12–25 % (under 10 % is
  invisible after compression), padding 60–140 px.
- **Layers:** a produced frame has a background treatment, midground content and foreground
  accents. Premium/minimal briefs deliberately keep space — "breathing room" is then the design,
  but the background is still *treated* (gradient void, glow, soft shadow), never flat `#000`/`#fff`.
- **Two focal points** where the brief allows (hero + caption), anchored to edges or thirds, not a
  lone centred block — except deliberate solemn moments (hook line, end card).
- **Colour presence:** at least one colour that pulls the eye per scene; tint neutrals toward the
  brand hue; brand accent at full saturation on focal elements.
- **Banding:** large full-frame linear gradients on dark backgrounds band under H.264. Prefer radial
  gradients / solid + glow, or add a static 2 % noise overlay (a small tiled PNG) to dither.
- **Images always move:** perspective tilt, slow push (scale 1 → 1.04 over the beat), device frame,
  or a floating extract at another depth. A raw flat image looks unfinished.
- **Every line or connector earns its place:** it starts at a real element, ends at one, and
  reveals/routes/emphasises something. Otherwise cut it.
- **AI design tells to avoid unless the brief asks:** gradient text everywhere, identical card
  grids, cyan-on-dark neon, everything centred with equal weight, the same font everyone uses.

---

## 6. Recipes (copy, then adapt ids/times)

### 6.1 Floating laptop: rise, orbit, push-in, screen change
```js
const lap = MK.laptop("#stage", { shadow: "rgba(112,72,62,.5)" });
lap.screen.innerHTML = `<div class="scr" id="scrHero"><img src="assets/hero_screen.png"></div>
  <div class="scr" id="scrNext" style="clip-path:inset(0 0 0 100%)"> …rebuilt UI… </div>`;
tl.set(lap.rig, { x: 300, y: 900, scale: .58, rotationX: -6, rotationY: -40 }, 0);
tl.to(lap.rig, { y: 110, duration: 2.6, ease: "power3.out" }, 3.2);            // rise
tl.to(lap.rig, { rotationY: -9, duration: 3.2, ease: "power2.out" }, 3.2);      // orbit to front
tl.fromTo(lap.floor, { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 1.8, ease: "power3.out" }, 4.3);
MK.hover(tl, lap.bob, 5.4, 30);
MK.gloss(tl, lap.glossBar, 4.9);
tl.to(lap.rig, { x: -150, y: 390, scale: 1.42, rotationX: -5, rotationY: -1, duration: 3, ease: "power2.inOut" }, 7.0); // push-in
tl.to("#scrNext", { clipPath: "inset(0 0 0 0%)", duration: .9, ease: "power2.inOut" }, 10.0); // wipe to next screen
```
Screen image size: crop at 2× the screen box (e.g. 2300×1344 for 1150×672) when you can.
Push-in with overlay text: add a second copy of the screen image blurred with a radial mask
that keeps only the focus region sharp, and fade it in during the push:
```css
#heroBlur{filter:blur(9px) brightness(.6);background:url(assets/hero_screen.png) 0 0/100% 100%;
  -webkit-mask-image:radial-gradient(28% 44% at 75% 59%,transparent 45%,#000 100%);mask-image:radial-gradient(28% 44% at 75% 59%,transparent 45%,#000 100%)}
```

### 6.2 UI cards peel off the screen and return
Rebuild the card in HTML twice: once inside the screen (`#s1`, the slot) and once inside
`lap.lifts` at the same coordinates (`#L1`, class `lift`, starts hidden).
```js
MK.lift(tl, "#L1", 10.95, { z: 230, x: -150, y: -40, rotationY: -10, rotationX: 4, scale: 1.04 }, { ghost: "#s1" });
tl.to("#L1", { y: -52, duration: 3.6, ease: "sine.inOut" }, 12.05);   // hang in depth (parallax float)
MK.settle(tl, "#L1", 20.9, { ghosts: "#s1" });                         // glide back
```
Lift toward the camera and **away from the caption side**. Different z per card (150/250/350).

### 6.3 Floating glass UI assembly
```js
const parts = ["#g1", "#g2", "#g3", "#g4"];          // .glass panels in their FINAL layout
parts.forEach((p, i) => tl.fromTo(p,
  { opacity: 0, z: -600 + i * 120, x: (i % 2 ? 1 : -1) * 420, y: 200 - i * 90, rotationY: (i % 2 ? -1 : 1) * 30, rotationX: 12 },
  { opacity: 1, z: 0, x: 0, y: 0, rotationY: 0, rotationX: 0, duration: 1.1, ease: "power3.out" }, t + i * 0.18));
// container of the panels: perspective:1800px on its parent, transform-style:preserve-3d on itself
```
Glass = class `glass` (light) or `glass-dark`. Keep text inside panels ≥ 22 px at 1080p.

### 6.4 Chart line draws on (no fake numbers)
```html
<svg width="700" height="380"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#E3B34A" stop-opacity=".3"/><stop offset="1" stop-color="#E3B34A" stop-opacity="0"/></linearGradient>
  <clipPath id="ac"><rect id="acr" width="0" height="380"/></clipPath></defs>
  <path clip-path="url(#ac)" fill="url(#area)" d="M28 300 C 120 262 … L 672 350 L 28 350 Z"/>
  <path id="line" fill="none" stroke="#E3B34A" stroke-width="3.2" stroke-linecap="round"
        style="filter:drop-shadow(0 0 6px rgba(227,179,74,.8))" d="M28 300 C 120 262 …"/></svg>
```
```js
MK.lineDraw(tl, "#line", 22.0, { dur: 1.7 });
tl.fromTo("#acr", { attr: { width: 0 } }, { attr: { width: 700 }, duration: 1.7, ease: "power2.inOut" }, 22.0);
```
Gridlines faint (5 % white), no axis labels, no values. Panels use skeleton bars
(`<div class="sk">` 9 px tall, 8 % white) instead of invented text.

### 6.5 Logo lockup resolve (end card)
```html
<div id="bloom"></div>   <!-- radial brand-colour glow, 1100px circle, centred -->
<div id="lockup" style="position:absolute;left:0;right:0;top:470px;display:flex;align-items:center;justify-content:center;gap:34px;opacity:0">
  <img src="assets/logo.png" style="height:116px"><div class="wordmark">AASTHI</div></div>
<div class="t" id="tag" style="left:0;right:0;top:636px;text-align:center">India's private markets. From anywhere.</div>
```
```js
tl.fromTo("#bloom", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .7, ease: "power3.out" }, T);
tl.fromTo("#lockup", { opacity: 0, filter: "blur(16px)", scale: .94 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: .55, ease: "power3.out" }, T + .1);
MK.fadeIn(tl, "#tag", T + .5, { dur: .5 });
MK.breathe(tl, "#bloom", T + .8, DURATION);   // the only thing moving in the hold
```
Logo: always the user's file (keyed to transparent with `prep_image.py key`), never redrawn.
Wordmark: the brand name in the font closest to the logo lettering, tracked +.04–.08em.

### 6.6 Phone rotating between aspect ratios
```js
const ph = MK.phone("#stage", { w: 440, h: 900 });
ph.screen.innerHTML = `
  <div class="scr" id="portrait" style="position:absolute;inset:0"> …9:16 content… </div>
  <div id="landscape" style="position:absolute;left:50%;top:50%;width:${900-32}px;height:${440-32}px;
       margin-left:${-(900-32)/2}px;margin-top:${-(440-32)/2}px;transform:rotate(90deg);opacity:0"> …16:9 content… </div>`;
tl.set(ph.rig, { rotationX: -4 }, 0);
tl.to(ph.phone, { rotationZ: -90, duration: 1.0, ease: "power3.inOut" }, T);   // turn landscape
tl.to("#portrait", { opacity: 0, duration: .3 }, T + .35);
tl.to("#landscape", { opacity: 1, duration: .3 }, T + .45);
```
(`#landscape` has a static CSS rotate and is never tweened for transform — only opacity.)

### 6.7 Statement stack (block-wipe lines + overshoot last line)
```html
<div class="stack" style="position:absolute;left:150px;top:190px;display:flex;flex-direction:column;align-items:flex-start">
  <div class="t" id="k1">Because</div><div class="t" id="k2">great</div><div class="t" id="k3">captions</div>
  <div class="t" id="k4" style="color:var(--lime);font-weight:800">what they say</div></div>
```
```js
["#k1","#k2","#k3"].forEach((s, i) => MK.blockWipe(tl, s, T + i * .45, { color: "#F4EFE3", dur: .6 }));
MK.popIn(tl, "#k4", T + 1.5, { from: .5 });
```
`.stack .t{position:relative}` so the lines stack. A bouncing dot between lines: a small circle
tweened `y` to each line's top with `ease:"power2.out"` and `back.out` on landing.

### 6.8 Rosette rolls in and becomes a bullet
```js
const r = MK.rosette("#bulletHost", { size: 90 });            // host = zero-size div left of the text
tl.fromTo(r, { x: -700, rotation: 0, opacity: 0 }, { x: 0, rotation: 420, opacity: 1, duration: 1.1, ease: "power3.out" }, T);
const end = MK.typewriter(tl, "#line", T + .9, { cps: 18 });   // text types beside it
MK.highlight(tl, "#landWord", end + .1, { bg: "linear-gradient(90deg,#C7F36B,#10B981)" });
```

### 6.9 Glowing tube threading through blocks
Draw the tube in **two SVG layers** with the same path: one below the blocks, one above. Clip the
upper copy to the segments where the tube passes in front (`<clipPath>` rects), so it weaves.
```js
const back = MK.tube("#tubeBack", D, { width: 12 }), front = MK.tube("#tubeFront", D, { width: 12 });
// #tubeFront has style="clip-path:url(#frontSegments)" defined in its <defs>
MK.tubeDraw(tl, back, T, 2.2); MK.tubeDraw(tl, front, T, 2.2);
```

### 6.10 Pill → ring with a spark
```html
<div id="pill" style="position:absolute;left:830px;top:500px;width:260px;height:80px;border-radius:40px;background:#C7F36B;opacity:0"></div>
<div id="sparks" style="position:absolute;left:960px;top:540px;width:0;height:0"></div>
```
```js
tl.fromTo("#pill", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .4, ease: "back.out(2)" }, T);
tl.to("#pill", { width: 160, height: 160, left: 880, top: 460, borderRadius: 80, backgroundColor: "rgba(199,243,107,0)",
  boxShadow: "inset 0 0 0 10px #C7F36B", duration: .6, ease: "power3.inOut" }, T + .6);
const host = document.querySelector("#sparks");
for (let i = 0; i < 8; i++) {                     // spark burst when the ring closes
  const d = document.createElement("div");
  d.style.cssText = "position:absolute;width:10px;height:10px;margin:-5px;border-radius:50%;background:#F4EFE3;opacity:0";
  host.appendChild(d);
  const a = (i / 8) * Math.PI * 2;
  tl.fromTo(d, { x: 0, y: 0, opacity: 1, scale: 1 }, { x: Math.cos(a) * 140, y: Math.sin(a) * 140, opacity: 0, scale: .3, duration: .6, ease: "power3.out" }, T + 1.15);
}
tl.fromTo("#pill", { scale: 1 }, { scale: 1.12, duration: .18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, T + 1.15);
```

### 6.11 Rotating square releases a shape
```js
tl.fromTo("#sq", { opacity: 0, rotation: 0, scale: .4 }, { opacity: 1, rotation: 135, scale: 1, duration: .9, ease: "power3.out" }, T);
tl.to("#sq", { rotation: 225, scale: .2, opacity: 0, duration: .5, ease: "power3.in" }, T + 1.0);
tl.fromTo(rosetteEl, { scale: 0, rotation: -90, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: .7, ease: "back.out(2)" }, T + 1.1);
tl.to(rosetteEl, { x: 520, y: -140, rotation: 360, duration: 1.2, ease: "power2.inOut" }, T + 1.9);  // travels to its next role
```
`#sq` and the rosette share the same centre (zero-size host div at the centre point).

### 6.12 Ribbon weaving behind and in front of an inset (footage, card, phone)
Same two-layer trick as 6.9: ribbon SVG A **under** the inset, ribbon SVG B **over** it with a
clip-path that keeps only the stretches where it crosses in front. Draw both with the same
`MK.lineDraw` timing; a thick stroke (40–70 px) with a two-stop gradient and round caps reads as a
ribbon. Add `swoosh` SFX at the draw start.

### 6.13 Screen content in HTML (rebuilt UI)
Build UI at the device's screen size (e.g. 1150×672) with real fonts, exact copy from the ref,
the ref's colours/radii/shadows. Nav bars and photos can be image crops; everything that will be
lifted or animated must be real DOM.

---

### 6.14 Scene shapes (proven whole-scene patterns — pick one per beat)
| Shape | What happens | Build with |
|---|---|---|
| **Kinetic type beats** | the words *are* the motion: a line swaps words in place, or a statement builds line by line to a pop payoff | `blockWipe`/`maskRise`/`popIn`, hard cuts on the beat |
| **Typewriter reveal** | a caret types (and edits) a line, then it collapses into the brand | `typewriter` + `blurOut` + logo lockup |
| **Device showcase** | one device held as hero while its screens change through a real flow | `laptop`/`phone` rig + screen wipes + `lift` |
| **Camera journey** | the camera travels through one continuous world: dive in → something happens → travel to the consequence | rig/stage tweens (push, orbit, pan) with `power2.inOut` legs |
| **Zoom-out reveal** | open tight on a detail, one long decelerating pull-back reveals the whole | stage `scale` 3 → 1, `expo.out`, 2.5–4 s |
| **Grid / list assemble** | N items cascade into a grid or list and hold | stagger `fromTo` (0.06–0.1 s), `glass` cards |
| **Constellation / hub** | nodes spring into a ring around a centre, the camera pushes in on the core | `arcText`/positioned nodes + `popIn` + stage push |
| **Comparison split** | two equal items enter from opposite sides with mirrored tilts, badges pop | mirrored `fromTo` rotationY ±18 + `popIn` |
| **Fixed anchor, cycling** | one element never moves while the words/themes around it cycle | pinned element + `karaoke`/hard-cut swaps |
| **Takeover** | a cycling word is shoved aside by the hero crashing in | `x` crash with `power4.out` + displaced text `x` |
| **Prompt → answer** | a prompt types into an input, the product answers | `typewriter` + streaming lines (`fadeIn` stagger) |
| **Data hero** | one real number/chart carries the beat | `lineDraw` chart / count only with real data |
| **Title card** | one line or card, one restrained move, then stillness | `blurIn` or `maskRise`, hold |
| **Logo lockup** | the mark comes to exist: assembles, draws on, or blooms, then holds | recipe 6.5 (+ `lineDraw` outline, `breathe`) |

### 6.15 Ikigai editorial type (ref: "ikigai" edit — serif words + a circle over one word)
Off-white paper #EDECE8, EB Garamond ("Gara", bundled) 80–150 px lowercase, ink #2B2B2B, one accent
(#F26B1D). Words fade in on the voice; the circle pops onto the key word (r ≈ 0.8 × size) and later
glides to the next key word or shrinks to 0. Partial cover of a long word is the look. Pair with a
tiny two-line tag bottom-left (`<b>E</b>xp 000 · the race`, first letter in the accent).
```js
ED.ik(tl, "#ik1", { x: 170, y: 400, size: 96, words: [["everyone", T(3,5)], ["ran", T(3,5)+.15], ["after", T(3,7)], ["marks.", T(3,6), "font-style:italic"]],
  kfs: [{ t: T(3,6), i: 3, r: 90 }, { t: T(3,9) - .1, i: 3, r: 0, dur: .25 }] });
ED.ik(tl, "#ik2", { x: 170, y: 520, size: 96, circle: "#F26B1D", words: [["— i ran after", T(3,9)], ["AI.", T(3,10), "font-style:italic"]], kfs: [{ t: T(3,10), i: 1, r: 72 }] });
```
Venn "intersection" payoff: 4 SVG circles (r 210, centres ±100 px) drawn with `strokeDashoffset`, one
per spoken word, labels fade in; a filled centre circle pops on the key word with the answer ("AI")
inverted inside; then the centre scales ×14 to fill the frame = the transition to the next scene.

### 6.16 Illustrated characters with the dot print (Open Peeps → dotify)
The accepted "character" look: clean hand-drawn Open Peeps (CC0) in 2–3 flat colours, re-printed as
square dots (`tools/dotify.py`), on paper with thin grey line-art sets (Zippet reference). Recipe:
1. `node tools/peeps/setup.cjs` once (already done on this machine). Spec the hero with a head, beard,
   accessory and skin that echo the person's photo (e.g. `Pomp` quiff + `FullMedium` beard +
   `Sunglasses`) and ONE outfit colour for all poses (green top, orange laptop). Poses: busts
   `Computer` `Explaining` `PointingUp` `TeeArmsCrossed`; full body `kind:"stand"`: `RestingColorPants`
   (+ `back:true` = back shot), `WalkingColorTee`, `Dancer` (= jump); extras with other heads, skins
   and tops for crowds.
2. `node tools/peeps/peeps.cjs spec.json svg/` → `node tools/peeps/rasterize.mjs svg/ png/ 1200`.
3. `python tools/dotify.py png/x.png assets/x_dots.png --cell 5..7 [--paper #EDECE8]` (cell from the
   display size; `--paper` when line-art must not show through the dots).
4. Animate as flat puppets: rise-in with back.out, `ED.walk`, `ED.jump`, pose swaps with a 0.25 s
   scaleY squash (from .94), breathing scaleY 1.012 yoyo. The Computer bust's laptop carries a swirl
   logo — cover it with a brand sticker.
Icons in the same world: draw flat SVG icons (robot, clapper, megaphone, burst, flask, bulb, rocket)
in the palette, rasterise, dotify, and put them on rounded cards (#F7F6F2 / green / orange) with a
soft shadow.

### 6.17 Push through the screen into a dark world (Zippet "push back" reveal)
A room layer (paper, line-art, the character at a laptop) and a dark layer (#4B3F3E) clipped to
`circle(0)` at the laptop screen. `ED.pushThrough(tl, "#room", "#dw", screenX, screenY, t)` scales the
room ×7 into the screen while the dark world opens from the same point. Inside: white rounded dashes
drift up, cards fly in from below one per spoken word (back.out 1.5, rotation ±40° → ±5°), the
character points; on the summary word the cards gather into a stack and a centred `ED.ik` line lands
("all with AI."). Put the music DROP on the push — it is the biggest moment of the film.

### 6.18 Concept beats with characters (show the idea, don't label it)
- "I joined X": full-body BACK shot of the hero at a line-drawn gate/door; the doors swing open on the
  verb; he walks in (bob + scale .72) and the camera pushes through the gate.
- "Everyone did A, I did B": a crowd walks one way into a building labelled A (building layer ABOVE
  the walkers so they disappear into it); the hero stops, a glowing orb/door for B opens on the other
  side, he jumps out of the crowd into it (`ED.jump`), the orb pulses, 10 px shake. Never rotate an
  orb that carries text.
- "I learned / mentored / now do everything": pose swaps on one set (typing → explaining with 4
  student busts rising and nodding on the verb) → push through the screen.

### 6.19 Collage opening → illustrated middle (mixed-style films)
A photo-collage cold open (torn edges, halftone prints, rubber stamps, paper boil) can hand over to a
calmer illustrated/editorial world with `ED.tear` on the first word of the new section. Keep one
through-line (the accent colour, the paper texture at 6–13 % multiply, the grain) so it reads as one
film. Lower texture and grain in the clean world (texture .06, grain .12); restore them if the last
beat returns to collage.

## 7. Editing knowledge

- **Continuous vs cut.** Premium films avoid hard cuts: connect scenes by moving *through*
  something (push into a screen, whip, blob wipe, fade through black). Kinetic films cut hard on
  the beat; use a cut when the energy must jump.
- **Match cut:** end a scene on a shape/position, start the next with a similar shape in the same
  place (rosette → bullet, pill → ring, screen → full frame).
- **Transition inventory per film:** 2–4 kinds, repeated. Using every transition once looks cheap.
- **Transitions carry meaning:** crossfade = "this continues" · hard cut = "wake up", disruption,
  register shift · slow dissolve = "drift with me" · push/whip = travel · iris/zoom = focus on one
  thing. Spend the biggest transition on the centrepiece (the hero reveal, the logo); connective
  beats get quiet ones. A 5–7 beat brand film wants 1–2 showpiece transitions, not more.
- **Declare the rhythm** before building (e.g. `fast-fast-SLOW-fast-WHIP-hold`) and check the
  draft against it.
- **Pacing curve:** calm hook → energy rises through the proof beats → one peak (whip / biggest
  move) around 50–65 % → slows into trust → still end card.
- **Beat grid:** with a pulse, place reveals on beats (`t = start + n × 60/bpm`). Transitions start
  half a beat early so the swap lands on the beat.
- **J/L audio:** the score's chord change or riser starts 0.3–1.0 s *before* the visual section
  change; the chime lands *on* the logo frame.
- **Breathing room:** after a dense scene, give 0.5–1 s of calmer motion. The end card holds ≥ 1.5 s.
- **Eye trace:** the next thing appears where the eye already is (near the last element or along
  the motion direction). Don't make the viewer search.
- **Safe zones:** 16:9 keep text inside 4 % margins; 9:16 keep text out of the top 12 % and bottom
  20 % (platform UI), and captions in the middle band.

---

## 8. Typography craft

### 8.1 Fonts bundled (`engine/fonts.css`, latin)
Cormorant Garamond 500/600 (+500 italic) · Instrument Serif 400 (+italic) · Fraunces 400/600/800
(+italic) · Playfair Display 400/600/800 (+italic) · DM Serif Display 400 (+italic) · Inter
400–800 · Manrope 400/600/800 · Plus Jakarta Sans 400/600/800 · Space Grotesk 400/500/700 ·
JetBrains Mono 400/700. Need another? `npm i @fontsource/<name>` and copy the woff2 + add an
`@font-face` in the film's `<style>`. `check.mjs` warns on any font without a face.

### 8.2 Setting
- Serif display lowercase: letter-spacing −.012em, leading 1.02–1.08, weight 500.
- Sans display: 700–800, letter-spacing −.02 to −.035em.
- Captions/eyebrows: 500–600, letter-spacing .12–.2em, never below 22 px at 1080p.
- One line per idea: use `<span class="ln">` blocks for deliberate line breaks; never `<br>`.
- Widths: set `width` on headline blocks so wrapping is intentional; check wraps in snapshots.

### 8.3 Text over busy backgrounds
Scrim (radial dark gradient behind the text), background blur (DOF copy like 6.1), move the text
beside the subject, or darken the whole studio (`bgLight` opacity down). Text shadow alone is not
enough.

### 8.4 Layout grid (1920×1080)
Margins 120–150 px left/right, 90 px top/bottom. Columns: text column x 140–820 when the hero is
right; hero column x 900–1800. Centred lines: `left:0;right:0;text-align:center` with max ~1400 px
of text (use padding on the element: `left:260px;right:260px`).

---

## 9. Assets

```bash
python3 $SKILL/tools/prep_image.py probe  ref.png row=150          # find screen edges (brightness jumps)
python3 $SKILL/tools/prep_image.py crop   ref.png assets/hero.png 327 127 1130 596 --scale 2 --sharpen
python3 $SKILL/tools/prep_image.py unwarp ref.png assets/scr.png 292,90 948,112 1022,540 330,555 --size 1600x940
python3 $SKILL/tools/prep_image.py key    logo.png assets/logo.png --bg auto --tol 60
python3 $SKILL/tools/prep_image.py palette ref.png --n 6
FPS=30 $SKILL/tools/prep_video.sh footage.mp4 assets/clip          # image sequence
```
- Always `Read` (view) a prepared image once before using it.
- Screens: keep the crop's aspect ratio equal to the device screen box (1150×672 = 1.711).
- Logos: key to transparent, keep the original proportions (set only height in CSS).
- Footage of people: only if the user supplies it; never generate or fake people.
- Editing real footage (short-form: cuts, captions, cut-outs, mix): follow `SHORTFORM.md` and its
  toolkit `tools/shortform/sf.py`. Long-form / multi-cam / NLE projects: `LONGFORM.md` + `CONNECTORS.md`.
- Overlays for an NLE (lower thirds, cards, captions over footage): `render.mjs --alpha` → ProRes 4444
  with alpha; mark full-frame background layers `data-alpha-hide`.

Free-asset sourcing (log every file; credit CC BY / CC BY-SA in the caption):
```bash
python3 $SKILL/tools/commons.py search "chess knight piece" 8            # Wikimedia Commons images
python3 $SKILL/tools/commons.py get "File:X.jpg" assets/raw/x.jpg 1600   # → appends assets/CREDITS.txt
python3 $SKILL/tools/commons.py search "paper tearing" 8 --audio         # audio: fetch with `original`
python3 $SKILL/tools/commons.py original "File:Y.ogg" assets/sfx/y.ogg
python3 $SKILL/tools/mixkit.py list free-sound-effects/whoosh/            # Mixkit SFX / music (free licence, no credit)
python3 $SKILL/tools/mixkit.py get free-sound-effects/transition/ "Movie trailer whoosh hit" assets/sfx/whoosh_hit.mp3
node $SKILL/tools/peeps/peeps.cjs spec.json svg/                           # characters (§6.16)
node $SKILL/tools/peeps/rasterize.mjs svg/ png/ 1200
python3 $SKILL/tools/dotify.py png/x.png assets/x_dots.png --cell 6 --paper "#EDECE8"   # dot print
```
- Object cut-outs: `rembg` session `isnet-general-use`, crop to bbox, then duotone / halftone / paper
  sticker edge (reference implementation: `personal/content/santhosh-intro/tools/look.py` —
  `duotone`, `halftone`, `paper_card`, `sticker`).
- One small photo of a person (even 200 px) is enough for a collage cut-out if it is printed
  (halftone, paper edge, shown mid-size). Don't repeat the real face all film long: use a matching
  illustrated character for the rest, and don't end on the photo unless asked.
- Real brand/company logos: don't — they read as endorsement; use drawn icons.

---

## 10. Audio

**Pro sound pass → SOUND.md** (sounds fetched per film from the internet by `audio/source.py`, roles, anchors: hit transient / whoosh
peak / riser end on the frame, layering, −14 LUFS mix). Kit call times below are your spotting list.

1. **Music** (MUSIC.md): write the music brief, choose a track, `music.py analyse` (read the sheet),
   `music.py fit --duration <film> --drop-at <reveal>` → `assets/music_fit.wav` + `music_fit.beats.js`.
   Load the beats file in the page and time cuts/effects from `FX.grid()` (§4 FX kit).
2. **SFX** (SOUND.md): cues from the Build Sheet, timed by the kit's returned times (`MK.karaoke` word
   times → `role:click`, `MK.glitchIn` ticks → `stack:glitch`, whip swap → `stack:cut`/`stack:whoosh_hit`,
   logo → `stack:reveal` + `stack:ding`, drop → `stack:drop`). Use stacks for anything that must feel big.
3. **Voice:** `audio/tts_vo.py` (temp VO with a word clock) or the real VO; `align_vo.py vo.m4a --asr` →
   phrase list to re-time captions.
4. `mix.json` (`voice`, `music`, `sfx`) → `python3 $SKILL/audio/mixdown.py mix.json assets/mix.wav`;
   then look at `sfx_lib.py spec assets/mix.wav --marks <cut times>`.
5. Set `data-audio` on the root; the renderer muxes it (trimmed to duration). Target loudness for
   web/social ≈ −14 LUFS (`ffmpeg -i out.mp4 -af ebur128 -f null -` to measure).

### 10.2 Voice-first films from real audio (tested: santhosh-intro)
1. **Voice**: `python3 $SKILL/audio/tts_vo.py lines.txt assets/vo --voice te-IN-MohanNeural --tempo 1.14`
   gives a temporary TTS voice with word timings (Tenglish → Telugu voice, Telugu in Telugu script;
   English voices skip Telugu). It prints the word-index map; build the whole timeline on
   `T(line, k)`. When the real voice arrives, align it to the same lines and every cut re-times.
2. **Music**: a free-licence track (Mixkit) whose **drop** lands on the biggest reveal. Find the drop =
   the biggest jump of the 50 ms RMS in dB after smoothing (Mixkit "Thunder": 20.15 s).
3. **Mix**: `python3 $SKILL/audio/mixdown.py mix.json assets/mix.wav` — voice on top, music
   side-chained −10 dB under it, `pre_gain` lifts quiet builds, SFX `[t, file, gain, pan]` on every
   cut: whoosh on wipes/iris, trailer hit on the key word, pop on each card/circle, metal hit on a
   strike-through, sparkle on a magic reveal, paper rustle/crumple in collage parts. Verify: transcribe
   the mix with faster-whisper (the voice must survive) and measure ≈ −14 LUFS.
4. **Trending songs**: never bake copyrighted trending audio into the MP4 (it gets muted / loses
   reach). Deliver with free music and tell the user to add the trending sound inside the app at
   upload, voice kept loud.

---

## 11. QA

### 11.1 `check.mjs` ERRORs → must fix
Math.random / clocks / repeat:-1 / play() / fetch → replace with kit equivalents. External URL →
download to assets. Missing file / script error → fix path or code. No `Film.build` / no
`data-duration` → fix the root.

### 11.1b What check.mjs measures (so you know what "clean" means)
Static: determinism bans, external URLs, CSS animations/transitions, fonts without faces.
Runtime (every 0.2 s): script errors, missing files, timeline length, every `.t` text box —
outside the 4 % safe area, overlapping another text, overlapping a **protected element**
(`data-clear`), and too short to read. Pixel pass: each caption's **contrast** against what is
actually behind it (text hidden, background measured), **busy backgrounds** (texture behind text),
**near-empty frames** (≥ 1 s of flat colour mid-film) and **harsh flashes** (≥ 75 % of the frame
brightening > 20 % within 0.1 s). `--fast` skips the pixel pass; `--strict` fails on warnings.

**Mark what text must never cover** with `data-clear="name"`: device screens being showcased,
the logo, faces in footage, the product photo. Example: `<div class="mk-screen" data-clear="screen">`
or on a kit element after building: `lap.screen.dataset.clear = "screen"`.

**Definition of done:** `check.mjs --strict` passes, or every remaining warning is listed in the
delivery note with the reason it is intentional.

### 11.2 Warnings → judge
- *outside safe area* → move text in (unless it's intentionally full-bleed decoration; then drop
  its `t` class).
- *overlapping text* → real problem unless one is a dimmed list item designed to sit behind.
- *readable for only Xs* → lengthen the hold, shorten the copy, or reveal faster.
- *timeline runs past the end* → shorten the last tweens (an ambient loop is fine).
- *font has no @font-face* → add the face or switch to a bundled font.
- *low contrast* → darker/lighter text, a scrim behind it, or move it to a calmer area.
- *busy background* → blur/darken the region behind (DOF copy, recipe 6.1), a soft scrim, or move.
- *overlaps protected element* → move the text beside the element; never over a showcased screen.
- *near-empty frame* → something should be moving or visible; tighten the gap or fill it.
- *harsh brightness jump* → ease background changes over ≥ 0.4 s or cover them with a wipe.

### 11.3 Visual checklist (on the contact sheet)
- [ ] Every headline complete, spelled right, not clipped, not over busy content.
- [ ] No element accidentally stretched (a CSS rule hitting the wrong `img` is common).
- [ ] Device angle believable (keyboard not dominating; lid not flipped).
- [ ] Lifted cards in front of the device, not clipped by the screen.
- [ ] Transitions mid-frame look intentional (streaks cover the swap; no bare frame).
- [ ] Palette consistent; one accent per scene.
- [ ] End frame: logo sharp and centred, tagline readable, nothing else moving.

### 11.4 Known pitfalls → fixes (learned in production)
| Symptom | Cause | Fix |
|---|---|---|
| Image stretched to full screen height | generic `.scr img{height:100%}` also hits a nav/logo img | give special imgs a more specific selector (`.scr img.nav{height:63px}`) |
| Laptop looks like a giant keyboard | rig rotationX too steep / perspective-origin too high | rotationX −5…−8, perspective-origin `50% 56%` |
| Karaoke pill/highlight invisible | span without `display:block` ignores width/height | kit CSS already fixes; for custom pills use block elements |
| 3D band huge / flat strip | ring centred at the camera plane | kit `MK.band` pushes the ring back by its radius; keep radius ≤ 900 |
| Element "jumps" at a random time when scrubbing | two `fromTo` on the same element/property | one reveal per element; later changes use `to` |
| Headline text sits over the screen's own headline | push-in framing | blur/darken the screen except the focus region, or move the text |
| Captions from two scenes overlap | missing exit or `data-out` | every caption gets an exit; scene layers get `data-in/out` |
| Fonts look like Times/Arial | font not loaded | bundled font or local @font-face; check warns |
| Footage frozen/black | H.264 `<video>` in Chromium | `prep_video.sh` → image sequence or webm |
| Element never appears / sits off-screen | entrance tween and another transform tween on the same element overlap | one `fromTo` for both, or wrapper (entrance) + child (drift) |
| Ambient glow/float missing in render | loop created with bare `gsap.to` outside `tl` | put it on `tl` (`MK.breathe/drift/hover`) |
| Dark→light scene change reads as a flash | background opacity switched with `tl.set` | fade it over ≥ 0.4 s or hide the switch under a wipe/whip |
| Render slower than expected | heavy `filter: blur()` on big layers every frame | blur smaller elements, use pre-blurred images, lower `--workers` if RAM-bound |
| Dotted character looks see-through (bars/lines show through) | dot gaps are transparent | `dotify.py --paper "#EDECE8"` (paper fill inside the silhouette) |
| Text on a spinning orb/badge reads upside down | rotation tween on an element that carries text | pulse/bob it instead; rotate only a ring without text |
| Pose/variant leaks into another scene | a child set to `visibility:visible` inside a scene hidden by `data-out` | swap variants with `opacity`, never `visibility` |
| Text set with `tl.set(el,{innerHTML})` / `textContent` doesn't revert when scrubbing | GSAP can't restore DOM text | stack the variants and switch opacity, or compute from `tl.time()` in an onUpdate |
| A later `fromTo` (yoyo/repeat) breaks an element's entrance | immediateRender of the later fromTo | `immediateRender:false` on every later `fromTo` of an already-animated element |
| Caption words appear out of reading order | code-mixed VO (Telugu order ≠ English caption order) | reveal caption words in reading order on the nearest spoken word |
| "The command line is too long" (Windows) | 150+ paths passed to a CLI | call the tool's JS API from a script (see tools/peeps/setup.cjs) |
| Python print crashes on Telugu (`charmap codec`) | Windows console encoding | `PYTHONIOENCODING=utf-8` |
| ffmpeg "Access is denied" / ENOENT | `FFMPEG` env points to a folder | fixed: render.mjs and audio/ffbin.py resolve folder → ffmpeg.exe, else PATH, else imageio-ffmpeg |
| Circle / highlight lands off its word | text measured before the webfont loaded (layout in the fallback font) | ED kit pre-loads Gara and re-measures once fonts are loaded; for custom measuring, `document.fonts.load()` the face before `Film.build` |
| Whole style rejected ("looks coded") after a full build | generic flat vector shapes drawn from scratch | stop; show 3–4 still style frames built from a real illustration library + the user's refs; rebuild only after "go" (DIRECTOR §13) |

---

## 12. Render and deliver

```bash
node $SKILL/bin/render.mjs films/<name> --out films/<name>/out/<name>.mp4 [--workers 4] [--crf 17]
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact films/<name>/out/<name>.mp4
ffmpeg -v error -y -i films/<name>/out/<name>.mp4 -vf "select='not(mod(n\,150))',scale=480:-1,tile=3x2" -frames:v 1 strip.jpg
```
Other formats: set `data-width/height` (1080×1920 for 9:16, 1080×1080 for 1:1) and re-layout —
never scale a 16:9 layout into 9:16. `--from/--to` renders a section for quick fixes.
Deliver: the MP4 path, duration, resolution, and a one-paragraph summary of what's in each beat
plus any deviations from the brief (and why).

---

## 12.5 Review loop (where the user sees the work)

| Pass | Collaborative | Autonomous |
|---|---|---|
| Concept (DIRECTOR §4) | show 5 pitches, wait | pick, state choice + the typical one left behind |
| Storyboard (DIRECTOR §10) | frame table, wait; optional sketch sheet (`--at scenes` on the static layout), wait | post both, continue |
| Build | revise only the frames named in feedback | — |
| Final look | show contact sheet (+ draft MP4), ask "render, or what changes?" | show contact sheet with the delivery |

Render is the expensive, final step: in collaborative runs render only after the final-look
answer. Every delivery reports the real duration, resolution, the contact sheet and any
deviations from the brief.

## 13. Cost-aware mode (smaller / cheaper models — same quality bar)

If you are a smaller or local model: follow this section to the letter. Your job is not to be
inventive in code — it is to assemble proven parts precisely and verify them. The quality lives in
the kit, the recipes, `EXAMPLES.md` and the QA loop.


Quality comes from the kit, the recipes and the QA loop — not from improvising. A smaller model
gets the same result by following the path exactly:

1. **Never write an effect the kit already has.** Look it up in §4 / §6 first. Copy recipes
   verbatim, then change ids, times, colours, copy.
2. **Start from `template/index.html`** (or `template/shortform.html`). Copy its structure; don't
   redesign the layer stack.
3. **Work from the Build Sheet row by row.** One kit call per row. Keep the scene comments.
4. **Static layout → snapshot → then animate.** Most visual bugs are layout bugs; catch them
   with one snapshot before writing the timeline.
5. **Budget your checks:** `check.mjs` after every scene block you add (fast); snapshots only at
   hold midpoints; `--draft` once; the full render once at the end.
6. **Edit surgically:** change the specific lines (targeted replacements), don't regenerate the
   file. Don't re-read large files you just wrote; re-read only the part you are fixing.
7. **Stop conditions:** 0 errors, all warnings judged, checklist §11.3 all yes. If a fix doesn't
   work after two tries, simplify the effect (e.g. `blurIn` instead of a custom reveal) rather
   than piling on changes.
8. **Custom 3D is optional.** If a CUSTOM effect is risky, deliver the kit version and say so.
