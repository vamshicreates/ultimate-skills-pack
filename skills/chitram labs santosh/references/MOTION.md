# MOTION — the craft of a senior motion designer, editor and sound designer, translated to code

This is the knowledge an After Effects / Cinema 4D motion designer, a Premiere / Resolve editor and
a sound designer carry in their heads, written so you can apply it in HTML/CSS/SVG/GSAP. Use it to
*design* motion (in the prompt) and to *build* it (in code). Every rule here has a reason; when you
break one, break it on purpose and say why.

Contents: 1 Mindset · 2 The 12 principles for motion graphics · 3 The graph editor in code ·
4 Timing charts (frames) · 5 Spacing, arcs, overlap · 6 Overshoot, springs, settle · 7 Motion blur ·
8 Text animation · 9 Shape layers & trim paths → SVG · 10 Mattes & masks · 11 Precomps, nulls,
parenting · 12 3D layers & the camera · 13 Light, materials, grading · 14 Effects cookbook
(AE → code) · 15 Editing craft (Premiere) · 16 Sound design & mix · 17 Colour · 18 Delivery specs ·
19 The director's review

---

## 1. Mindset

- **Motion is information.** Every move answers: what is important, where to look, what changed,
  how things relate. If a move answers none of these, delete it.
- **Hierarchy through time.** What moves first is read as most important. Sequence replaces
  position: stagger in order of importance, not in DOM order.
- **Restraint is the premium signal.** Fewer elements, longer holds, bigger type, one hero move at
  a time. Busy frames read as cheap.
- **Rhythm.** A film is music for the eyes: vary long and short, fast and slow, dense and empty.
  Monotony (every move 0.5 s, every scene 3 s) is the most common amateur tell.
- **Continuity.** Things don't pop into existence without reason; they enter from somewhere, are
  revealed by something, or grow from something that was already there.
- **Design the key poses first** (like pose-to-pose animation): the frame at rest before and after
  each move must be a good composition on its own. Motion is the path between good frames.

## 2. The 12 principles, for motion graphics

| Principle | In motion graphics | In code |
|---|---|---|
| Squash & stretch | UI elements compress on impact, stretch on speed; keep volume (scaleX × scaleY ≈ 1) | on landing: `scaleY .92 → 1, scaleX 1.06 → 1` over 0.12–0.2 s |
| Anticipation | a small move opposite to the main move before it (cards dip before lifting, text pulls back before shooting out) | 0.1–0.2 s counter-move (`y: +8`) then the main move; or `MK.curves.anticipate` |
| Staging | one clear idea per frame; the eye knows where to go | one focal element, everything else lower contrast / still |
| Pose-to-pose | keyframe the key poses, let the ease fill between | `fromTo` between two designed states; never tween from arbitrary states |
| Follow-through & overlapping action | parts of a thing arrive at different times (card, then its shadow, then its label) | stagger children 2–4 frames (0.07–0.13 s) after the parent |
| Slow in & slow out | nothing in nature starts or stops instantly | every tween eased; linear only for drifts/rotations/scrolls |
| Arcs | natural motion travels on curves | tween `x` and `y` with different eases (x `power1.out`, y `power3.out`) or animate along a path |
| Secondary action | small supporting motion that adds life (glow breathes while the card lands) | ambient finite loops (`MK.breathe/drift/hover`) on decoratives |
| Timing | the number of frames decides weight and mood | §4 tables |
| Exaggeration | push key moves slightly beyond natural so they read at speed | overshoot 3–8 %, scale punches 1.05–1.12 |
| Solid drawing → solid space | consistent light direction, perspective and depth across the film | one key light, one perspective value, consistent shadows |
| Appeal | shapes and timing that feel pleasant and intentional | clean geometry, consistent radii, eased everything, no jitter |

## 3. The graph editor in code

After Effects' **Value graph** is the position over time; the **Speed graph** is how fast. A
premium arrival is a speed graph that starts high and decays to zero with a long tail (influence
~70–90 % on the incoming keyframe). In GSAP, eases are those curves.

| AE setting | Feel | GSAP |
|---|---|---|
| Linear | mechanical, constant | `"none"` |
| Easy Ease (F9), 33 % both | gentle, generic | `MK.curves.easyEase` ≈ `"power1.inOut"` |
| Easy Ease In only (arrival), 70 % influence | confident arrival | `"power3.out"` |
| Arrival, 85–95 % influence | luxury glide, long tail | `"expo.out"` or `MK.curves.glide` (0.16, 1, 0.3, 1) |
| Snappy UI | quick, crisp | `MK.curves.snap` (0.2, 0.8, 0.2, 1) or `"power4.out"` |
| Easy Ease Out only (departure) | accelerates away | `"power2.in"` / `MK.curves.exit` |
| Camera whip (slow-fast-slow, fast middle) | energetic travel | `MK.curves.whip` (0.7, 0, 0.3, 1) or `"power4.inOut"` |
| Overshoot then settle | playful/physical | `"back.out(1.7)"` or `MK.curves.settle` |
| Anticipate + overshoot | cartoony, punchy | `MK.curves.anticipate` |

Rules:
- `.out` for entrances, `.in` for exits, `.inOut` for moves between two on-screen positions.
- Separate dimensions: for a move on an arc, give x and y different eases.
- **Don't reuse one ease everywhere** — at most two tweens with the same ease per scene.
- Custom curve from a designer: `MK.bezier(x1, y1, x2, y2)` takes the same four numbers as CSS
  `cubic-bezier()` and the AE/Figma bezier handles.
- Speed ramps / time remap: tween a proxy `{p:0}→{p:1}` with a strong ease and drive the thing
  from `onUpdate` (e.g. `el.style.transform = …p…`), or tween the element's own timeline with
  `tl.to(childTl, {progress:1, ease})`.

## 4. Timing charts (30 fps; 1 frame = 0.033 s)

| Action | Frames | Seconds |
|---|---|---|
| Micro UI (tap feedback, toggle, tick) | 4–8 | 0.13–0.27 |
| Button press + release | 6 + 8 | 0.2 + 0.27 |
| Small element in (chip, icon, label) | 10–15 | 0.33–0.5 |
| Card / panel in | 15–24 | 0.5–0.8 |
| Headline reveal (premium) | 27–36 | 0.9–1.2 |
| Headline reveal (kinetic) | 10–18 | 0.33–0.6 |
| Exit | 60–70 % of the entrance | |
| Stagger between siblings (decorative) | 2–4 | 0.07–0.13 |
| Stagger between list items with their own meaning | 12–40 | 0.4–1.3 |
| Camera move (premium) | 75–120 | 2.5–4 |
| Whip / fast transition | 10–24 | 0.33–0.8 |
| Hold before a scene leaves | ≥ reading time | 0.6 + 0.22 × words |
| End-card hold | ≥ 45 | ≥ 1.5 |

Weight through time: fast (0.15–0.3 s) = energy, urgency · medium (0.3–0.5 s) = professional ·
slow (0.5–0.8 s) = luxury, gravity · very slow (0.8–2 s) = cinematic, emotional. The slowest move
in a film should be ≥ 3× the fastest.

Don't start at 0: the first move of a film or scene begins 3–9 frames in.

## 5. Spacing, arcs, overlap

- **Spacing** (how far a thing travels each frame) is what the eye reads as the ease. Bunched
  frames at the end = soft landing. Check it in snapshots: take 5 frames across the move.
- **Arcs:** anything thrown, swung or orbiting moves on a curve. Rotation can follow direction of
  travel (`rotation` tweened with the path's tangent) for organic objects; UI stays upright.
- **Overlap (offset keyframes):** in a group, the leader moves, the rest follow 2–4 frames later;
  the last settles last. Shadows lag their objects by 1–2 frames and are softer.
- **Drag:** long or soft things (ribbons, tails, text trails) follow their head with delay and
  damping — build as N copies with increasing delay and decreasing opacity (echo).
- **Cascade vs burst:** cascades (0.06–0.1 s) read as "a list"; bursts (0–0.03 s) read as "one
  object breaking apart".

## 6. Overshoot, springs, settle

- Overshoot 3–8 % for UI, 10–20 % for playful. Never more than two visible bounces.
- `back.out(1.2)` subtle · `back.out(1.7)` standard · `back.out(2.5)` playful.
- `elastic.out(1, 0.5)` only for playful brands and small elements; never on text blocks.
- A spring-like settle for scale: `1 → 1.08 → 0.98 → 1` over 0.35 s (three keys) reads more
  natural than a single back ease on large objects.
- Physical bounce (dropping object): each bounce ~55 % the height and ~70 % the duration of the
  previous; squash on contact.

## 7. Motion blur

After Effects renders motion blur from the shutter (180° = blur of half a frame's travel). Browsers
don't, so fake it only where speed is high:
- **Directional blur** proportional to speed: during a fast x move, tween `filter: blur(Npx)` up
  and back down with the move (8–24 px), or use an SVG `feGaussianBlur stdDeviation="16 0"` for
  horizontal-only blur.
- **Streak copies**: 3–5 semi-transparent copies trailing along the path (echo) for whips.
- **Transitions** hide the speed: whips and push transitions blur the whole stage (`MK.whip`,
  `MK.transition` whipPan/zoom).
- Never blur slow moves; it just looks out of focus.

## 8. Text animation (AE text animators → code)

- **Range selectors** (per character / word / line with offset) → split into spans (`MK.words`,
  or split characters yourself) and stagger. Per-line reveals read best for headlines; per-word for
  captions; per-character only for short, large words or typing.
- **Animator properties:** position (y rise from a mask: `MK.maskRise`/`wordsRise`), opacity,
  scale (from 0.9, never from 0 for text), blur (`MK.blurIn`), tracking (letter-spacing from
  +0.3em → 0 for luxury resolves), fill colour change (highlight a word), skew for speed.
- **Wiggly selector** → per-character seeded offsets (`MK.rng(seed)`), small (±2–4 px, ±2°),
  used for playful or glitch looks only.
- **Kinetic type rules:** one idea per line; big (headline ≥ 6 % of frame height); left or centre
  aligned consistently per scene; line breaks where the meaning breaks; a highlight word in the
  accent colour, max one per line; never animate every word of a long sentence.
- **Legibility in motion:** text must be still (or nearly) while being read. Reveal → hold ≥
  reading time → exit. Rotating/scaling text is unreadable until it stops.
- **Typewriter:** 14–20 chars/s for reading speed, 30+ chars/s when the typing itself is the gag;
  caret blinks at 2 Hz after typing.
- **Karaoke / captions:** highlight lands on each word's start ±1 frame; pill moves in 0.12–0.16 s.

## 9. Shape layers & trim paths → SVG

| After Effects | Code |
|---|---|
| Trim Paths (start/end) | `stroke-dasharray = length`, tween `stroke-dashoffset` length → 0 (`MK.lineDraw`); both ends: tween dasharray too |
| Stroke with round caps | `stroke-linecap: round`, `stroke-linejoin: round` |
| Repeater | loop that clones an element N times with offset transform (rotate i × 360/N for radial) |
| Merge / offset paths | draw once; use `paint-order` or a second thicker stroke underneath for outlines |
| Path morph | interpolate two paths with the **same number of points** (tween each coordinate), or crossfade two paths with a clip reveal |
| Gooey / metaball | SVG filter: `feGaussianBlur stdDeviation=10` → `feColorMatrix` alpha `18 -7` on a group of circles; move the circles |
| Wiggle paths | tween path points with seeded offsets on a finite yoyo |
| Gradient stroke | `linearGradient` on the stroke; animate `x1/x2` for a travelling highlight |
| Dash animation (marching ants) | tween `stroke-dashoffset` linearly, finite repeats |

## 10. Mattes & masks

| AE | Code |
|---|---|
| Alpha track matte (text reveals a video/image) | `background-clip: text` with the image as background, or an SVG `<mask>` with the text |
| Luma matte / gradient wipe | `mask-image: linear-gradient(...)`; tween `mask-position` or `mask-size` |
| Linear wipe | `clip-path: inset(0 100% 0 0)` → `inset(0 0 0 0)` |
| Radial wipe / clock wipe | `mask-image: conic-gradient(#000 var(--a), transparent 0)` driven by a tweened CSS variable |
| Iris | `clip-path: circle(0% at x y)` → `circle(80% …)` (`MK.transition` iris) |
| Rectangle mask reveal behind a line | parent `overflow:hidden`, child `yPercent: 110 → 0` (`MK.maskRise`) |
| Inverted matte (cut-out) | `mask-composite: exclude` or an SVG mask with a black shape |
| Feathered edge | mask gradient with a soft ramp (0–15 % feather) |
Text behind a subject: three layers — full image, text, then a cut-out of the subject on top.

## 11. Precomps, nulls, parenting

- **Precomp** → a wrapper `div` (a "scene" or "group") you can move/scale/fade as one. Keep scene
  containers full-frame (`.layer`) with `data-in/data-out`.
- **Null object** → an empty wrapper that carries a transform for its children (rig). Chain them:
  `camera (stage) → rig (orbit) → bob (hover) → object`. Each level owns one kind of motion.
- **Parenting** → DOM nesting; a child inherits the parent's transform. Put the entrance on the
  parent and ambient motion on the child so they never fight.
- **Anchor point** → `transform-origin`. Set it where the object would pivot in reality (hinge at
  the lid's bottom, a card's centre, a needle's base).
- **Time remap / nested timing** → build a sub-timeline for a component and place it on the main
  timeline at an absolute time (`tl.add(subTl, 12.4)`); never let it run on its own clock.

## 12. 3D layers & the camera

- **Perspective = focal length.** On a 1920×1080 frame: `perspective: 1500px` ≈ wide (35 mm,
  strong depth) · `2300px` ≈ normal (50 mm) · `3500px+` ≈ tele (85 mm+, flat). Pick one per film.
- **Camera moves** (animate the rig/stage): dolly/push = scale or `z` · truck = `x` · pedestal = `y`
  · pan/tilt = `rotationY/rotationX` of the stage around the viewer · orbit = rotationY of the rig
  around the object's centre · roll = `rotationZ` (rarely; small).
- **Rack focus / DOF:** blur what's not the subject (`filter: blur`) and sharpen the subject; change
  over 0.6–1.2 s; depth order: foreground bokeh blur > background blur > subject sharp.
- **Parallax / multiplane:** 3–5 depth planes moving at different speeds during a camera move
  (near 1.5–3× far). With a true CSS 3D stage (`preserve-3d`), `z` gives parallax for free.
- **3D rules:** `transform-style: preserve-3d` on every wrapper between the stage and 3D children;
  `filter`, `overflow:hidden` and `opacity<1` on a wrapper flatten it — apply them on leaves or on
  the stage. Keep flat cards within ±25° to avoid seeing their mirrored backs.
- **Device angles that sell:** 3/4 at rotationY ±18–28°, slight top-down rotationX −5…−8°. Steeper
  shows too much keyboard; flatter loses depth.

## 13. Light, materials, grading (CSS)

- **One key light** (usually upper-left) for the whole film: gradients brighten toward it,
  highlights sit on its side, shadows fall away from it.
- **Contact + ambient shadow:** a tight dark shadow under the object plus a wide soft one
  (`box-shadow: 0 2px 6px rgba(0,0,0,.25), 0 30px 60px rgba(0,0,0,.18)`), or a radial floor
  gradient that scales/fades with the object's height (hover → shadow smaller and lighter).
- **Specular sweep:** a narrow white gradient bar (10–16 % opacity) crossing a surface in 1–1.6 s
  (`MK.gloss`). One per surface per scene, never looping constantly.
- **Rim light:** `box-shadow: inset 0 1px 0 rgba(255,255,255,.6)` on the lit edge; a thin bright
  gradient border on dark cards.
- **Glass:** layered translucent gradient + 1 px white edge + soft shadow (avoid `backdrop-filter`
  on large areas — slow and inconsistent).
- **Metal (brushed):** repeating fine linear gradients + a broad light gradient.
- **Glow:** stacked `drop-shadow`s in the accent colour or a blurred copy behind; keep it tight.
- **Grade:** a full-frame overlay with `mix-blend-mode: soft-light`/`overlay` in a warm or cool
  tint at 10–20 %, a subtle vignette (radial gradient, 15–25 % at the corners). Keep brand hex
  values untouched in the grade (apply the grade under the brand elements if needed).
- **Banding:** big dark linear gradients band under H.264 → prefer radial gradients, or add a 2 %
  static noise texture.

## 14. Effects cookbook (After Effects → code)

| AE effect | Code recipe |
|---|---|
| Glow | blurred duplicate behind (`filter: blur(20px)`, accent colour, 40–60 %) |
| CC Light Sweep | `MK.gloss` bar or `MK.sweep` over text |
| Gradient Ramp animated | CSS gradient on a large element; tween `background-position` |
| Fractal Noise / Turbulent Displace | SVG `feTurbulence` + `feDisplacementMap`; tween `baseFrequency`/`scale` attributes (deterministic) |
| Echo | N clones with increasing delay and decreasing opacity |
| Wiggle expression | seeded noise: `x = A * sin(t*f1+φ1) + A/2 * sin(t*f2+φ2)` evaluated in an `onUpdate` of a tweened proxy |
| Loop expression | finite `repeat` with `yoyo` (`MK.repeats(span, period)`) |
| Linear/Venetian/Radial wipe | clip-path / blinds / conic mask (§10, `MK.transition` blinds) |
| Card wipe / grid dissolve | a grid of tiles each holding a crop of the scene (`background-position`), staggered flip/scale |
| Shatter | tiles fly outward on arcs with rotation, burst stagger |
| Camera shake | small seeded x/y/rotation offsets decaying over 0.3–0.5 s, only for impacts |
| Chromatic aberration | two tinted copies offset ±2–6 px, `mix-blend-mode: screen` (`MK.glitchIn`) |
| Lens distortion / vignette | radial gradient overlay; no fisheye (hard in DOM) |
| Particles | only when asked; ≤ 40 deterministic elements with seeded positions, eased drift |
| Time-lapse counter | only real numbers; step a text value on a tweened proxy with `Math.round` |
| Liquid / morphing blob | SVG path morph (same point count) or gooey filter (§9) |

Unknown effect? Research it (ENGINE §R): find a CSS/SVG/Canvas implementation, then make it
deterministic (timeline-driven, seeded).

## 15. Editing craft (Premiere / Resolve thinking)

- **Walter Murch's rule of six** (what a cut must serve, in priority): emotion (51 %) > story
  (23 %) > rhythm (10 %) > eye trace (7 %) > 2D plane of screen (5 %) > 3D space of action (4 %).
  If a cut is emotionally right but spatially imperfect, keep it.
- **Cut types:** hard cut (energy, disruption) · match cut (shape/position/motion continues across
  the cut) · cut on action (cut mid-movement; the motion hides the cut) · jump cut (same framing,
  time skip — rhythm, urgency) · smash cut (sudden contrast) · J-cut (next scene's sound starts
  before its picture) · L-cut (previous sound continues under the new picture) · cross-dissolve
  (time passing, continuity) · dip to black (chapter end).
- **Shot/beat length:** premium brand 3–5 s · product demo 2–4 s · social 0.8–2 s · end card ≥ 1.5 s.
  Vary lengths; the ear and eye tire of a constant cut rate.
- **Cut on the beat** (or a steady fraction of it) for music-driven films; land big reveals on the
  downbeat, transitions start half a beat early so the swap lands on the beat.
- **Eye trace:** the next shot's focal point appears where the eye already is. Don't make the
  viewer search after a cut.
- **The 180° rule / screen direction:** keep a subject's travel direction consistent across cuts
  (left→right = forward/progress in LTR cultures).
- **Breathing room:** after a dense beat, a calmer one. The film's energy curve: calm hook →
  rising → one peak (≈ 50–65 %) → settle → still end card.
- **Kill your darlings:** if a beat doesn't serve the message, cut it, however good it looks.

## 16. Sound design & mix

- **Hit points:** every significant visual event has a sound, in sync to ±1 frame: card lift
  (shimmer), land (soft impact), whip (whoosh starting ~2 frames before the visual peak), UI
  (click), glitch (tick), reveal (riser ending exactly on the reveal frame), logo (chime).
- **Layering:** a sound = transient (click/attack) + body (tone) + tail (reverb). Big moments use
  a sub layer.
- **Music:** chord changes lead scene changes by 0.3–1 s (J-cut logic); the pulse drops out for
  whips and the end hold; the final chord resolves on the logo.
- **Mix levels:** music bed under VO ducked 6–10 dB (duck 0.5–0.6); SFX 3–6 dB below the peak of
  the music unless they are the moment; nothing clips.
- **Loudness targets:** web/social ≈ −14 LUFS integrated, true peak ≤ −1 dBTP; broadcast −23/−24
  LUFS; podcasts −16. Measure: `ffmpeg -i out.mp4 -af ebur128 -f null -`.
- **Silence** is a tool: a half-second of near-silence before the logo makes the chime land.

## 17. Colour

- **60/30/10**: background/neutrals/accent. One accent per scene; the accent marks the most
  important thing in the frame.
- **Contrast:** captions ≥ 4.5:1 against what's actually behind them; large headlines ≥ 3:1.
- **Harmony:** pick from the brand; supporting colours are tints/shades of the brand hue or its
  complement at low saturation. Tint greys toward the brand hue.
- **Temperature for mood:** warm (cream, gold) = human, premium, welcoming; cool (navy, teal) =
  trust, tech, calm; high-saturation complementary = energy, youth.
- **Light vs dark scenes:** alternate to create rhythm; a dark-to-light change is a big event —
  ease it over ≥ 0.4 s or hide it in a transition (no harsh flashes).

## 18. Delivery specs

| Platform | Canvas | Safe area | Notes |
|---|---|---|---|
| YouTube / web hero | 1920×1080 16:9 | 4–5 % margins | 30 or 60 fps |
| Instagram Reels / TikTok / Shorts | 1080×1920 9:16 | keep text out of top 12 % and bottom 20 %; keep right 12 % clear of icons | hook in the first 1 s |
| Instagram / LinkedIn feed | 1080×1080 or 1080×1350 | 5 % | captions large (in-feed viewing is small) |
| X / Twitter | 1920×1080 or 1080×1080 | 5 % | ≤ 2:20 |
| Presentation / event screen | 1920×1080 or 3840×2160 | 5 % | ambient, longer holds |
Encode: H.264 High, yuv420p, CRF 16–18, AAC 48 kHz 192–256 kbps, `+faststart`. sRGB/Rec.709.

## 19. The director's review (run on the contact sheet and the draft)

For every scene ask, and fix anything that fails:
1. Where does the eye go first? Is that the most important thing?
2. Can every line be read comfortably, and is it on screen long enough?
3. Is anything covering the thing we're showing?
4. Does every element have a reason to move, and a verb?
5. Is there one hero move, or are three things fighting?
6. Do eases and durations vary across the film? Does the slowest move feel ≥ 3× the fastest?
7. Do transitions mean something, and is the biggest one on the centrepiece?
8. Is the light consistent (one key direction), is depth consistent (one perspective)?
9. Does the sound hit every event, and does the music resolve on the logo?
10. Would this frame look at home in the reference film / at the studio we're emulating? If not,
    what's the one change that gets it there?
